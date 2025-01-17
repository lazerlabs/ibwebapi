from dataclasses import dataclass
from enum import Enum, auto


@dataclass
class Endpoint:
    path: str
    rate_limit: int = 10

    def __str__(self):
        return self.path


class IBKREndpoint(Enum):
    TICKLE = Endpoint("/tickle", 1)
    ACCOUNT_SUMMARY = Endpoint("/portfolio/{accountId}/summary", 5)
    PORTFOLIO_ACCOUNTS = Endpoint("/portfolio/accounts")
    HISTORICAL_DATA = Endpoint("/iserver/marketdata/history", 5)
    CONTRACT_SEARCH = Endpoint("/iserver/secdef/search")
    STOCK_INFO = Endpoint("/trsrv/stocks")
    CONTRACT_DETAILS = Endpoint("/iserver/contract/{conid}/info")
    CONTRACT_INFO = Endpoint("/iserver/contract/{conid}/info-quick")
    CONTRACT_RULES = Endpoint("/iserver/contract/rules")
    SECDEF = Endpoint("/trsrv/secdef")
    SECDEF_INFO = Endpoint("/iserver/secdef/info")
    ALL_CONIDS = Endpoint("/trsrv/all-conids")
    STRIKES = Endpoint("/iserver/secdef/strikes")
