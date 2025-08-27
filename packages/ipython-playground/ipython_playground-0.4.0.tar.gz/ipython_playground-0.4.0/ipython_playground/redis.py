from __future__ import annotations

from typing import Dict

from .utils import log


def setup_redis() -> Dict[str, object]:
    """Create a Redis client from app configuration and expose it for IPython.

    Looks up `get_redis` from `app.configuration.redis` (from the starter template)
    and returns a dict so it can be injected into the interactive environment.
    """

    try:
        # Assumes the application provides this helper
        from app.configuration.redis import get_redis  # type: ignore
    except Exception as e:  # noqa: BLE001 - best-effort optional import
        log.debug(f"Could not import app.configuration.redis.get_redis: {e}")
        return {}

    try:
        redis_client = get_redis()
    except Exception as e:  # noqa: BLE001 - surface but don't crash playground
        log.warning(f"Failed to initialize Redis client: {e}")
        return {}

    # Keep the surface minimal and consistent with other helpers
    return {"redis_client": redis_client}
