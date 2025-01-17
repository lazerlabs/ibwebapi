import asyncio
import logging
from typing import Any, Dict, Optional, Set
from urllib.parse import urlencode

import aiohttp
from aiohttp import ClientResponse, ClientSession

from ibwebapi.client.endpoints import Endpoint, IBKREndpoint

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IBKRRESTClient:
    def __init__(
        self,
        base_url: str,
        session_timeout: int = 60,
        max_retries: int = 3,
        retry_statuses: Optional[Set[int]] = None,
        initial_retry_delay: float = 1.0,
        max_retry_delay: float = 60.0,
        unauthorized_initial_delay: float = 60.0,
        unauthorized_retry_delay: float = 300.0,  # 5 minutes
        unauthorized_max_retries: int = 12,  # Try for up to 1 hour by default
    ):
        self.base_url = base_url
        self.session_timeout = session_timeout
        self.session: Optional[ClientSession] = None
        self.connected = False
        self._endpoint_map = {endpoint: endpoint.value for endpoint in IBKREndpoint}
        self._last_request_time = 0.0
        self._rate_limit_lock = asyncio.Lock()
        self.max_retries = max_retries
        self.retry_statuses = retry_statuses or {
            429,
            503,
            502,
            504,
        }  # Common transient errors
        self.initial_retry_delay = initial_retry_delay
        self.max_retry_delay = max_retry_delay
        self.unauthorized_initial_delay = unauthorized_initial_delay
        self.unauthorized_retry_delay = unauthorized_retry_delay
        self.unauthorized_max_retries = unauthorized_max_retries

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def connect(self):
        """Establishes a connection with the IBKR API and keeps it alive."""
        backoff = 1
        while not self.connected:
            try:
                self.session = aiohttp.ClientSession(
                    connector=aiohttp.TCPConnector(ssl=True, verify_ssl=False)
                )
                logger.info("Attempting to connect to IBKR API with rate limiting...")
                await self.tickle()
                logger.info("Connection established.")
                self.connected = True
                backoff = 1
            except aiohttp.ClientError as e:
                logger.error(
                    f"Connection failed: {e}. Retrying in {backoff} seconds..."
                )
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60)

    async def disconnect(self):
        """Closes the session gracefully."""
        if self.session:
            await self.session.close()
            self.session = None
            self.connected = False
            logger.info("Disconnected from IBKR API.")

    def _get_retry_params(
        self, status_code: int, retry_count: int
    ) -> tuple[float, int]:
        """Get retry delay and max retries based on status code."""
        if status_code == 401:
            # For unauthorized errors, use longer delays
            if retry_count == 0:
                return self.unauthorized_initial_delay, self.unauthorized_max_retries
            return self.unauthorized_retry_delay, self.unauthorized_max_retries
        else:
            # For other errors, use exponential backoff
            delay = min(
                self.initial_retry_delay * (2**retry_count),
                self.max_retry_delay,
            )
            return delay, self.max_retries

    async def _request(
        self,
        method: str,
        endpoint: IBKREndpoint,
        path_params: Dict[str, Any] | None = None,
        query_params: Dict[str, Any] | None = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generic method to make API requests with rate limiting and retries."""
        if not self.session:
            raise RuntimeError("Not connected to IBKR API")

        # Calculate wait time based on rate limit
        rate_limit = endpoint.value.rate_limit
        wait_time = 1.0 / rate_limit if rate_limit > 0 else 0
        retry_count = 0
        last_error = None

        while True:
            try:
                async with self._rate_limit_lock:
                    # Wait for rate limit
                    now = asyncio.get_event_loop().time()
                    time_since_last = now - self._last_request_time
                    if time_since_last < wait_time:
                        await asyncio.sleep(wait_time - time_since_last)

                    url = f"{self.base_url}{self._endpoint_map[endpoint]}"
                    if path_params:
                        url = url.format(**path_params)
                    if query_params:
                        url += f"?{urlencode(query_params)}"

                    logger.debug(f"Making request to: {url}")
                    async with getattr(self.session, method.lower())(
                        url, **kwargs
                    ) as response:
                        if (
                            response.status == 401
                            or response.status in self.retry_statuses
                        ):
                            retry_delay, max_retries = self._get_retry_params(
                                response.status, retry_count
                            )

                            if retry_count >= max_retries:
                                error_msg = await response.text()
                                logger.error(
                                    f"Max retries ({max_retries}) exceeded for status {response.status}. "
                                    f"Last error: {error_msg}"
                                )
                                response.raise_for_status()

                            error_msg = await response.text()
                            if response.status == 401:
                                logger.warning(
                                    f"Gateway authentication failed (status 401). "
                                    f"Attempt {retry_count + 1}/{max_retries}. "
                                    f"Waiting {retry_delay:.1f} seconds for gateway to recover. "
                                    f"Error: {error_msg}"
                                )
                            else:
                                logger.warning(
                                    f"Received status {response.status} from {url}. "
                                    f"Attempt {retry_count + 1}/{max_retries}. "
                                    f"Retrying in {retry_delay:.1f} seconds. Error: {error_msg}"
                                )

                            await asyncio.sleep(retry_delay)
                            retry_count += 1
                            continue

                        await self._handle_response(response)
                        self._last_request_time = asyncio.get_event_loop().time()
                        return await response.json()

            except aiohttp.ClientResponseError as e:
                last_error = e
                if e.status == 401 or e.status in self.retry_statuses:
                    retry_delay, max_retries = self._get_retry_params(
                        e.status, retry_count
                    )

                    if retry_count >= max_retries:
                        logger.error(
                            f"Max retries ({max_retries}) exceeded for status {e.status}. "
                            f"Last error: {str(e)}"
                        )
                        raise

                    if e.status == 401:
                        logger.warning(
                            f"Gateway authentication failed (status 401). "
                            f"Attempt {retry_count + 1}/{max_retries}. "
                            f"Waiting {retry_delay:.1f} seconds for gateway to recover. "
                            f"Error: {str(e)}"
                        )
                    else:
                        logger.warning(
                            f"Request failed with status {e.status}. "
                            f"Attempt {retry_count + 1}/{max_retries}. "
                            f"Retrying in {retry_delay:.1f} seconds. Error: {str(e)}"
                        )

                    await asyncio.sleep(retry_delay)
                    retry_count += 1
                    continue
                raise

            except aiohttp.ClientError as e:
                logger.error(f"Request failed: {e}")
                self.connected = False
                raise

    async def _handle_response(self, response: ClientResponse) -> None:
        """Handle API response and raise appropriate exceptions."""
        if response.status >= 400:
            error_msg = await response.text()
            logger.error(f"API error: {response.status} - {error_msg}")
            response.raise_for_status()

    async def tickle(self) -> Dict[str, Any]:
        """Sends a tickle request to keep the session alive."""
        return await self._request("GET", IBKREndpoint.TICKLE)

    async def run(self):
        """Main loop to maintain the connection and send periodic tickles."""
        async with self:
            try:
                while True:
                    await self.tickle()
                    await asyncio.sleep(self.session_timeout)
            except asyncio.CancelledError:
                logger.info("Stopping client...")
