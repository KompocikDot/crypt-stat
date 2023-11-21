import asyncio

from .input import FormInput
from .webapp import create_plot, run_background_worker


async def run_in_asyncio_loop(payload: FormInput) -> None:
    await asyncio.gather(
        run_background_worker(), create_plot(payload=payload, cli=True)
    )


def run_cli(payload: FormInput) -> None:
    asyncio.run(run_in_asyncio_loop(payload=payload))
