from httpx import AsyncClient
import asyncio


class Worker:
    CURRENCIES_CODES = ["USD", "EUR", "EUR", "PLN", "JPY", "GBP"]
    CRYPTO_CODES = crypto_list = [
        "BTC",  # Bitcoin
        "ETH",  # Ethereum
        "BNB",  # Binance Coin
        "XRP",  # Ripple
        "ADA",  # Cardano
        "DOGE",  # Dogecoin
        "SOL",  # Solana
        "DOT",  # Polkadot
        "LTC",  # Litecoin
        "LINK"  # Chainlink
    ]

    API_URL = ""

    def __init__(self, api_key: str, worker_delay: int) -> None:
        self.__api_key = api_key
        self._worker_delay = worker_delay

    async def run(self) -> None:
        async with AsyncClient() as client:
            while True:
                data = self._scrape_data(client)
                exists_in_db = self.check_in_db(data)
                if not exists_in_db:
                    self.insert_to_db(data)

                await asyncio.sleep(self._worker_delay)

    async def _scrape_data(self, client: AsyncClient) -> dict:
        while True:
            resp = await client.get(self.API_URL)