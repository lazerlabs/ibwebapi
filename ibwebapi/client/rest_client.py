import asyncio
import logging
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import aiohttp
from aiohttp import ClientResponse, ClientSession

from ibwebapi.client.endpoints import IBKREndpoint

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IBKRRESTClient:
    def __init__(self, base_url: str, session_timeout: int = 60):
        self.base_url = base_url
        self.session_timeout = session_timeout
        self.session: Optional[ClientSession] = None
        self.connected = False
        self._endpoint_map = {endpoint: endpoint.value for endpoint in IBKREndpoint}

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
                logger.info("Attempting to connect to IBKR API...")
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

    async def _request(
        self,
        method: str,
        endpoint: IBKREndpoint,
        path_params: Dict[str, Any] = None,
        query_params: Dict[str, Any] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generic method to make API requests."""
        if not self.session:
            raise RuntimeError("Not connected to IBKR API")

        url = f"{self.base_url}{self._endpoint_map[endpoint]}"
        logger.info(f"Request URL: {url}")

        # Handle path parameters
        if path_params:
            url = url.format(**path_params)

        # Handle query parameters
        if query_params:
            url += f"?{urlencode(query_params)}"

        try:
            async with getattr(self.session, method.lower())(url, **kwargs) as response:
                await self._handle_response(response)
                return await response.json()
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
