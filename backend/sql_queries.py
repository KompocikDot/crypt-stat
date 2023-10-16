SELECT_CRYPTO_DATA = (
    "SELECT id, volume, price, cc.name, cc.code FROM historical_data hd"
    "INNER JOIN cryptocurrencies cc ON cc.id = hd.cryptocurrency_id "
    "INNER JOIN currencies c ON c.id = hd.currency_id"
    "WHERE cc.short_name IN $1"
)

SELECT_CURRENCIES_CODES = "SELECT name FROM currencies WHERE `short_name` in $1"
