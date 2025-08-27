#!/usr/bin/env python
"""
ShipBoss MCP Server – v4.0.12
• Uses official FastMCP SDK (≥1.2.0)
• Inline schemas handled by SDK; no manual JSON-RPC plumbing
• Parcel + freight endpoints
• Fixed logging configuration to use stderr
• Fixed dotenv dependency conflicts
"""

from __future__ import annotations
import os, asyncio, time, logging, typing as t, sys, argparse, re, difflib
import httpx
from pydantic import BaseModel, Field
from typing import Literal
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP          # <-- only FastMCP

# ───────── config ─────────
def get_api_token():
    """Get API token from command-line arguments, environment variables, or .env file"""
    # Load .env file from the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_file = os.path.join(script_dir, '.env')
    if os.path.exists(env_file):
        load_dotenv(env_file)

    parser = argparse.ArgumentParser(description='ShipBoss MCP Server')
    parser.add_argument('--api-token', type=str, help='ShipBoss API token (or set SHIPBOSS_API_TOKEN env var)')
    args, unknown = parser.parse_known_args()

    # Check command-line argument first, then environment variable
    api_token = args.api_token or os.getenv("SHIPBOSS_API_TOKEN")

    if not api_token:
        raise RuntimeError(
            "API token required. Either:\n"
            "  1. Create a .env file with SHIPBOSS_API_TOKEN=your_token\n"
            "  2. Set SHIPBOSS_API_TOKEN environment variable, or\n"
            "  3. Pass --api-token argument"
        )

    # Debug: Print source of token (remove this in production)
    source = "command-line argument" if args.api_token else "environment/.env file"
    print(f"DEBUG: API token loaded from {source}", file=sys.stderr)

    return api_token

API_TOKEN = get_api_token()

BASE_URL  = "https://ship.shipboss.io/api/public/v1"
TIMEOUT   = 20
MAX_RETRY = 3

# Configure logging to stderr explicitly to avoid interfering with stdio JSON-RPC
def setup_logging():
    """Setup logging configuration for MCP server"""
    # Clear any existing handlers to ensure clean slate
    logging.getLogger().handlers.clear()
    
    # Configure logging with explicit stderr output
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        stream=sys.stderr,  # Explicitly use stderr to avoid stdout interference
        force=True  # Override any existing configuration
    )
    
    # Ensure no handlers are writing to stdout
    for handler in logging.root.handlers:
        if hasattr(handler, 'stream') and handler.stream == sys.stdout:
            handler.stream = sys.stderr

mcp = FastMCP("shipboss")        # instance used for @mcp.tool()

# ───────── helper ─────────
async def post(endpoint: str, body: dict) -> dict:
    url = f"{BASE_URL}/{endpoint}"
    headers = {"Authorization": f"Bearer {API_TOKEN}",
               "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        for attempt in range(1, MAX_RETRY + 1):
            resp = await client.post(url, json=body, headers=headers)
            if resp.status_code == 429:
                await asyncio.sleep(int(resp.headers.get("Retry-After", "1")) or 1)
                continue
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") == "success":
                return data["data"]
            raise RuntimeError(data.get("message", "ShipBoss API error"))
        raise RuntimeError("Exhausted retries")

async def _collect_service_suggestions(
    *,
    from_addr: dict,
    to_addr: dict,
    packages: list[dict],
    ship_date: str,
    package_type: str | None,
    requested_carrier: str | None,
    requested_service_name: str | None,
) -> dict:
    """Call get-rates and aggregate valid services per carrier to build
    suggestions for error enrichment. Returns a dict with keys:
      - by_carrier: {carrier: [service_name, ...]}
      - closest_matches: [service_name, ...]  # for the requested carrier if any
    """
    # Build get-rates payload
    rates_payload: dict[str, t.Any] = {
        "addresses": {"from": from_addr, "to": to_addr},
        "packages": packages,
        "ship_date": ship_date,
    }
    if package_type:
        rates_payload["package_type"] = package_type

    try:
        rates_data = await post("get-rates", rates_payload)
    except Exception:
        # If get-rates fails, return empty suggestions to avoid masking the root error
        return {"by_carrier": {}, "closest_matches": []}

    by_carrier: dict[str, list[str]] = {}
    seen: dict[str, set[str]] = {}
    for rate in rates_data.get("rates", []) or []:
        carrier_name = rate.get("carrier_name") or rate.get("carrier") or ""
        service_name = rate.get("service_name") or ""
        if not carrier_name or not service_name:
            continue
        if carrier_name not in by_carrier:
            by_carrier[carrier_name] = []
            seen[carrier_name] = set()
        if service_name not in seen[carrier_name]:
            seen[carrier_name].add(service_name)
            by_carrier[carrier_name].append(service_name)

    # Compute closest matches for the requested service name within the requested carrier
    closest: list[str] = []
    if requested_carrier and requested_service_name:
        pool = by_carrier.get(requested_carrier) or []
        closest = difflib.get_close_matches(requested_service_name, pool, n=5, cutoff=0.5)

    return {"by_carrier": by_carrier, "closest_matches": closest}

# ───────── helper functions ─────────
def parse_address(address_string: str) -> dict:
    """Parse an address string into components with optional address_2 support.
    Accepted common formats (commas or newlines as separators):
      - 'Street, City, State ZIP, Country'
      - 'Street, City, State, ZIP, Country'
      - 'Street, Address 2, City, State, ZIP, Country' (any number of address lines)

    Country code is REQUIRED (e.g., US, CA, IL).
    """
    # Split on commas or newlines, drop empty chunks
    raw_parts = re.split(r"[,\n]", address_string)
    parts = [p.strip() for p in raw_parts if p and p.strip()]

    if len(parts) < 4:
        raise ValueError(
            "Address must include country code: 'Street, City, State ZIP, Country'"
        )

    country = parts[-1].strip().upper()

    # Decide between 'State ZIP' combined vs separate 'State','ZIP'
    if len(parts) == 4:
        # 'Street, City, State ZIP, Country' OR 'Street, City, ZIP, Country'
        state_zip_tokens = parts[-2].split()
        token = state_zip_tokens[0] if state_zip_tokens else ""
        city = parts[-3]
        address_lines = parts[:-3]  # everything before city

        # Heuristics: if token looks like a postal code (mostly digits), treat as ZIP.
        looks_like_zip = bool(re.fullmatch(r"[A-Za-z0-9\- ]{3,}", token)) and not bool(re.fullmatch(r"[A-Za-z]{2}", token))
        if looks_like_zip:
            state = ""
            zip_code = token
        else:
            state = token
            zip_code = state_zip_tokens[1] if len(state_zip_tokens) > 1 else ""
    else:
        # Expect separate state and zip at the end: ..., City, State, ZIP, Country
        if len(parts) < 5:
            raise ValueError("Invalid address format")
        state = parts[-3]
        zip_code = parts[-2]
        city = parts[-4]
        address_lines = parts[:-4]  # Street and optional address_2..n

    # Only require state for countries that mandate it commonly (US/CA/MX)
    if not state and country in ("US", "CA", "MX"):
        raise ValueError("State/Province is required for US/CA/MX addresses")
    if not country:
        raise ValueError("Country code is required (e.g., 'US', 'CA', 'MX')")

    # Normalize address lines
    address_1 = address_lines[0] if address_lines else ""
    address_2 = ", ".join(address_lines[1:]) if len(address_lines) > 1 else None

    result = {
        "address_1": address_1,
        "city": city,
        "state": state,
        "zip": zip_code,
        "country": country
    }
    if address_2:
        result["address_2"] = address_2
    return result

def _normalize_address_dict(addr: dict) -> dict:
    """Normalize common address dict key variants to ShipBoss fields.
    Keeps unknown fields as-is.
    """
    if not isinstance(addr, dict):
        raise ValueError("Address must be a string or object")

    mapping = {
        "addr1": "address_1",
        "addr2": "address_2",
        "postal_code": "zip",
        "postcode": "zip",
        "province": "state",
        "region": "state",
        "country_code": "country",
    }

    normalized = dict(addr)
    for src, dst in mapping.items():
        if src in normalized and dst not in normalized:
            normalized[dst] = normalized[src]
    return normalized

def coerce_address(address: t.Union[str, dict]) -> dict:
    """Accept either a free-form string or a structured dict.
    - If string → parse into components (with address_2 support)
    - If dict → normalize key variants and return as-is
    """
    if isinstance(address, str):
        return parse_address(address)
    if isinstance(address, dict):
        return _normalize_address_dict(address)
    raise ValueError("Address must be a string or object")

def auto_detect_package_type(weight: float, length: float | None, width: float | None, height: float | None) -> str:
    """Auto-detect best package type based on dimensions and weight"""
    length = length or 0
    width = width or 0
    height = height or 0
    max_dim = max(length, width, height)
    
    if weight <= 0.5 and max_dim <= 12:
        return "ENVELOPE"
    elif weight <= 1 and max_dim <= 15:
        return "PAK"
    elif max_dim <= 8:
        return "BOX_SM"
    elif max_dim <= 12:
        return "BOX_MD"
    elif max_dim <= 18:
        return "BOX_LG"
    elif max_dim <= 24:
        return "BOX_XL"
    else:
        return "CUSTOMER_PACKAGING"

# ───────── service name helpers ─────────
def _normalize_service_name(carrier: str, svc: str) -> str:
    """Translate common shorthand service aliases into the exact names expected
    by the ShipBoss API so that end-users can pass convenient values like
    "GROUND" instead of "UPS Ground".
    """
    lookup = {
        "UPS": {
            "GROUND": "UPS Ground",
            "EXPRESS": "UPS Worldwide Express",
            "2DAY": "UPS Second Day Air",
            "NEXT_DAY": "UPS Next Day Air"
        },
        "FedEx": {
            "GROUND": "FedEx Ground",
            "HOME_DELIVERY": "FedEx Home Delivery",
            "2DAY": "FedEx 2Day",
            "OVERNIGHT": "FedEx Priority Overnight"
        },
        "DHL": {
            "EXPRESS_WORLDWIDE": "Express Worldwide"
        }
    }

    # Exact match first (case sensitive). If already correct, just return.
    if carrier in lookup and svc in lookup[carrier].values():
        return svc

    # Upper-case key for mapping, strip spaces/underscores for robustness
    key = svc.upper().replace(" ", "_")
    resolved = lookup.get(carrier, {}).get(key, svc)  # fall back to original

    # Heuristic: for FedEx/UPS, if caller passed 'International Priority' without
    # carrier prefix, prepend the carrier brand. Avoid doing this for DHL where
    # official names commonly omit the brand (e.g., 'Express Worldwide').
    if carrier in ("FedEx", "UPS"):
        if not resolved.lower().startswith(carrier.lower() + " "):
            # If the user already passed the exact official name, keep it.
            # Otherwise, try prefixing the carrier for better matching server-side.
            if carrier not in resolved:
                return f"{carrier} {resolved}"
    return resolved

# ───────── tools ─────────
@mcp.tool()
async def ping() -> dict:
    """Health-check: returns {'ok': true}"""
    return {"ok": True}

@mcp.tool()
async def get_parcel_rates(
    origin: t.Union[str, dict], 
    destination: t.Union[str, dict], 
    weight_pounds: float, 
    ship_date: str,
    dimensions_inches: list[float] | None = None,
    package_type: str | None = None,
    **extra_data
) -> dict:
    """Get parcel shipping rates.
    
    Args:
        origin: Origin address as string (e.g. "123 Main St, New York, NY 10001, US")
        destination: Destination address as string (e.g. "456 Oak Ave, Los Angeles, CA 90210, US") 
        weight_pounds: Package weight in pounds
        ship_date: Ship date in YYYY-MM-DD format
        dimensions_inches: Optional [length, width, height] in inches
        package_type: Optional package type (ENVELOPE, BOX_SM, BOX_MD, BOX_LG, BOX_XL, PAK, CUSTOMER_PACKAGING)
    """
    # Parse addresses
    from_addr = coerce_address(origin)
    to_addr = coerce_address(destination)

    # Backward-compatibility: allow a single JSON string via 'extra_data'
    if isinstance(extra_data.get("extra_data"), str):
        try:
            import json
            parsed_extra = json.loads(extra_data.pop("extra_data"))
            extra_data.update(parsed_extra)
        except Exception:
            pass

    # Enrich addresses with from_/to_* extras (e.g., address_2, name, phone)
    from_extras: dict[str, t.Any] = {}
    to_extras: dict[str, t.Any] = {}
    for key, value in list(extra_data.items()):
        if key.startswith("from_"):
            attr = key[len("from_"):]
            from_extras[attr] = value
            extra_data.pop(key)
        elif key.startswith("to_"):
            attr = key[len("to_"):]
            to_extras[attr] = value
            extra_data.pop(key)
    if from_extras:
        from_addr.update(from_extras)
    if to_extras:
        to_addr.update(to_extras)
    
    # Build package data
    package = {"weight": weight_pounds, "quantity": 1}
    if dimensions_inches:
        if len(dimensions_inches) >= 3:
            package["length"] = dimensions_inches[0]
            package["width"] = dimensions_inches[1] 
            package["height"] = dimensions_inches[2]
    
    # Build request data
    data = {
        "addresses": {"from": from_addr, "to": to_addr},
        "packages": [package],
        "ship_date": ship_date
    }
    
    # Auto-detect or use provided package type
    if package_type:
        data["package_type"] = package_type
    else:
        length = dimensions_inches[0] if dimensions_inches and len(dimensions_inches) > 0 else None
        width = dimensions_inches[1] if dimensions_inches and len(dimensions_inches) > 1 else None
        height = dimensions_inches[2] if dimensions_inches and len(dimensions_inches) > 2 else None
        data["package_type"] = auto_detect_package_type(weight_pounds, length, width, height)
    
    # Merge any remaining extras at the shipment level (e.g., options)
    if extra_data:
        data.update(extra_data)

    return await post("get-rates", data)

@mcp.tool()
async def create_parcel_label(
    origin: t.Union[str, dict],
    destination: t.Union[str, dict], 
    weight_pounds: float,
    ship_date: str,
    carrier: Literal["FedEx", "UPS", "DHL"],
    service_name: str,
    dimensions_inches: list[float] | None = None,
    package_type: str | None = None,
    label_type: str = "PDF",
    label_output: Literal["link", "base64", "both"] = "link",
    **extra_data
) -> dict:
    """Create parcel shipping label.

    Args:
        origin: Origin address as string (e.g. "123 Main St, New York, NY 10001, US")
        destination: Destination address as string (e.g. "456 Oak Ave, Los Angeles, CA 90210, US")
        weight_pounds: Package weight in pounds
        ship_date: Ship date in YYYY-MM-DD format
        carrier: Shipping carrier (FedEx, UPS, or DHL)
        service_name: Service level (e.g. "GROUND", "EXPRESS", "2DAY")
        dimensions_inches: Optional [length, width, height] in inches
        package_type: Optional package type (ENVELOPE, BOX_SM, BOX_MD, BOX_LG, BOX_XL, PAK, CUSTOMER_PACKAGING)
        label_type: Label format (PDF, FOUR_BY_SIX, FOUR_BY_SIX_DOC_TAB)
        from_* / to_* keyword args: Use prefixes ``from_`` and ``to_`` to provide
            contact fields that belong to the sender or recipient address,
            e.g. ``from_name``, ``from_phone``, ``to_contact_name``, ``to_email``.
            These will automatically be merged into the corresponding address
            objects before the request is sent to ShipBoss.

    Returns:
        dict: Contains package tracking information and label data. The response includes:
        - packages: Array with tracking numbers and base64-encoded labels
        - label_info: Contains the download URL for the label

        IMPORTANT: Display the label_info.link URL to the user so they can download their shipping label.
        The URL in label_info.link is the direct link to the generated shipping label PDF.
    """
    # Parse addresses
    from_addr = coerce_address(origin)
    to_addr = coerce_address(destination)
    
    # Build package data
    package = {"weight": weight_pounds, "quantity": 1}
    if dimensions_inches:
        if len(dimensions_inches) >= 3:
            package["length"] = dimensions_inches[0]
            package["width"] = dimensions_inches[1]
            package["height"] = dimensions_inches[2]
    
    # Build request data
    data = {
        "addresses": {"from": from_addr, "to": to_addr},
        "packages": [package],
        "ship_date": ship_date,
        "carrier": carrier,
        # Translate common shorthand service markers (e.g., "GROUND") to the
        # exact service names expected by ShipBoss.
        "service_name": _normalize_service_name(carrier, service_name),
        "label_type": label_type,
    }

    # Backward-compatibility: if caller passed a single JSON string via parameter
    # named ``extra_data`` (common misunderstanding), parse it so that its keys
    # participate in the enrichment/merge logic below.
    if isinstance(extra_data.get("extra_data"), str):
        try:
            import json
            parsed_extra = json.loads(extra_data.pop("extra_data"))
            extra_data.update(parsed_extra)
        except Exception:
            # Ignore parsing errors – let raw string go through as was before
            pass

    # ── enrich addresses with contact details supplied via **extra_data ──
    # Accept keyword arguments prefixed with ``from_`` or ``to_`` to populate
    # the corresponding address dictionaries. Example:
    # create_parcel_label(..., from_name="Sarah", from_phone="2125550123", to_name="John", to_phone="3105550456")
    from_extras: dict[str, t.Any] = {}
    to_extras: dict[str, t.Any] = {}

    # Collect and strip the prefix so that e.g. ``from_name`` -> {"name": ...}
    for key, value in list(extra_data.items()):  # list() so we can mutate extra_data
        if key.startswith("from_"):
            attr = key[len("from_"):]
            from_extras[attr] = value
            extra_data.pop(key)
        elif key.startswith("to_"):
            attr = key[len("to_"):]
            to_extras[attr] = value
            extra_data.pop(key)

    # Merge into parsed address dicts
    from_addr.update(from_extras)
    to_addr.update(to_extras)

    # ShipBoss create-label endpoint requires at minimum a phone number and either
    # ``name`` or ``contact_name`` on both sender & recipient records. To reduce
    # friction during early testing, provide sensible defaults if the caller did
    # not supply them. These defaults should be overridden in production usage.
    def ensure_minimum_fields(addr: dict, role: str) -> None:
        if not (addr.get("name") or addr.get("contact_name")):
            addr["name"] = f"{role.title()} Name"
        if not addr.get("phone"):
            addr["phone"] = "0000000000"

    ensure_minimum_fields(from_addr, "sender")
    ensure_minimum_fields(to_addr, "recipient")

    # Auto-detect or use provided package type
    if package_type:
        data["package_type"] = package_type
    else:
        length = dimensions_inches[0] if dimensions_inches and len(dimensions_inches) > 0 else None
        width = dimensions_inches[1] if dimensions_inches and len(dimensions_inches) > 1 else None
        height = dimensions_inches[2] if dimensions_inches and len(dimensions_inches) > 2 else None
        data["package_type"] = auto_detect_package_type(weight_pounds, length, width, height)

    # Merge extra data
    data.update(extra_data)

    try:
        raw = await post("create-label", data)

        # Backend always returns base64 in packages and may include label_info.link.
        # Shape the response according to label_output preference without requesting special backend behavior.
        output = dict(raw) if isinstance(raw, dict) else {"data": raw}

        packages = output.get("packages") or []
        label_info = output.get("label_info") or {}

        # Normalize shape when caller wants only link or only base64
        if label_output == "link":
            # Remove heavy base64 labels to reduce payload size
            slim_packages: list[dict] = []
            for pkg in packages:
                if isinstance(pkg, dict):
                    slim_pkg = {k: v for k, v in pkg.items() if k != "label"}
                    slim_packages.append(slim_pkg)
                else:
                    slim_packages.append(pkg)
            output["packages"] = slim_packages
            # Ensure label_info remains if provided by backend
            if label_info:
                output["label_info"] = label_info
        elif label_output == "base64":
            # Keep base64 labels, drop link info if present
            if "label_info" in output:
                output.pop("label_info", None)
        else:  # both
            # Ensure both are present when available; do not mutate base64
            # Nothing to remove; keep as-is
            pass

        return output
    except RuntimeError as e:
        message = str(e)
        # Enrich known invalid service name errors with suggestions
        if "service name is invalid" in message.lower() or "no valid services" in message.lower():
            suggestions = await _collect_service_suggestions(
                from_addr=from_addr,
                to_addr=to_addr,
                packages=[package],
                ship_date=ship_date,
                package_type=data.get("package_type"),
                requested_carrier=carrier,
                requested_service_name=service_name,
            )
            enriched = {
                "error": message,
                "hint": "The selected service name appears invalid. Here are available services.",
                "carrier": carrier,
                "requested_service_name": service_name,
                "available_services_by_carrier": suggestions.get("by_carrier", {}),
                "closest_matches_for_requested": suggestions.get("closest_matches", []),
            }
            raise RuntimeError(str(enriched))
        raise

@mcp.tool()
async def track_parcel(carrier: Literal["FedEx", "UPS", "DHL"], tracking_number: str) -> dict:
    """Track parcel shipment.
    
    Args:
        carrier: Shipping carrier (FedEx, UPS, or DHL)
        tracking_number: Package tracking number
    """
    data = {
        "carrier": carrier,
        "tracking_number": tracking_number
    }
    return await post("track", data)

# ───────── additional parcel tools ─────────
@mcp.tool()
async def create_pickup(
    origin: t.Union[str, dict],
    pickup_date: str,
    ready_time: str,
    close_time: str,
    carrier: Literal["FedEx", "UPS", "DHL"],
    quantity: int,
    total_weight: float,
    pickup_service_name: str | None = None,
    package_type: str | None = None,
    pickup_destination_country: str | None = None,
    test: bool | None = None,
    **extra_data
) -> dict:
    """Create a pickup to a given location.

    Args:
        origin: Pickup address as string (e.g. "123 Main St, New York, NY 10001, US")
        pickup_date: YYYY-MM-DD pickup date
        ready_time: HH:MM time the packages are ready
        close_time: HH:MM latest pickup time
        carrier: Carrier performing pickup (FedEx, UPS, DHL)
        quantity: Number of packages
        total_weight: Total weight in pounds
        pickup_service_name: Optional service name (required for UPS/FedEx)
        package_type: Optional package type (UPS only – Package or Letter)
        pickup_destination_country: Optional destination country code (UPS only)
        test: When true, use ShipBoss sandbox environment
    """
    data: dict[str, t.Any] = {
        "address": coerce_address(origin),
        "pickup_date": pickup_date,
        "ready_time": ready_time,
        "close_time": close_time,
        "carrier": carrier,
        "quantity": quantity,
        "total_weight": total_weight,
    }

    # Optional fields
    if pickup_service_name:
        data["pickup_service_name"] = pickup_service_name
    if package_type:
        data["package_type"] = package_type
    if pickup_destination_country:
        data["pickup_destination_country"] = pickup_destination_country
    if test is not None:
        data["test"] = test

    # Merge extra data
    data.update(extra_data)

    return await post("create-pickup", data)


@mcp.tool()
async def cancel_pickup(
    carrier: Literal["FedEx", "UPS", "DHL"],
    confirmation_number: str,
    test: bool | None = None
) -> dict:
    """Cancel an existing pickup.

    Args:
        carrier: Carrier that was scheduled (FedEx, UPS, DHL)
        confirmation_number: Confirmation / pickup ID to cancel
        test: When true, use ShipBoss sandbox environment
    """
    data: dict[str, t.Any] = {
        "carrier": carrier,
        "confirmation_number": confirmation_number,
    }
    if test is not None:
        data["test"] = test

    return await post("cancel-pickup", data)

# ───────── freight tools ─────────
@mcp.tool()
async def get_freight_rates(
    origin: t.Union[str, dict],
    destination: t.Union[str, dict],
    weight_pounds: float,
    length_inches: float,
    width_inches: float,
    height_inches: float,
    quantity: int,
    commodity: str,
    freight_class: float,
    package_type: Literal["PLT", "CTN", "CRT", "DRM", "CON", "BDL", "CYL", "OTH"] = "PLT",
    ship_date: str | None = None,
    test: bool | None = None
) -> dict:
    """Get freight shipping rates.

    Args:
        origin: Origin address as string (domestic – e.g. "3500 Sunset Ave, Ocean, NJ, 07712, US")
        destination: Destination address as string (domestic)
        weight_pounds: Weight of a single freight piece
        length_inches: Length in inches
        width_inches: Width in inches
        height_inches: Height in inches
        quantity: Number of identical freight pieces
        commodity: Description of the goods
        freight_class: NMFC freight class (e.g. 60, 85, 125)
        package_type: Freight package type (default PLT)
        ship_date: Optional pickup date in YYYY-MM-DD format
        test: When true, use ShipBoss sandbox environment

    Returns:
        dict: Contains available freight rates with quote IDs.

        IMPORTANT: After getting freight rates, users should log into their ShipBoss account
        at https://app.shipboss.io to create the actual shipment using the quote ID from the response.
        Freight label creation is not available through this API and must be done through the ShipBoss web interface.
    """
    from_addr = coerce_address(origin)
    to_addr = coerce_address(destination)

    package: dict[str, t.Any] = {
        "weight": weight_pounds,
        "length": length_inches,
        "width": width_inches,
        "height": height_inches,
        "quantity": quantity,
        "commodity": commodity,
        "freight_class": freight_class,
    }

    data: dict[str, t.Any] = {
        "addresses": {"from": from_addr, "to": to_addr},
        "packages": [package],
        "package_type": package_type,
    }
    if ship_date:
        data["pickup"] = {"date": ship_date}
    if test is not None:
        data["test"] = test

    return await post("get-freight-rates", data)





@mcp.tool()
async def track_freight(tracking_number: str, test: bool | None = None) -> dict:
    """Track a freight shipment by tracking number.

    Args:
        tracking_number: Freight tracking number
        test: When true, use ShipBoss sandbox environment
    """
    data: dict[str, t.Any] = {"tracking_number": tracking_number}
    if test is not None:
        data["test"] = test

    return await post("track-freight", data)

# ───────── main ─────────
def main() -> None:
    """Entry point for the shipboss-mcp-server console script."""
    setup_logging()  # Configure logging to stderr
    
    # Ensure stdout/stderr are properly flushed before starting JSON-RPC
    # Important: If you're getting "Unexpected token" JSON parse errors in Claude Desktop,
    # it's likely because your MCP configuration is running "pip install" on startup.
    # 
    # SOLUTION:
    # 1. Create a virtual environment: python -m venv shipboss_env
    # 2. Activate it: shipboss_env\Scripts\activate (Windows) or source shipboss_env/bin/activate (macOS/Linux)
    # 3. Install the package: pip install shipboss-mcp-server
    # 4. Update your Claude Desktop config to point to the full path:
    #    Windows: "C:\\path\\to\\shipboss_env\\Scripts\\shipboss-mcp-server.exe"
    #    macOS/Linux: "/path/to/shipboss_env/bin/shipboss-mcp-server"
    #
    # See README.md for detailed setup instructions.
    sys.stdout.flush()
    sys.stderr.flush()
    
    # Ensure we're in a clean state for JSON-RPC communication
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout.buffer.flush()
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr.buffer.flush()
    
    mcp.run(transport="stdio")     # SDK handles JSON-RPC/stdio

if __name__ == "__main__":
    main()
