from ics import Calendar, Event
from datetime import datetime


def generate_calendar(events):

    cal = Calendar()

    for e in events:

        event = Event()

        event.name = e["name"] or f'{e["game"].upper()} {e["type"]}'
        event.begin = datetime.fromisoformat(e["date"].replace("Z","+00:00"))
        event.location = f'{e["store"]} - {e["address"]}'

        cal.events.add(event)

    with open("pokemon_madrid.ics","w") as f:
        f.writelines(cal)