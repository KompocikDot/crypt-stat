CREATE TABLE currencies(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY NOT NULL,
    symbol VARCHAR(255),
    name VARCHAR(255)
);


CREATE TABLE cryptocurrencies(
    id INT GENERATED ALWAYS AS IDENTITY  PRIMARY KEY NOT NULL,
    symbol VARCHAR(255),
    name VARCHAR(255)
);

CREATE TABLE historical_data(
    id INT  GENERATED ALWAYS AS IDENTITY  PRIMARY KEY NOT NULL,

    price NUMERIC(30, 15),
    volume_24h NUMERIC(30, 15),
    volume_change_24h NUMERIC(30, 15),
    percent_change_1h NUMERIC(30, 15),
    percent_change_24h NUMERIC(30, 15),
    percent_change_7d NUMERIC(30, 15),
    percent_change_30d NUMERIC(30, 15),
    percent_change_60d NUMERIC(30, 15),
    percent_change_90d NUMERIC(30, 15),
    market_cap NUMERIC(30, 15),
    market_cap_dominance NUMERIC(30, 15),
    last_updated TIMESTAMP,

    cryptocurrency_id INT REFERENCES cryptocurrencies(id) NOT NULL,
    currency_id INT REFERENCES currencies(id) NOT NULL
);


INSERT INTO currencies (symbol, name)
VALUES
('USD', 'United States Dollar'),
('AUD', 'Australian Dollar'),
('CAD', 'Canadian Dollar'),
('CHF', 'Swiss Franc'),
('CNY', 'Chinese Yuan'),
('EUR', 'Euro'),
('GBP', 'Pound Sterling'),
('JPY', 'Japanese Yen'),
('PLN', 'Polish Złoty'),
('RUB', 'Russian Ruble'),
('AED', 'United Arab Emirates Dirham');

INSERT INTO cryptocurrencies (symbol, name) VALUES
('BTC', 'Bitcoin'),
('ETH', 'Ethereum'),
('USDT', 'Tether USDt'),
('BNB', 'BNB'),
('XRP', 'XRP'),
('USDC', 'USDC'),
('SOL', 'Solana'),
('ADA', 'Cardano'),
('DOGE', 'Dogecoin'),
('TRX', 'TRON');
