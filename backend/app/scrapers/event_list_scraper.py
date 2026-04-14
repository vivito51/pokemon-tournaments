import logging

from app.scrapers.search_setup import enable_event_list_view

logger = logging.getLogger(__name__)


def _pick_first(mapping, *keys, default=""):
    for key in keys:
        value = mapping.get(key)
        if value not in (None, ""):
            return value
    return default


def _extract_products(entry):
    event_payload = entry.get("Events") if isinstance(entry.get("Events"), dict) else {}
    candidates = [
        entry.get("Products"),
        entry.get("Product"),
        event_payload.get("Products"),
    ]

    for candidate in candidates:
        if isinstance(candidate, list) and candidate:
            return [str(item).lower() for item in candidate if item]
        if isinstance(candidate, dict):
            listing = candidate.get("List")
            if isinstance(listing, list) and listing:
                return [str(item).lower() for item in listing if item]
            name = candidate.get("Name")
            if name:
                return [str(name).lower()]

    return []


def _extract_address(entry):
    event_payload = entry.get("Events") if isinstance(entry.get("Events"), dict) else {}
    candidates = [
        entry.get("Address"),
        entry.get("StoreAddress"),
        event_payload.get("Address"),
    ]

    for candidate in candidates:
        if isinstance(candidate, dict):
            full_address = candidate.get("Full_address") or candidate.get("FullAddress")
            if full_address:
                return str(full_address)

    return ""


def _extract_store_name(entry):
    event_payload = entry.get("Events") if isinstance(entry.get("Events"), dict) else {}
    candidates = [
        entry.get("StoreName"),
        entry.get("LocationName"),
        entry.get("OrganizerName"),
        event_payload.get("Address", {}).get("Name")
        if isinstance(event_payload.get("Address"), dict)
        else None,
        event_payload.get("ActivityGroup", {}).get("Display_name")
        if isinstance(event_payload.get("ActivityGroup"), dict)
        else None,
        entry.get("Store", {}).get("Name") if isinstance(entry.get("Store"), dict) else None,
    ]

    for candidate in candidates:
        if candidate:
            return str(candidate)

    return "Unknown Store"


def normalize_event_list_response(data):
    event_list = data.get("data", {}).get("EventList", {}).get("List", [])

    normalized = []

    for entry in event_list:
        event_payload = entry.get("Events") if isinstance(entry.get("Events"), dict) else entry
        if not isinstance(event_payload, dict):
            continue

        store_name = _extract_store_name(entry)
        event_type = _pick_first(entry, "EventTypeName", "EventType", default="Unknown")
        event_name = _pick_first(event_payload, "Name", "EventName", default="")

        if not event_name:
            event_name = f"{event_type} - {store_name}"

        games = _extract_products(entry)

        normalized.append(
            {
                "name": event_name,
                "date": _pick_first(event_payload, "Start_date", "StartDate", default=""),
                "game": games[0] if games else "unknown",
                "games": games,
                "type": event_type,
                "store": store_name,
                "address": _extract_address(entry),
            }
        )

    return normalized


def get_events_from_event_list(page):
    logger.info("Loading event list view and waiting for DataActionGetEventList")

    with page.expect_response(
        lambda r: (
            "DataActionGetEventList" in r.url
            and r.status == 200
            and "json" in r.headers.get("content-type", "").lower()
        ),
        timeout=30000,
    ) as response_info:
        enable_event_list_view(page)

    response = response_info.value
    data = response.json()
    normalized_events = normalize_event_list_response(data)

    logger.info(
        "Event list response received: %s raw events, %s normalized events",
        len(data.get("data", {}).get("EventList", {}).get("List", [])),
        len(normalized_events),
    )

    return normalized_events
