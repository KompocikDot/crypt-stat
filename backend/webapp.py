import logging
import os

from asyncpg import Pool, create_pool
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi_utils.tasks import repeat_every

from .crypto import CryptoResult
from .input import FormInput
from .worker import Worker

GET_PLOT_BAD_REQUEST_RESP = (
    '<div class="ml-2">"date until" value cannot be '
    'earlier than "date from" value, try again</div>'
)

load_dotenv()

app = FastAPI(title="CRYPT-STAT")


@app.on_event("startup")
@repeat_every(seconds=10, raise_exceptions=True)
async def run_background_worker() -> None:
    if not hasattr(app.state, "db"):
        try:
            app.state.db = await create_pool(os.getenv("DB_URL"))
        except OSError:
            logging.exception("Could not connect to db - it's most likely down")

    worker = Worker(db_pool=app.state.db)
    await worker.run()


@app.get("/")
async def read_index() -> FileResponse:
    return FileResponse("./backend/assets/index.html")


@app.post("/get-plot/")
async def get_plot(payload: FormInput, request: Request) -> HTMLResponse:
    if payload.date_until < payload.date_from:
        return HTMLResponse(GET_PLOT_BAD_REQUEST_RESP)

    plot = await create_plot(payload, db=request.app.state.db)
    return HTMLResponse(plot)


async def create_plot(
    payload: FormInput, db: Pool | None = None, cli: bool = False
) -> str | None:
    if cli:
        db = await create_pool(os.getenv("DB_URL"))
    res = CryptoResult(payload=payload, db_pool=db)
    plot = await res.generate_plot(cli)
    return plot


app.mount("/static/", StaticFiles(directory="./backend/assets"), name="static")
