from enum import Enum, auto


class IBKREndpoint(Enum):
    TICKLE = auto()
    ACCOUNT_SUMMARY = auto()
    PORTFOLIO_ACCOUNTS = auto()
    HISTORICAL_DATA = auto()
