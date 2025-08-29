import asyncio
from decimal import Decimal
from typing import List, Dict

import httpx

from sirius import common
from sirius.common import DataClass, Currency
from sirius.http_requests import AsyncHTTPSession, HTTPResponse

_account_list: List["IBKRAccount"] = []
_account_list_lock = asyncio.Lock()


class Contract(DataClass):
    description: str
    currency: Currency
    position: Decimal
    average_cost: Decimal
    market_value: Decimal
    type: str

    @staticmethod
    async def get_all(account_id: str) -> List["Contract"]:
        contract_type_dict: Dict[str, str] = {"STK": "Stock", "OPT": "Option", "FUT": "Future", "FOP": "Future's Option", "BND": "Bond"}
        base_url: str = common.get_environmental_secret("IBKR_SERVICE_BASE_URL")
        url: str = f"{base_url}/portfolio/{account_id}/positions/"
        session: AsyncHTTPSession = AsyncHTTPSession(base_url)

        await session.client.aclose()
        session.client = httpx.AsyncClient(verify=False)
        response: HTTPResponse = await session.get(url)
        return [
            Contract(
                description=data["contractDesc"],
                currency=Currency(data["currency"]),
                position=Decimal(str(data["position"])),
                average_cost=Decimal(str(data["avgPrice"])),
                market_value=Decimal(str(data["mktPrice"])),
                type=contract_type_dict[data['assetClass']],
            )
            for data in response.data
        ]


class IBKRAccount(DataClass):
    id: str
    name: str
    contract_list: List[Contract] = []

    @staticmethod
    async def get_all_ibkr_accounts() -> List["IBKRAccount"]:
        global _account_list
        if len(_account_list) == 0:
            async with _account_list_lock:
                if len(_account_list) == 0:
                    base_url: str = common.get_environmental_secret("IBKR_SERVICE_BASE_URL")
                    url: str = f"{base_url}/portfolio/accounts/"
                    session: AsyncHTTPSession = AsyncHTTPSession(base_url)

                    await session.client.aclose()
                    session.client = httpx.AsyncClient(verify=False)
                    response: HTTPResponse = await session.get(url)

                    _account_list = [IBKRAccount(id=data["id"], name=data["accountAlias"] if data["accountAlias"] else data["id"]) for data in response.data]

        return _account_list
