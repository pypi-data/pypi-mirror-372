import json
import logging
import textwrap
import traceback

import httpx
import tenacity
from tenacity import retry, stop_after_attempt, wait_fixed

from ..Constant.constant import Constant

logger = logging.getLogger(__name__)
constant = Constant()

maxRetries = constant.httpRetryConfig.MAX_RETRIES
waitSeconds = constant.httpRetryConfig.WAIT_SECONDS
timeout = constant.httpRetryConfig.TIMEOUT


class HttpClient:
    @retry(stop=stop_after_attempt(maxRetries), wait=wait_fixed(waitSeconds))
    async def get(self, endpoint: str, headers: dict = None, auth=None):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(endpoint, headers=headers, auth=auth)
                self._validate_response(response, endpoint, headers, auth)
                return response.json()
        except Exception as e:
            return self._handle_exception(e)

    @retry(stop=stop_after_attempt(maxRetries), wait=wait_fixed(waitSeconds))
    async def post(
        self,
        endpoint: str,
        data: dict = None,
        headers: dict = None,
        files: dict = None,
    ):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                if files:
                    response = await client.post(
                        endpoint, data=data, files=files, headers=headers
                    )
                else:
                    response = await client.post(endpoint, json=data, headers=headers)

                self._validate_response(response, endpoint, headers, data, files)
                return response.json()
        except Exception as e:
            return self._handle_exception(e)

    def _validate_response(
        self,
        response: httpx.Response,
        endpoint: str,
        headers: dict = None,
        data: dict = None,
        files: dict = None,
        auth=None,
    ):
        if response.status_code != 200:
            try:
                response_body = response.json()
            except Exception:
                response_body = response.text  # fallback if not JSON
            request_payload = {
                "Endpoint": endpoint,
                "Headers": headers,
                "Data": data,
                "Files": files,
                "Auth": auth,
            }
            message = textwrap.dedent(
                f"""
                 Request Payload:
                 {json.dumps(request_payload, indent=2)}

                Response Body:
                {json.dumps(response_body, indent=2) if isinstance(response_body, dict) else response_body}
                """
            )

            raise httpx.HTTPStatusError(
                message.strip(),
                request=response.request,
                response=response,
            )

    def _handle_exception(self, e: Exception) -> dict:
        """Capture and log full trace from RetryError or any other error."""
        if isinstance(e, tenacity.RetryError) and e.last_attempt:
            final_exc = e.last_attempt.exception()
            stack_trace = "".join(
                traceback.format_exception(
                    type(final_exc), final_exc, final_exc.__traceback__
                )
            )
            logger.error(f"RetryError occurred:\n{stack_trace}")
            return {
                "error": f"{type(final_exc).__name__}: {final_exc}",
                "stack_trace": stack_trace,
            }
        else:
            stack_trace = traceback.format_exc()
            logger.error(f"Unexpected error occurred:\n{stack_trace}")
            return {
                "error": f"{type(e).__name__}: {e}",
                "stack_trace": stack_trace,
            }
