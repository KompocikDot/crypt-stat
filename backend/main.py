import os

from dotenv import load_dotenv

from worker import Worker

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn

load_dotenv("../.env")

@asynccontextmanager
async def lifespan(_: FastAPI):
    api_worker = Worker(api_key=os.getenv("COINMARKETCAP_API_KEY"), worker_delay=60)
    await api_worker.run()
    yield


app = FastAPI(title="CRYPT-STAT", lifespan=lifespan)


@app.get("/")
async def read_index():
    return FileResponse("./assets/index.html")


@app.post("/")
async def get_plot():
    ...


if __name__ == '__main__':
    uvicorn.run(app)


# TODO: Wczytanie danych z API
# TODO: Zapis do bazy (w razie potrzeby)
# TODO: Obróbka danych na podstawie requesta
# TODO: Zwrot danych (obrobionych) w formie html z wykresem(svg)
# TODO: Powtórz
