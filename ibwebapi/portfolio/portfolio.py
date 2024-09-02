from typing import Any, Dict

from ibwebapi.client.endpoints import IBKREndpoint
from ibwebapi.client.rest_client import IBKRRESTClient


class IBKRPortfolio(IBKRRESTClient):
    async def get_account_summary(self, account_id: str) -> Dict[str, Any]:
        """Retrieves account summary for a given account ID."""
        return await self._request(
            "GET", IBKREndpoint.ACCOUNT_SUMMARY, path_params={"accountId": account_id}
        )

    async def get_portfolio_accounts(self) -> Dict[str, Any]:
        """Retrieves a list of portfolio accounts."""
        return await self._request("GET", IBKREndpoint.PORTFOLIO_ACCOUNTS)
