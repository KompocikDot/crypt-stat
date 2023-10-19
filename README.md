# CRYPT-STAT

## What's crypt stat?
- That's a simple webapp with worker which stores cryptocurrencies prices and other data into postgres

> What do you require to use?
> - Just python 3.10+ and postgresql database **OR** docker (with compose)

## Usage
1. `cd` into `./backend` folder
2. run `docker-compose build` and `docker-compose up` (if you don't have postgresql running already)
3. create .env file inside `./backend` folder and create `DB_URL` variable with url to the postgresql
4. **IF USING docker**: add `POSTGRES_PASSWORD, POSTGRES_USER, POSTGRES_DB and POSTGRES_HOST` variables in .env
5. run `python3 main.py`

![How CRYPT-STAT works](https://github.com/KompocikDot/crypt-stat/assets/58148956/c092fca3-bfdb-42b7-ab6c-1a76c5560600)
