import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ibwebapi.client.endpoints import IBKREndpoint

from ..client.rest_client import IBKRRESTClient


@dataclass
class HistoricalBar:
    o: float
    c: float
    h: float
    l: float  # noqa: E741
    volume: float = field(metadata={"json_key": "v"})
    timestamp: int = field(metadata={"json_key": "t"})


@dataclass
class HistoricalData:
    serverId: str
    symbol: str
    text: str
    priceFactor: str
    startTime: str
    high: str
    low: str
    timePeriod: str
    barLength: int
    mdAvailability: str
    mktDataDelay: int
    outsideRth: bool
    tradingDayDuration: int
    volumeFactor: int
    priceDisplayRule: int
    priceDisplayValue: str
    chartPanStartTime: str
    direction: int
    negativeCapable: bool
    messageVersion: int
    points: int
    travelTime: int
    data: list[HistoricalBar] = field(default_factory=list)


class HistoricalDataJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, HistoricalData):
            return obj.__dict__
        if isinstance(obj, HistoricalBar):
            return {
                field.metadata.get("json_key", field.name): getattr(obj, field.name)
                for field in obj.__dataclass_fields__.values()
            }
        return super().default(obj)


class HistoricalDataJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if all(key in dct for key in ["o", "c", "h", "l", "v", "t"]):
            return HistoricalBar(
                o=dct["o"],
                c=dct["c"],
                h=dct["h"],
                l=dct["l"],
                volume=dct["v"],
                timestamp=dct["t"],
            )
        if "serverId" in dct and "data" in dct:
            dct["data"] = [
                self.object_hook(bar) if isinstance(bar, dict) else bar
                for bar in dct["data"]
            ]
            return HistoricalData(**dct)
        return dct


class IBKRMarketData(IBKRRESTClient):
    async def get_historical_data(
        self,
        conid: str,
        bar: str,
        period: str = "1w",
        exchange: Optional[str] = None,
        start_time: Optional[datetime] = None,
        outside_rth: bool = False,
    ) -> HistoricalData:
        """
        Retrieves historical market data for a given contract.

        :param conid: Contract identifier for the ticker symbol of interest
        :param bar: Individual bars of data to be returned (e.g., '1min', '5min', '1h', '1d')
        :param period: Overall duration for which data should be returned (default: '1w')
        :param exchange: Returns the data from the specified exchange
        :param start_time: Starting date and time of the request duration
        :param outside_rth: Include data outside regular trading hours
        :return: Dictionary containing historical market data
        """
        query_params = {
            "conid": conid,
            "bar": bar,
            "period": period,
            "outsideRth": str(outside_rth).lower(),
        }

        if exchange:
            query_params["exchange"] = exchange
        if start_time:
            query_params["startTime"] = start_time.strftime("%Y%m%d-%H:%M:%S")

        response = await self._request(
            "GET", IBKREndpoint.HISTORICAL_DATA, query_params=query_params
        )
        data = json.loads(json.dumps(response), cls=HistoricalDataJSONDecoder)
        return data
        # return response
