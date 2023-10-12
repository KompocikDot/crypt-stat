import asyncio

from httpx import AsyncClient


class Worker:
    CURRENCIES_CODES = ["USD", "EUR", "EUR", "PLN", "JPY", "GBP"]
    CRYPTO_CODES = [
        "BTC",  # Bitcoin
        "ETH",  # Ethereum
        "BNB",  # Binance Coin
        "XRP",  # Ripple
        "ADA",  # Cardano
        "DOGE",  # Dogecoin
        "SOL",  # Solana
        "DOT",  # Polkadot
        "LTC",  # Litecoin
        "LINK",  # Chainlink
    ]

    API_URL = "https://web-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"

    def __init__(self, api_key: str, worker_delay: int) -> None:
        self.__api_key = api_key
        self._worker_delay = worker_delay

    async def run(self) -> None:
        async with AsyncClient() as client:
            while True:
                data = await self.__scrape_data(client)
                exists_in_db = await self.__check_in_db(data)
                if not exists_in_db:
                    await self.__insert_to_db(data)

                await asyncio.sleep(self._worker_delay)

    async def __scrape_data(self, client: AsyncClient) -> dict:
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "deflate, gzip",
            "Content-Type": "application/json",
            "X-CMC_PRO_API_KEY": self.__api_key,
        }

        resp = await client.get(self.API_URL, headers=headers)
        return resp.json()

    async def __check_in_db(self, data):
        ...

    async def __insert_to_db(self, data):
        ...
