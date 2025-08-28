import os

import dotenv
import pytest

from csmarketapi import CSMarketAPI
from csmarketapi.enums import Market


@pytest.fixture(scope="module")
def env():
    env_loaded = False
    if not env_loaded:
        try:
            dotenv.load_dotenv()
            env_loaded = True
        except Exception:
            pass
    yield True


@pytest.mark.asyncio
async def test_get_listings_latest_aggregated(env):

    async with CSMarketAPI(os.getenv("API_KEY")) as client:

        assert (
            await client.get_listings_latest_aggregated(
                market_hash_name=os.getenv("MARKET_HASH_NAME"), markets=list(Market)
            )
        ).listings is not None


@pytest.mark.asyncio
async def test_get_listings_history_aggregated(env):
    async with CSMarketAPI(os.getenv("API_KEY")) as client:

        assert (
            await client.get_listings_history_aggregated(
                market_hash_name=os.getenv("MARKET_HASH_NAME"), markets=list(Market)
            )
        ).items is not None


@pytest.mark.asyncio
async def test_get_sales_latest_aggregated(env):
    async with CSMarketAPI(os.getenv("API_KEY")) as client:

        assert (
            await client.get_sales_latest_aggregated(
                market_hash_name=os.getenv("MARKET_HASH_NAME"), markets=list(Market)
            )
        ).sales is not None


@pytest.mark.asyncio
async def test_get_sales_history_aggregated(env):
    async with CSMarketAPI(os.getenv("API_KEY")) as client:

        assert (
            await client.get_sales_history_aggregated(
                market_hash_name=os.getenv("MARKET_HASH_NAME"), markets=list(Market)
            )
        ).items is not None


@pytest.mark.asyncio
async def test_get_items(env):
    async with CSMarketAPI(os.getenv("API_KEY")) as client:

        assert (await client.get_items()).items is not None


@pytest.mark.asyncio
async def test_get_currency_rates(env):
    async with CSMarketAPI(os.getenv("API_KEY")) as client:

        assert (await client.get_currency_rates()).items is not None


@pytest.mark.asyncio
async def test_get_player_counts_latest(env):
    async with CSMarketAPI(os.getenv("API_KEY")) as client:

        assert (await client.get_player_counts_latest()).count is not None


@pytest.mark.asyncio
async def test_get_player_counts_history(env):
    async with CSMarketAPI(os.getenv("API_KEY")) as client:

        assert (await client.get_player_counts_history()).items is not None


@pytest.mark.asyncio
async def test_get_steam_profile(env):
    async with CSMarketAPI(os.getenv("API_KEY")) as client:

        assert (
            await client.get_steam_profile(steam_id=os.getenv("STEAM_ID"))
        ).data is not None


@pytest.mark.asyncio
async def test_get_steam_inventory(env):
    async with CSMarketAPI(os.getenv("API_KEY")) as client:

        assert (
            await client.get_steam_inventory(steam_id=os.getenv("STEAM_ID"))
        ).steamid is not None


@pytest.mark.asyncio
async def test_get_steam_friendslist(env):
    async with CSMarketAPI(os.getenv("API_KEY")) as client:

        assert (
            await client.get_steam_friendslist(steam_id=os.getenv("STEAM_ID"))
        ).data is not None


@pytest.mark.asyncio
async def test_get_float_info(env):
    async with CSMarketAPI(os.getenv("API_KEY")) as client:

        await client.get_float_info(inspect_link=os.getenv("INSPECT_LINK"))
