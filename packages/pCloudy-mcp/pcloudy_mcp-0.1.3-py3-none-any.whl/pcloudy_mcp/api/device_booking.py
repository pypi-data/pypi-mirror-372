import logging

from ..Constant.constant import Constant
from .authenticate import AuthAPI
from .http_client import HttpClient

# import webbrowser


logger = logging.getLogger(__name__)
constant = Constant()
auth_api = AuthAPI()


class DeviceBooking(HttpClient):
    """
    This class handles device booking operations in the pCloudy MCP application.
    It provides methods to book devices, get device list, live view URL, and release bookings.
    """

    async def get_device_list(self, platform: str) -> dict:
        """
        Retrieve the list of devices available for booking.

        Args:
            platform (str): The platform to filter devices by ('android' or 'ios').

        Returns:
            dict: A dictionary containing the list of devices or error.
        """
        token = await auth_api.get_token()

        payload = {
            "token": token,
            "duration": constant.DURATION_TO_BOOK_DEVICE,
            "platform": platform,
            "available_now": "false",
        }
        headers = {"Content-Type": "application/json"}
        response = await self.post(
            constant.pclodyApiEndpoint.GET_DEVICE_LIST,
            data=payload,
            headers=headers,
        )
        return response

    async def book_device(self, platform: str, device_id: int) -> dict:
        """
        Book a device for the specified platform.

        Args:
            platform (str): The platform for the device.
            device_id (int): The ID of the device to book.

        Returns:
            dict: API response with booking details or error.
        """
        token = await auth_api.get_token()

        payload = {
            "token": token,
            "duration": constant.DURATION_TO_BOOK_DEVICE,
            "id": device_id,
        }

        headers = {"Content-Type": "application/json"}

        response = await self.post(
            constant.pclodyApiEndpoint.BOOK_DEVICE, data=payload, headers=headers
        )

        # Enable for auto open the url in browser

        # result = response.get("result", {})
        # rid = result.get("rid")

        # # If booking was successful, retrieve the live view URL
        # live_view_response = await self.get_live_view_url(rid=rid)
        # live_view_url = live_view_response.get("result", {}).get("URL")
        # webbrowser.open(live_view_ur)

        return response

    async def get_live_view_url(self, rid: int) -> dict:
        """
        Retrieve the live view URL for a booked device.

        Args:
            rid (int): The booking ID (RID).

        Returns:
            dict: API response with the live view URL or error.
        """
        token = await auth_api.get_token()

        payload = {"token": token, "rid": rid}

        headers = {"Content-Type": "application/json"}

        response = await self.post(
            constant.pclodyApiEndpoint.LIVE_VIEW_URL, data=payload, headers=headers
        )

        return response

    async def release_device(self, rid: int) -> dict:
        """
        Release a booked device.

        Args:
            rid (int): The booking ID (RID).

        Returns:
            dict: API response confirming release or error.
        """
        token = await auth_api.get_token()

        payload = {"token": token, "rid": rid}

        headers = {"Content-Type": "application/json"}

        response = await self.post(
            constant.pclodyApiEndpoint.RELEASE_DEVICE, data=payload, headers=headers
        )

        return response
