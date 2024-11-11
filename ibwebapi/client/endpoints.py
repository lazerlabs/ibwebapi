from enum import Enum, auto


class IBKREndpoint(Enum):
    TICKLE = "/tickle"
    ACCOUNT_SUMMARY = "/portfolio/{accountId}/summary"
    PORTFOLIO_ACCOUNTS = "/portfolio/accounts"
    HISTORICAL_DATA = "/iserver/marketdata/history"
    CONTRACT_SEARCH = "/iserver/secdef/search"
    STOCK_INFO = "/trsrv/stocks"
    CONTRACT_DETAILS = "/iserver/contract/{conid}/info"
    CONTRACT_INFO = "/iserver/contract/{conid}/info-quick"
    CONTRACT_RULES = "/iserver/contract/rules"
    SECDEF = "/trsrv/secdef"
    SECDEF_INFO = "/iserver/secdef/info"
    ALL_CONIDS = "/trsrv/all-conids"
    STRIKES = "/iserver/secdef/strikes"
