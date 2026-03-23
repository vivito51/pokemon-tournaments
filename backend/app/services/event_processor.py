import json
from pathlib import Path

from app.core.settings import get_settings

def load_events(path="events.json"):
    with open(path) as f:
        return json.load(f)


def deduplicate_events(events):

    seen = set()
    cleaned = []

    for e in events:

        key = (
            e["store"],
            e["date"],
            e["game"],
            e["type"]
        )

        if key in seen:
            continue

        seen.add(key)
        cleaned.append(e)

    return cleaned


def save_events(events, path="events_clean.json"):
    target_path = (
        get_settings().clean_events_path if path == "events_clean.json" else Path(path)
    )
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "w") as f:
        json.dump(events, f, indent=4)
