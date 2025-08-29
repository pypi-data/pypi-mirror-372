import asyncio
import datetime
import itertools
from decimal import Decimal
from enum import Enum
from typing import List, Dict, Any

import httpx

from sirius import common
from sirius.common import DataClass, Currency
from sirius.http_requests import AsyncHTTPSession, HTTPResponse

_account_list: List["IBKRAccount"] = []
_account_list_lock = asyncio.Lock()

base_url: str = common.get_environmental_secret("IBKR_SERVICE_BASE_URL", "https://ibkr-service:5000/v1/api/")
session: AsyncHTTPSession = AsyncHTTPSession(base_url)
session.client = httpx.AsyncClient(verify=False)


class ContractType(Enum):
    STOCK = "STK"
    OPTION = "OPT"
    FUTURE = "FUT"
    FUTURE_OPTION = "FOP"
    BOND = "BND"


class Exchange(Enum):
    NASDAQ = "NASDAQ"


class IBKRAccount(DataClass):
    id: str
    name: str

    @staticmethod
    async def get_all_ibkr_accounts() -> List["IBKRAccount"]:
        global _account_list
        if len(_account_list) == 0:
            async with _account_list_lock:
                if len(_account_list) == 0:
                    response: HTTPResponse = await session.get(f"{base_url}/portfolio/accounts/")
                    _account_list = [IBKRAccount(id=data["id"], name=data["accountAlias"] if data["accountAlias"] else data["id"]) for data in response.data]

        return _account_list


class Contract(DataClass):
    id: int
    name: str
    symbol: str
    currency: Currency
    type: ContractType

    @staticmethod
    async def get_from_contract_id(contract_id: int) -> "Contract":
        response: HTTPResponse = await session.get(f"{base_url}iserver/contract/{contract_id}/info")
        return Contract(
            id=contract_id,
            name=response.data["company_name"],
            symbol=response.data["symbol"],
            currency=Currency(response.data["currency"]),
            type=ContractType(response.data["instrument_type"]),
        )

    @staticmethod
    async def find_contract_id(ticker: str, contract_type: ContractType) -> List[int]:
        response: HTTPResponse = await session.get(f"{base_url}iserver/secdef/search?symbol={ticker}&secType={contract_type.value}")
        valid_result_list: List[Dict[str, Any]] = list(filter(lambda d: d["description"] in Exchange, response.data))
        return [int(data["conid"]) for data in valid_result_list]

    @staticmethod
    async def find_contract(ticker: str, contract_type: ContractType) -> List["Contract"]:
        contract_id_list: List[int] = await Contract.find_contract_id(ticker, contract_type)
        return [await Contract.get_from_contract_id(contract_id) for contract_id in contract_id_list]


class MarketData(DataClass):
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    timestamp: datetime.datetime

    @staticmethod
    def _get_from_ohlc_data(ohlc_data: Dict[str, float]) -> "MarketData":
        return MarketData(
            open=Decimal(str(ohlc_data["o"])),
            high=Decimal(str(ohlc_data["h"])),
            low=Decimal(str(ohlc_data["l"])),
            close=Decimal(str(ohlc_data["c"])),
            volume=Decimal(str(ohlc_data["v"])),
            timestamp=datetime.datetime.fromtimestamp(ohlc_data["t"] / 1000),
        )

    @staticmethod
    async def _get_ohlc_data(contract_id: int, from_time: datetime.datetime, to_time: datetime.datetime) -> List[Dict[str, float]]:
        number_of_days: int = (to_time - from_time).days
        date_format_code: str = "%Y%m%d-%H:%M:%S"
        response: HTTPResponse = await session.get(
            f"{base_url}iserver/marketdata/history",
            query_params={
                "conid": contract_id,
                "period": f"{min(number_of_days, 999)}d",
                "bar": "1d",
                "startTime": to_time.strftime(date_format_code),
                "direction": "-1"
            }
        )

        response_from_time: datetime.datetime = datetime.datetime.strptime(response.data["startTime"], date_format_code)
        raw_ohlc_data = list(filter(lambda data: data["t"] >= (from_time.timestamp() * 1000), response.data["data"]))

        if from_time < response_from_time:
            new_raw_ohlc_data: List[Dict[str, float]] = await MarketData._get_ohlc_data(contract_id, from_time, response_from_time)
            raw_ohlc_data = list(itertools.chain.from_iterable([raw_ohlc_data, new_raw_ohlc_data]))

        return raw_ohlc_data

    @staticmethod
    async def get(contract_id: int, from_time: datetime.datetime, to_time: datetime.datetime | None = None) -> List["MarketData"]:
        to_time = to_time if to_time else datetime.datetime.now()
        return [MarketData._get_from_ohlc_data(ohlc_data) for ohlc_data in await MarketData._get_ohlc_data(contract_id, from_time, to_time)]
