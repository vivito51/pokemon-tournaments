import json
from pathlib import Path

from app.core.settings import get_settings

VALID_GAMES = {"tcg", "vg"}

def load_events(path="events.json"):
    with open(path) as f:
        return json.load(f)


def _normalized_games(event):
    if isinstance(event.get("games"), list) and event["games"]:
        return [str(game).lower() for game in event["games"] if game]

    if event.get("game"):
        return [str(event["game"]).lower()]

    return []


def _expand_event_games(event):
    games = [game for game in _normalized_games(event) if game != "pgo"]

    if not games:
        return []

    event_type = event.get("type", "")
    unique_games = list(dict.fromkeys(games))
    valid_games = [game for game in unique_games if game in VALID_GAMES]

    if not valid_games:
        return []

    if len(valid_games) == 1:
        normalized_event = event.copy()
        normalized_event["game"] = valid_games[0]
        normalized_event.pop("games", None)
        return [normalized_event]

    if event_type == "League":
        chosen_game = "tcg" if "tcg" in valid_games else valid_games[0]
        normalized_event = event.copy()
        normalized_event["game"] = chosen_game
        normalized_event.pop("games", None)
        return [normalized_event]

    expanded = []
    for game in valid_games:
        normalized_event = event.copy()
        normalized_event["game"] = game
        normalized_event.pop("games", None)
        expanded.append(normalized_event)

    return expanded


def deduplicate_events(events):
    seen = set()
    cleaned = []

    for e in events:
        expanded_events = _expand_event_games(e)

        for normalized_event in expanded_events:
            key = (
                normalized_event["store"],
                normalized_event["date"],
                normalized_event["game"],
                normalized_event["type"]
            )

            if key in seen:
                continue

            seen.add(key)
            cleaned.append(normalized_event)

    return cleaned


def save_events(events, path="events_clean.json"):
    target_path = (
        get_settings().clean_events_path if path == "events_clean.json" else Path(path)
    )
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "w") as f:
        json.dump(events, f, indent=4)
