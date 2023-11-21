import argparse
from datetime import date

import uvicorn

from backend.cli import run_cli
from backend.input import FormInput
from backend.webapp import app

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

        run_cli(payload=payload)
    else:
        uvicorn.run(app)
