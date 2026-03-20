import json

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

    with open(path, "w") as f:
        json.dump(events, f, indent=4)