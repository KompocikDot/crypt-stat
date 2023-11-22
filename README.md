# CRYPT-STAT

## What's crypt stat?
- That's a simple webapp with worker which stores cryptocurrencies prices and other data into postgres

> What do you require to use?
> - Just python 3.10+ and postgresql database **OR** docker (with compose)

## Usage

> Web gui mode
1. Run `docker-compose build` and `docker-compose up` (if you don't have postgresql running already)
2. Create .env file inside `./backend` folder and create `DB_URL` variable with url to the postgresql
3. Add `POSTGRES_PASSWORD, POSTGRES_USER, POSTGRES_DB and POSTGRES_HOST` variables in .env
6. run `python3 main.py`

> Cli mode
1. Run `docker-compose build` and `docker-compose up` (if you don't have postgresql running already)
2. Create .env file inside `./backend` folder and create `DB_URL` variable with url to the postgresql
3. Add `POSTGRES_PASSWORD, POSTGRES_USER, POSTGRES_DB and POSTGRES_HOST` variables in .env
4. run ```python3 main.py --cli--currencies <currency_code> <crypto_code> --dates <date_from> <date_until> --chart-type <type>```

## Cli flags:
`-- currencies` - takes two args - `<currency_code> - eg. USD` and `<crypto_code> - eg. BTC`

`-- dates` - takes two args - `<date_from> and <date_until> - iso format date - eg. 2023-10-23`

`--chart-type` - takes one arg - `<type>` - choice from `price, market_cap, market_cap_dominance`


## Demo
![How CRYPT-STAT works](https://github.com/KompocikDot/crypt-stat/assets/58148956/c092fca3-bfdb-42b7-ab6c-1a76c5560600)
