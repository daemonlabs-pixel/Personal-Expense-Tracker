 BEGIN;
 CREATE TABLE IF NOT EXISTS categories(
    id INTEGER PRIMARY KEY,
    name TEXT COLLATE NOCASE UNIQUE NOT NULL

);

CREATE TABLE IF NOT EXISTS transactions(
    id INTEGER PRIMARY KEY,
    amount INTEGER  NOT NULL CHECK(amount>0) ,
    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('expense','income')) ,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    description TEXT,
    date TEXT NOT NULL CHECK(date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
    currency_code TEXT NOT NULL CHECK(currency_code IN('XOF','EUR','USD') )
);

COMMIT;
