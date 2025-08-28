import logging

from ..Constant.constant import Constant
from ..errors.exception import APIRequestError
from ..utils.config import Config
from ..utils.token_cache import load_cached_token, save_token_to_cache
from .http_client import HttpClient

logger = logging.getLogger(__name__)

config = Config()
constant = Constant()

USERNAME = config.userdetail.pcloudy_username
PASSWORD = config.userdetail.pcloudy_api_key


class AuthAPI(HttpClient):
    async def get_token(self):
        # Try using cached token first
        cached_token = load_cached_token()
        if cached_token:
            get_device_list_response = await self.authenticate_token(cached_token)
            if get_device_list_response.get("not_error"):
                return cached_token
            else:
                logger.warning(f"⚠️ {get_device_list_response.get('error')}")

        # If not found or invalid, fetch a new one
        auth = (USERNAME, PASSWORD)
        response = await self.get(constant.pclodyApiEndpoint.AUTHENTICATE, auth=auth)
        token = response.get("result", {}).get("token")

        if not token:
            error = response.get("result", {}).get("error")
            raise APIRequestError("Authentication", error)

        save_token_to_cache(token)
        return token

    async def authenticate_token(self, token: str) -> dict:
        """
        Authenticate the token with the server by calling the get-device-list endpoint.
        Returns a dict with keys 'not_error' and optionally 'error'.
        """
        payload = {
            "token": token,
            "duration": constant.DURATION_TO_BOOK_DEVICE,
            "platform": "android",
            "available_now": "false",
        }

        headers = {"Content-Type": "application/json"}

        response = await self.post(
            constant.pclodyApiEndpoint.GET_DEVICE_LIST,
            data=payload,
            headers=headers,
        )

        if response.get("result", {}).get("error"):
            return {
                "error": response.get("result", {}).get("error"),
                "not_error": False,
            }

        return {"not_error": True}
