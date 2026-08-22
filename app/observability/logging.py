import json
import logging
from datetime import (
    datetime,
    timezone,
)
from typing import Any

from app.observability.context import (
    get_request_id,
)


class JsonFormatter(logging.Formatter):
    def format(
        self,
        record: logging.LogRecord,
    ) -> str:

        payload: dict[str, Any] = {
            "timestamp": (
                datetime.now(timezone.utc)
                .isoformat()
            ),
            "level": record.levelname,
            "logger": record.name,
            "message": (
                record.getMessage()
            ),
            "request_id": (
                get_request_id()
            ),
        }

        event_data = getattr(
            record,
            "event_data",
            None,
        )

        if isinstance(
            event_data,
            dict,
        ):
            payload.update(
                event_data
            )

        if record.exc_info:
            payload["exception"] = (
                self.formatException(
                    record.exc_info
                )
            )

        return json.dumps(
            payload,
            default=str,
            separators=(",", ":"),
        )


def configure_logging() -> None:
    handler = logging.StreamHandler()

    handler.setFormatter(
        JsonFormatter()
    )

    root = logging.getLogger()

    root.handlers.clear()
    root.addHandler(handler)

    root.setLevel(
        logging.INFO
    )