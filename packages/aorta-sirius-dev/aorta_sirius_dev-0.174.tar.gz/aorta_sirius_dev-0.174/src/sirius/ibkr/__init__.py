import asyncio
import datetime
import itertools
from decimal import Decimal
from enum import Enum, auto
from typing import List, Dict, Any, Type, Set

import httpx

from sirius import common
from sirius.common import DataClass, Currency
from sirius.exceptions import OperationNotSupportedException
from sirius.http_requests import AsyncHTTPSession, HTTPResponse

_account_list: List["IBKRAccount"] = []
_account_list_lock = asyncio.Lock()

base_url: str = common.get_environmental_secret("IBKR_SERVICE_BASE_URL", "https://ibkr-service:5000/v1/api/")
session: AsyncHTTPSession = AsyncHTTPSession(base_url)
session.client = httpx.AsyncClient(verify=False, timeout=60)


class ContractType(Enum):
    STOCK = "STK"
    OPTION = "OPT"
    FUTURE = "FUT"
    FUTURE_OPTION = "FOP"
    BOND = "BND"


class OptionContractType(Enum):
    PUT = auto()
    CALL = auto()


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

    @staticmethod
    def _get_contract_subclass(contract_type_str: str) -> Type["Contract"]:
        try:
            return {  # type: ignore[return-value]
                "STK": StockContract,
                "OPT": OptionContract,
                "FUT": FutureContract,
                "FOP": FuturesOptionContract,
                "BOND": BondContract,
            }[contract_type_str]
        except KeyError:
            raise OperationNotSupportedException(f"Unknown contract type string: {contract_type_str}")

    @staticmethod
    async def get(contract_id: int) -> "Contract":
        response: HTTPResponse = await session.get(f"{base_url}iserver/contract/{contract_id}/info")
        cls: Type[Contract] = Contract._get_contract_subclass(response.data["instrument_type"])
        return cls(
            id=contract_id,
            name=response.data["company_name"],
            symbol=response.data["symbol"],
            currency=Currency(response.data["currency"]),
        )

    @staticmethod
    async def find_contract_id(ticker: str, contract_type: ContractType) -> List[int]:
        response: HTTPResponse = await session.get(f"{base_url}iserver/secdef/search?symbol={ticker}&secType={contract_type.value}")
        valid_result_list: List[Dict[str, Any]] = list(filter(lambda d: d["description"] in Exchange, response.data))
        return [int(data["conid"]) for data in valid_result_list]

    @staticmethod
    async def find_contract(ticker: str, contract_type: ContractType) -> List["Contract"]:
        contract_id_list: List[int] = await Contract.find_contract_id(ticker, contract_type)
        return [await Contract.get(contract_id) for contract_id in contract_id_list]


class StockContract(Contract):
    pass


class OptionContract(Contract):
    strike_price: Decimal
    expiry_month_str: str
    type: OptionContractType

    @staticmethod
    async def get_all(underlying_contract: StockContract, expiry_month_str: str, strike_price: Decimal) -> List["OptionContract"]:
        response: HTTPResponse = await session.get(
            f"{base_url}iserver/secdef/info",
            query_params={
                "conid": underlying_contract.id,
                "sectype": ContractType.OPTION.value,
                "month": expiry_month_str,
                "strike": float(strike_price)}
        )

        return [OptionContract(
            **underlying_contract.model_dump(exclude={"id"}),
            id=data["conid"],
            strike_price=strike_price,
            expiry_month_str=expiry_month_str,
            type=OptionContractType.CALL if data["right"] == "C" else OptionContractType.PUT
        ) for data in response.data]

    @staticmethod
    async def find_all(underlying_contract: StockContract) -> List["OptionContract"]:
        option_contract_list: List[OptionContract] = []
        response: HTTPResponse = await session.get(f"{base_url}iserver/secdef/search?symbol={underlying_contract.symbol}&secType={ContractType.STOCK.value}")
        data: Dict[str, Any] = next(filter(lambda c: int(c["conid"]) == underlying_contract.id, response.data))
        option_data: Dict[str, Any] = next(filter(lambda o: ContractType(o["secType"]) == ContractType.OPTION, data["sections"]))
        expiry_month_str_list: List[str] = option_data["months"].split(";")

        responses: List[HTTPResponse] = await asyncio.gather(*[
            session.get(f"{base_url}iserver/secdef/strikes", query_params={"conid": underlying_contract.id, "sectype": ContractType.OPTION.value, "month": expiry_month_str})
            for expiry_month_str in expiry_month_str_list
        ])
        for expiry_month_str, response in zip(expiry_month_str_list, responses):
            all_strike_price_set: Set[Decimal] = set([Decimal(str(strike_price)) for strike_price in response.data.get("call", [])])
            all_strike_price_set.update([Decimal(str(strike_price)) for strike_price in response.data.get("put", [])])
            sub_option_contract_list: List[List[OptionContract]] = await asyncio.gather(*[
                OptionContract.get_all(underlying_contract, expiry_month_str, strike_price)
                for strike_price in all_strike_price_set
            ])

            option_contract_list.extend(list(itertools.chain.from_iterable(sub_option_contract_list)))

        return option_contract_list


class FutureContract(Contract):
    pass


class FuturesOptionContract(Contract):
    pass


class BondContract(Contract):
    pass


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
