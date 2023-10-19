SELECT_CRYPTO_DATA_QUERY = (
    "SELECT price, market_cap, market_cap_dominance, last_updated, "
    "cryptocurrency_id, currency_id, cc.id as cryptocurrency_id, c.id as currency_id "
    "FROM historical_data AS hd "
    "INNER JOIN cryptocurrencies AS cc ON cc.id = hd.cryptocurrency_id "
    "INNER JOIN currencies AS c ON c.id = hd.currency_id "
    "WHERE cc.symbol = $1 AND c.symbol = $2 AND last_updated BETWEEN $3 AND $4 "
    "ORDER BY last_updated"
)

SELECT_CURRENCIES_CODES_QUERY = "SELECT name FROM currencies WHERE short_name in $1"

HISTORICAL_DATA_EXISTS_QUERY = (
    "SELECT 1 FROM historical_data WHERE currency_id = $1 "
    "AND cryptocurrency_id = $2 AND last_updated = $3"
)


INSERT_HISTORICAL_DATA_QUERY = (
    "INSERT INTO historical_data(price, market_cap, "
    "market_cap_dominance, last_updated, cryptocurrency_id, currency_id"
    ") VALUES ($1, $2, $3, $4, $5, $6)"
)


SELECT_CRYPTOCURRENCIES_QUERY = "SELECT symbol, id FROM cryptocurrencies"

SELECT_CURRENCIES_QUERY = "SELECT symbol, id FROM currencies"
