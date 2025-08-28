from typing import Self

import httpx

from .enums import Currency, Market
from .models import (
    CurrencyRates,
    FloatInfo,
    Items,
    ListingsHistoryAggregated,
    ListingsLatestAggregated,
    PlayerCountsHistory,
    PlayerCountsLatest,
    SalesHistoryAggregated,
    SalesLatestAggregated,
    SteamFriendslist,
    SteamInventory,
    SteamProfile,
)


class CSMarketAPI:
    def __init__(self, api_key: str):
        self.client = httpx.AsyncClient(
            base_url="https://api.csmarketapi.com",
            params={
                "key": api_key,
            },
            follow_redirects=True,
        )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[Exception] | None,
        exc_value: Exception | None,
        traceback: any,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        await self.client.aclose()
        self.client = None

    async def get_listings_latest_aggregated(
        self,
        market_hash_name: str,
        markets: list[Market],
        currency: Currency = Currency.USD,
        max_age: str | None = None,
    ) -> ListingsLatestAggregated:
        r = await self.client.get(
            "/v1/listings/latest/aggregate",
            params={
                "market_hash_name": market_hash_name,
                "markets": [market.value for market in markets],
                "currency": currency.value,
                **({"max_age": max_age} if max_age is not None else {}),
            },
        )
        r.raise_for_status()
        return ListingsLatestAggregated(**r.json())

    async def get_listings_history_aggregated(
        self,
        market_hash_name: str,
        markets: list[Market],
        currency: Currency = Currency.USD,
        max_age: str | None = None,
    ) -> ListingsHistoryAggregated:
        r = await self.client.get(
            "/v1/listings/history/aggregate",
            params={
                "market_hash_name": market_hash_name,
                "markets": [market.value for market in markets],
                "currency": currency.value,
                **({"max_age": max_age} if max_age is not None else {}),
            },
        )
        r.raise_for_status()
        return ListingsHistoryAggregated(items=r.json())

    async def get_sales_latest_aggregated(
        self,
        market_hash_name: str,
        markets: list[Market],
        currency: Currency = Currency.USD,
    ) -> SalesLatestAggregated:
        r = await self.client.get(
            "/v1/sales/latest/aggregate",
            params={
                "market_hash_name": market_hash_name,
                "markets": [market.value for market in markets],
                "currency": currency.value,
            },
        )
        r.raise_for_status()
        return SalesLatestAggregated(**r.json())

    async def get_sales_history_aggregated(
        self,
        market_hash_name: str,
        markets: list[Market],
        start: str | None = None,
        end: str | None = None,
        currency: Currency = Currency.USD,
    ) -> SalesHistoryAggregated:
        r = await self.client.get(
            "/v1/sales/history/aggregate",
            params={
                "market_hash_name": market_hash_name,
                "markets": [market.value for market in markets],
                **({"start": start} if start is not None else {}),
                **({"end": end} if end is not None else {}),
                "currency": currency.value,
            },
        )
        r.raise_for_status()

        return SalesHistoryAggregated(items=r.json())

    async def get_items(self) -> Items:
        r = await self.client.get("/v1/items")
        r.raise_for_status()
        return Items(items=r.json())

    async def get_currency_rates(self) -> CurrencyRates:
        r = await self.client.get("/v1/currency_rates")
        r.raise_for_status()
        return CurrencyRates(items=r.json())

    async def get_player_counts_latest(self) -> PlayerCountsLatest:
        r = await self.client.get("/v1/player_counts/latest")
        r.raise_for_status()
        return PlayerCountsLatest(**r.json())

    async def get_player_counts_history(
        self,
        start: str | None = None,
        end: str | None = None,
    ) -> PlayerCountsHistory:
        r = await self.client.get(
            "/v1/player_counts/history",
            params={
                **({"start": start} if start is not None else {}),
                **({"end": end} if end is not None else {}),
            },
        )
        r.raise_for_status()
        return PlayerCountsHistory(items=r.json())

    async def get_steam_profile(self, steam_id: str) -> SteamProfile:
        r = await self.client.get(
            "/v1/steam/profile",
            params={
                "steam_id": steam_id,
            },
        )
        r.raise_for_status()
        return SteamProfile(data=r.json())

    async def get_steam_inventory(self, steam_id: str) -> SteamInventory:
        r = await self.client.get(
            "/v1/steam/inventory",
            params={
                "steam_id": steam_id,
            },
        )
        r.raise_for_status()
        return SteamInventory(**r.json())

    async def get_steam_friendslist(self, steam_id: str) -> SteamFriendslist:
        r = await self.client.get(
            "/v1/steam/friendslist",
            params={
                "steam_id": steam_id,
            },
        )
        r.raise_for_status()
        return SteamFriendslist(data=r.json())

    async def get_float_info(self, inspect_link: str) -> FloatInfo:
        r = await self.client.get(
            "/v1/float",
            params={
                "inspect_link": inspect_link,
            },
        )
        r.raise_for_status()
        return FloatInfo(**r.json())
