import argparse
import asyncio
import os
from datetime import date

import uvicorn
from asyncpg import Pool, create_pool
from crypto import CryptoResult
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi_utils.tasks import repeat_every
from input import FormInput
from worker import Worker

load_dotenv()


app = FastAPI(title="CRYPT-STAT")


@app.on_event("startup")
@repeat_every(seconds=10)
async def run_background_worker() -> None:
    if not hasattr(app.state, "db"):
        app.state.db = await create_pool(os.getenv("DB_URL"))

    worker = Worker(db_pool=app.state.db)
    await worker.run()


@app.get("/")
async def read_index() -> FileResponse:
    return FileResponse("./assets/index.html")


@app.post("/get-plot/")
async def get_plot(payload: FormInput, request: Request) -> HTMLResponse:
    if payload.date_until < payload.date_from:
        return HTMLResponse(
            '<div class="ml-2">"date until" value cannot be '
            'earlier than "date from" value, try again</div>'
        )

    plot = await create_plot(payload, db=request.app.state.db)
    return HTMLResponse(plot)


async def create_plot(payload: FormInput, db: Pool | None = None, cli: bool = False):
    if cli:
        db = await create_pool(os.getenv("DB_URL"))
    res = CryptoResult(payload=payload, db_pool=db)
    return await res.generate_plot(cli)


async def run_cli(payload: FormInput) -> None:
    await asyncio.gather(
        run_background_worker(), create_plot(payload=payload, cli=True)
    )


app.mount("/static/", StaticFiles(directory="./assets"), name="static")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", action="store_true")
    parser.add_argument("--currencies", nargs=2, type=str)
    parser.add_argument("--dates", nargs=2, type=lambda val: date.fromisoformat(val))
    parser.add_argument("--chart-type", type=str)

    args = parser.parse_args()
    if args.cli:
        payload = FormInput(
            currency=args.currencies[0],
            cryptocurrency=args.currencies[1],
            date_from=args.dates[0],
            date_until=args.dates[1],
            data_type=args.chart_type,
        )

        asyncio.run(run_cli(payload=payload))
    else:
        uvicorn.run(app)
