from ics import Calendar, Event
from datetime import datetime

from app.core.settings import get_settings


def generate_calendar(events):
    settings = get_settings()
    settings.calendar_path.parent.mkdir(parents=True, exist_ok=True)

    cal = Calendar()

    for e in events:

        event = Event()

        event.name = e["name"] or f'{e["game"].upper()} {e["type"]}'
        event.begin = datetime.fromisoformat(e["date"].replace("Z","+00:00"))
        event.location = f'{e["store"]} - {e["address"]}'

        cal.events.add(event)

    with open(settings.calendar_path, "w") as f:
        f.writelines(cal)
