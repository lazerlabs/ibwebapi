import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

from ibwebapi.client.endpoints import IBKREndpoint
from ibwebapi.client.rest_client import IBKRRESTClient


class TimePeriod(Enum):
    MIN_1 = "1min"
    MIN_2 = "2min"
    MIN_3 = "3min"
    MIN_5 = "5min"
    MIN_10 = "10min"
    MIN_15 = "15min"
    MIN_30 = "30min"
    HOUR_1 = "1h"
    HOUR_2 = "2h"
    HOUR_3 = "3h"
    HOUR_4 = "4h"
    HOUR_8 = "8h"
    DAY_1 = "1d"
    WEEK_1 = "1w"
    MONTH_1 = "1m"

    # Additional time periods
    MIN_4 = "4min"
    MIN_6 = "6min"
    MIN_7 = "7min"
    MIN_8 = "8min"
    MIN_9 = "9min"
    MIN_11 = "11min"
    MIN_12 = "12min"
    MIN_13 = "13min"
    MIN_14 = "14min"
    MIN_16 = "16min"
    MIN_17 = "17min"
    MIN_18 = "18min"
    MIN_19 = "19min"
    MIN_20 = "20min"
    MIN_21 = "21min"
    MIN_22 = "22min"
    MIN_23 = "23min"
    MIN_24 = "24min"
    MIN_25 = "25min"
    MIN_26 = "26min"
    MIN_27 = "27min"
    MIN_28 = "28min"
    MIN_29 = "29min"
    HOUR_5 = "5h"
    HOUR_6 = "6h"
    HOUR_7 = "7h"
    DAY_2 = "2d"
    DAY_3 = "3d"
    DAY_4 = "4d"
    DAY_5 = "5d"
    WEEK_2 = "2w"
    WEEK_3 = "3w"
    WEEK_4 = "4w"
    MONTH_2 = "2m"
    MONTH_3 = "3m"
    MONTH_4 = "4m"
    MONTH_5 = "5m"
    MONTH_6 = "6m"
    YEAR_1 = "1y"
    YEAR_2 = "2y"
    YEAR_3 = "3y"
    YEAR_4 = "4y"
    YEAR_5 = "5y"


class BarSize(Enum):
    MIN_1 = "1min"
    MIN_2 = "2min"
    MIN_3 = "3min"
    MIN_5 = "5min"
    MIN_10 = "10min"
    MIN_15 = "15min"
    MIN_30 = "30min"
    HOUR_1 = "1h"
    HOUR_2 = "2h"
    HOUR_3 = "3h"
    HOUR_4 = "4h"
    HOUR_8 = "8h"
    DAY_1 = "1d"
    WEEK_1 = "1w"
    MONTH_1 = "1m"


@dataclass
class HistoricalBar:
    o: float
    c: float
    h: float
    l: float  # noqa: E741
    volume: float = field(metadata={"json_key": "v"})
    timestamp: datetime = field(
        metadata={"json_key": "t"}, default_factory=lambda: datetime.fromtimestamp(0)
    )

    def __post_init__(self):
        if isinstance(self.timestamp, int):
            self.timestamp = datetime.fromtimestamp(self.timestamp // 1000)


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
        if isinstance(obj, datetime):
            return obj.isoformat()
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

    def object_hook(self, dct: Dict[str, Any]) -> Any:
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
    def __init__(self, *args, cache_dir: str = "./cache", **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_filename(
        self,
        prefix: str,
        conid: str,
        bar: BarSize,
        period: TimePeriod,
        exchange: Optional[str],
        start_time: Optional[datetime],
        outside_rth: bool,
    ) -> Path:
        params = f"{conid}_{bar.value}_{period.value}"
        params += f"_exchange={exchange}" if exchange else ""
        params += f"_start={start_time.strftime('%Y%m%d-%H%M%S')}" if start_time else ""
        params += f"_orth={'1' if outside_rth else '0'}"
        return self.cache_dir / f"{prefix}_{params}.json"

    async def get_historical_data_json(
        self,
        conid: str,
        bar: BarSize,
        period: TimePeriod = TimePeriod.WEEK_1,
        exchange: Optional[str] = None,
        start_time: Optional[datetime] = None,
        outside_rth: bool = False,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
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
        cache_file = self._get_cache_filename(
            "hmd", conid, bar, period, exchange, start_time, outside_rth
        )

        if not force_refresh and Path(cache_file).exists():
            with Path(cache_file).open("r") as f:
                return json.load(f)

        query_params = {
            "conid": conid,
            "bar": bar.value,
            "period": period.value,
            "outsideRth": str(outside_rth).lower(),
        }

        if exchange:
            query_params["exchange"] = exchange
        if start_time:
            query_params["startTime"] = start_time.strftime("%Y%m%d-%H:%M:%S")

        response = await self._request(
            "GET", IBKREndpoint.HISTORICAL_DATA, query_params=query_params
        )
        data = json.dumps(response)

        # Cache the response
        with Path(cache_file).open("w") as f:
            f.write(data)

        return response
        # return response

    async def get_historical_data(
        self,
        conid: str,
        bar: BarSize,
        period: TimePeriod = TimePeriod.WEEK_1,
        exchange: Optional[str] = None,
        start_time: Optional[datetime] = None,
        outside_rth: bool = False,
        force_refresh: bool = False,
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

        data = await self.get_historical_data_json(
            conid, bar, period, exchange, start_time, outside_rth, force_refresh
        )
        data = json.loads(data, cls=HistoricalDataJSONDecoder)

        return data
        # return response
