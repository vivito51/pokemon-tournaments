import json
from datetime import datetime, timezone

from app.core.settings import get_settings


def export_events_for_frontend(events):
    settings = get_settings()
    settings.frontend_events_path.parent.mkdir(parents=True, exist_ok=True)

    with open(settings.frontend_events_path, "w") as f:
        json.dump(
            {
                "updatedAt": datetime.now(timezone.utc).isoformat(),
                "events": events,
            },
            f,
            indent=4,
        )
