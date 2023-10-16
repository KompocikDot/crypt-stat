import asyncio
from contextlib import asynccontextmanager

import uvicorn
from asyncpg import Pool
from crypto import CryptoResult
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from input import FormInput
from utils import get_db_pool
from worker import Worker

load_dotenv()


@asynccontextmanager
async def lifespan(_: FastAPI):
    api_worker = Worker(worker_delay=20)
    asyncio.create_task(api_worker.run())
    yield


app = FastAPI(title="CRYPT-STAT", lifespan=lifespan)


@app.get("/")
async def read_index():
    return FileResponse("./assets/index.html")


@app.post("/")
async def get_plot(payload: FormInput, db_pool: Pool = Depends(get_db_pool)):
    res = CryptoResult(payload=payload, db_pool=db_pool)
    plot = await res.generate_plot()

    return HTMLResponse(f"<div>{plot}</div>")


if __name__ == "__main__":
    uvicorn.run(app)


# TODO: Wczytanie danych z API
# TODO: Zapis do bazy (w razie potrzeby)
# TODO: Obróbka danych na podstawie requesta
# TODO: Zwrot danych (obrobionych) w formie html z wykresem(svg)
# TODO: Powtórz
# TODO: Dodaj docsy + testy
