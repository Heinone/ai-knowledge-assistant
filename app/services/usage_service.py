from collections import deque
from datetime import datetime, timezone
from typing import Any

MAX_USAGE_EVENTS = 50

_usage_events = deque(maxlen=MAX_USAGE_EVENTS)


def record_usage(event: dict[str, Any]) -> None:
    event_with_time = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **event,
    }

    _usage_events.appendleft(event_with_time)


def get_recent_usage() -> list[dict[str, Any]]:
    return list(_usage_events)