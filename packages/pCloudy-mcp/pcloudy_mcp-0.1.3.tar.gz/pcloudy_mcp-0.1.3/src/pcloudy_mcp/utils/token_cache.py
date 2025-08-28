import logging
import os

from diskcache import Cache

from ..Constant.constant import Constant

logger = logging.getLogger(__name__)
constant = Constant()

# Define base path: <root>/.cache/pcloudy_tokens
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
CACHE_DIR = os.path.join(BASE_DIR, ".cache", constant.TOKEN_CACHE_NAMESPACE)

# TTL for token cache (5 days in seconds)
TOKEN_TTL_SECONDS = constant.TOKEN_CACHE_TTL

# Initialize diskcache
cache = Cache(directory=CACHE_DIR)


def load_cached_token() -> str | None:
    """
    Load token from disk cache.
    """
    token = cache.get("token")
    if not token:
        logger.error(f"❌ Errro loading token {token}")
    return token


def save_token_to_cache(token: str) -> None:
    """
    Save token with TTL to disk cache.
    """
    try:
        cache.set("token", token, expire=TOKEN_TTL_SECONDS)
        logger.info("✅ Token saved to cache")
    except Exception as e:
        logger.error(f"🚫 Failed to save token to cache: {e}")


def delete_cached_token() -> None:
    """
    Explicitly delete the cached token before TTL expires.
    """
    try:
        if "token" in cache:
            cache.delete("token")
            logger.info("🗑️ Token successfully deleted from cache")
        else:
            logger.warning("ℹ️ No token found in cache to delete")

        return {"success": True, "message": "Successfully Refreshed"}
    except Exception as e:
        logger.error(f"🚫 Failed to delete token from cache: {e}")
        return {"success": False, "message": "Fail to refresh"}
