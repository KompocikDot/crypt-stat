import asyncio
import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from exceptions import MissingApiKeyException
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from input import FormInput
from worker import Worker

load_dotenv(".env")


@asynccontextmanager
async def lifespan(_: FastAPI):
    api_key = os.getenv("COINMARKETCAP_API_KEY")
    if not api_key:
        raise MissingApiKeyException

    api_worker = Worker(api_key=api_key, worker_delay=360)
    asyncio.create_task(api_worker.run())
    yield


app = FastAPI(title="CRYPT-STAT", lifespan=lifespan)


@app.get("/")
async def read_index():
    return FileResponse("./assets/index.html")


@app.post("/")
async def get_plot(payload: FormInput):
    return HTMLResponse(f"<div> {payload.cryptocurrencies} </div>")


if __name__ == "__main__":
    uvicorn.run(app)


# TODO: Wczytanie danych z API
# TODO: Zapis do bazy (w razie potrzeby)
# TODO: Obróbka danych na podstawie requesta
# TODO: Zwrot danych (obrobionych) w formie html z wykresem(svg)
# TODO: Powtórz
# TODO: Dodaj docsy + testy
