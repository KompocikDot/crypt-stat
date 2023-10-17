import os

import uvicorn
from asyncpg import create_pool
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
@repeat_every(seconds=20)
async def run_background_worker() -> None:
    if not hasattr(app.state, "db"):
        app.state.db = await create_pool(os.getenv("DB_URL"))

    worker = Worker(db_pool=app.state.db)
    await worker.run()


@app.get("/")
async def read_index():
    return FileResponse("./assets/index.html")


@app.post("/get-plot/")
async def get_plot(payload: FormInput, request: Request):
    if payload.date_until < payload.date_from:
        return HTMLResponse(
            "<div>date until cannot be earlier than date from, try again</div>"
        )
    res = CryptoResult(payload=payload, db_pool=request.app.state.db)
    plot = await res.generate_plot()

    return HTMLResponse(plot)


app.mount("/static/", StaticFiles(directory="./assets"), name="static")

if __name__ == "__main__":
    uvicorn.run(app)
