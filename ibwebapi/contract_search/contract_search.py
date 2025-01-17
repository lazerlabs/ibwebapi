import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from ibwebapi.client.endpoints import IBKREndpoint
from ibwebapi.client.rest_client import IBKRRESTClient


class Exchange(Enum):
    SMART = "SMART"
    UNKNOWN = "UNKNOWN"
    NASDAQ = "NASDAQ"
    MEXI = "MEXI"
    EBS = "EBS"
    AEQLIT = "AEQLIT"
    AMEX = "AMEX"
    NYSE = "NYSE"
    CBOE = "CBOE"
    PHLX = "PHLX"
    CHX = "CHX"
    ARCA = "ARCA"
    ISLAND = "ISLAND"
    ISE = "ISE"
    IDEAL = "IDEAL"
    NASDAQQ = "NASDAQQ"
    DRCTEDGE = "DRCTEDGE"
    BEX = "BEX"
    BATS = "BATS"
    NITEECN = "NITEECN"
    EDGEA = "EDGEA"
    CSFBALGO = "CSFBALGO"
    JEFFALGO = "JEFFALGO"
    NYSENASD = "NYSENASD"
    PSX = "PSX"
    BYX = "BYX"
    ITG = "ITG"
    PDQ = "PDQ"
    IBKRATS = "IBKRATS"
    CITADEL = "CITADEL"
    NYSEDARK = "NYSEDARK"
    MIAX = "MIAX"
    IBDARK = "IBDARK"
    CITADELDP = "CITADELDP"
    NASDDARK = "NASDDARK"
    IEX = "IEX"
    WEDBUSH = "WEDBUSH"
    SUMMER = "SUMMER"
    WINSLOW = "WINSLOW"
    FINRA = "FINRA"
    LIQITG = "LIQITG"
    UBSDARK = "UBSDARK"
    BTIG = "BTIG"
    VIRTU = "VIRTU"
    JEFF = "JEFF"
    OPCO = "OPCO"
    COWEN = "COWEN"
    DBK = "DBK"
    JPMC = "JPMC"
    EDGX = "EDGX"
    JANE = "JANE"
    NEEDHAM = "NEEDHAM"
    FRACSHARE = "FRACSHARE"
    RBCALGO = "RBCALGO"
    VIRTUDP = "VIRTUDP"
    BAYCREST = "BAYCREST"
    FOXRIVER = "FOXRIVER"
    MND = "MND"
    NITEEXST = "NITEEXST"
    PEARL = "PEARL"
    GSDARK = "GSDARK"
    NITERTL = "NITERTL"
    NYSENAT = "NYSENAT"
    IEXMID = "IEXMID"
    HRT = "HRT"
    FLOWTRADE = "FLOWTRADE"
    HRTDP = "HRTDP"
    JANELP = "JANELP"
    PEAK6 = "PEAK6"
    IMCDP = "IMCDP"
    CTDLZERO = "CTDLZERO"
    HRTMID = "HRTMID"
    JANEZERO = "JANEZERO"
    HRTEXST = "HRTEXST"
    IMCLP = "IMCLP"
    LTSE = "LTSE"
    SOCGENDP = "SOCGENDP"
    MEMX = "MEMX"
    INTELCROS = "INTELCROS"
    VIRTUBYIN = "VIRTUBYIN"
    JUMPTRADE = "JUMPTRADE"
    NITEZERO = "NITEZERO"
    TPLUS1 = "TPLUS1"
    XTXEXST = "XTXEXST"
    XTXDP = "XTXDP"
    XTXMID = "XTXMID"
    COWENLP = "COWENLP"
    BARCDP = "BARCDP"
    JUMPLP = "JUMPLP"
    OLDMCLP = "OLDMCLP"
    RBCCMALP = "RBCCMALP"
    WALLBETH = "WALLBETH"
    IBEOS = "IBEOS"
    JONES = "JONES"
    GSLP = "GSLP"
    BLUEOCEAN = "BLUEOCEAN"
    USIBSILP = "USIBSILP"
    OVERNIGHT = "OVERNIGHT"
    JANEMID = "JANEMID"
    IBATSEOS = "IBATSEOS"
    HRTZERO = "HRTZERO"
    VIRTUALGO = "VIRTUALGO"


class AssetClass(Enum):
    STK = "STK"  # stock (or ETF)
    OPT = "OPT"  # option
    FUT = "FUT"  # future
    IND = "IND"  # index
    FOP = "FOP"  # futures option
    CASH = "CASH"  # forex pair
    BAG = "BAG"  # combo
    WAR = "WAR"  # warrant
    BND = "BND"  # bond
    FND = "FND"  # mutual fund
    ICS = "ICS"  # inter-commodity spread
    CFD = "CFD"  # contract for difference
    SWP = "SWP"  # forex


@dataclass
class Contract:
    conid: int
    exchange: Exchange = Exchange.UNKNOWN
    isUS: Optional[bool] = None


@dataclass
class StockInfo:
    name: str
    chineseName: Optional[str]
    assetClass: AssetClass
    contracts: List[Contract] = field(default_factory=list)


@dataclass
class StockData:
    stocks: List[StockInfo] = field(default_factory=list)


class StockDataEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, StockData):
            return {"stocks": [self.default(stock) for stock in obj.stocks]}
        elif isinstance(obj, StockInfo):
            return {
                "name": obj.name,
                "chineseName": obj.chineseName,
                "assetClass": obj.assetClass.value,
                "contracts": [self.default(contract) for contract in obj.contracts],
            }
        elif isinstance(obj, Contract):
            return {
                "conid": obj.conid,
                "exchange": obj.exchange.value,
                "isUS": obj.isUS,
            }
        elif isinstance(obj, Enum):
            return obj.value
        return super().default(obj)


class StockDataDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct: Dict[str, Any]) -> Any:
        if "stocks" in dct:
            return StockData(
                stocks=[self.object_hook(stock) for stock in dct["stocks"]]
            )
        elif "name" in dct and "assetClass" in dct:
            return StockInfo(
                name=dct["name"],
                chineseName=dct["chineseName"],
                assetClass=AssetClass(dct["assetClass"]),
                contracts=[self.object_hook(contract) for contract in dct["contracts"]],
            )
        elif "conid" in dct:
            return Contract(
                conid=dct["conid"],
                exchange=Exchange(dct.get("exchange", "UNKNOWN")),
                isUS=dct.get("isUS"),
            )
        return dct


def encode_stock_data(data: StockData) -> str:
    return json.dumps(data, cls=StockDataEncoder)


def decode_stock_data(json_str: str) -> StockData:
    return json.loads(json_str, object_hook=stock_data_decoder)


class IBKRContractSearch(IBKRRESTClient):
    async def search_contract(self, symbol: str) -> Dict[str, Any]:
        """
        Searches for a contract by symbol and returns the contract details.

        :param symbol: The symbol to search for
        :return: Dictionary containing contract details
        """
        query_params = {"symbol": symbol, "name": True, "secType": "STK"}
        return await self._request(
            "GET", IBKREndpoint.CONTRACT_SEARCH, query_params=query_params
        )

    async def get_stock_info(self, symbols: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieves detailed stock information for given symbols.

        :param symbols: Comma-separated string of stock symbols
        :return: Dictionary with symbols as keys and lists of stock info as values
        """
        query_params = {"symbols": symbols}

        response = await self._request(
            "GET",
            IBKREndpoint.STOCK_INFO,
            query_params=query_params,
        )

        return response

    async def get_contract_details(self, conid: int) -> Dict[str, Any]:
        """
        Returns a list of contract details for the given conid.

        :param conid: The contract identifier
        :return: Dictionary containing contract details
        """
        return await self._request(
            "GET", IBKREndpoint.CONTRACT_DETAILS, path_params={"conid": conid}
        )

    async def test_module(self) -> str:
        print("-=" * 30, 'SOMETHING"')
        return "test_module"

    async def get_contract_rules(
        self, conid: int, isBuy: bool = True
    ) -> Dict[str, Any]:
        """
        Returns trading related rules for a specific contract and side.

        :param conid: The contract identifier
        :param isBuy: True for buy side rules, False for sell side rules
        :return: Dictionary containing contract rules
        """
        data = {"conid": conid, "isBuy": isBuy}
        return await self._request("POST", IBKREndpoint.CONTRACT_RULES, json=data)

    async def get_secdef(self, conid: int) -> Dict[str, Any]:
        """
        Returns the security definition for the given conid.
        """
        data = {"conids": conid}
        return await self._request("GET", IBKREndpoint.SECDEF, query_params=data)

    async def get_secdef_info(
        self,
        conid: int,
        sectype: Optional[str] = None,
        month: Optional[str] = None,
        strike: Optional[float] = None,
        right: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Validates the contract ID for the derivative contract.

        :param conid: The contract identifier of the underlying
        :param sectype: The security type (e.g., "OPT" for options)
        :param month: The expiration month (e.g., "JAN25")
        :param strike: The strike price
        :param right: The option right (e.g., "C" for call, "P" for put)
        :return: Dictionary containing contract validation information
        """
        query_params: dict[str, Union[str, float, int]] = {"conid": conid}
        if sectype:
            query_params["secType"] = sectype
        if month:
            query_params["month"] = month
        if strike is not None:
            query_params["strike"] = strike
        if right:
            query_params["right"] = right

        return await self._request(
            "GET", IBKREndpoint.SECDEF_INFO, query_params=query_params
        )

    async def get_all_conids(self, exchange: Exchange) -> List[Dict[str, Any]]:
        """
        Retrieves all contracts made available on a requested exchange.

        :param exchange: The exchange to retrieve contracts for
        :return: List of dictionaries containing contract information
        """
        response = await self._request(
            "GET", IBKREndpoint.ALL_CONIDS, query_params={"exchange": exchange.value}
        )
        return [response] if isinstance(response, dict) else response

    async def get_strikes(self, conid: int, sectype: str, month: str) -> Dict[str, Any]:
        """
        Retrieves all strikes for a given underlying and expiration.

        :param conid: The contract identifier of the underlying
        :param sectype: The security type (e.g., "OPT" for options)
        :param month: The expiration month (e.g., "JAN25")
        :return: Dictionary containing strike information
        """
        query_params = {"conid": conid, "secType": sectype, "month": month}
        return await self._request(
            "GET", IBKREndpoint.STRIKES, query_params=query_params
        )

    async def get_contract_for_stock(
        self, symbol: str, exchange: Exchange, is_us: bool
    ) -> Optional[int]:
        """
        Retrieves the conid for a specific stock given its symbol, exchange, and US status.

        :param symbol: The symbol to search for
        :param exchange: The exchange to search in
        :param is_us: Whether the stock is a US stock
        :return: The conid if found, None otherwise
        """
        stock_info = await self.get_stock_info(symbol)

        if symbol not in stock_info:
            return None

        for stock in stock_info[symbol]:
            if stock["assetClass"] == "STK":
                for contract in stock["contracts"]:
                    if (
                        contract.get("exchange") == exchange.value
                        and contract.get("isUS") == is_us
                    ):
                        return contract["conid"]

        return None
