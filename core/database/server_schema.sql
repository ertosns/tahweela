-- currency table relative to dollar
-- 'currency_value' is the value relative to American dollar.
-- all calculations in the are done in dollar.
CREATE TABLE IF NOT EXISTS currency (
id SERIAL PRIMARY KEY,
currency_name varchar(10) UNIQUE NOT NULL,
currency_value float NOT NULL
);

-- 'client' table is the graph of the whole network of users
-- 'contact_name' is the name of the contact, and can be null for anonymous contacts
-- 'client_join_dt' the timestamp at which the client joined the network
-- TODO add email, country, address, etc
CREATE TABLE IF NOT EXISTS clients (
       id SERIAL PRIMARY KEY,
       contact_name varchar(15),
       client_join_dt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

--CREATE  INDEX IF NOT EXISTS contacts_id_name ON contacts (contact_name);

-- credit card

-- market is a goods, and owners, and customers.
-- cost is the corresponding cost for product with 100% quality (new product)
-- TODO (UPDATE) for simplicity goods are assumed to be of single quantity 1,
-- such that goods are assigned from one owner to another after each transaction
-- for simplicity we assume that all goods are available for trade
CREATE TABLE IF NOT EXISTS goods (
       id SERIAL PRIMARY KEY,
       good_name varchar(15) NOT NULL,
       good_quality float NOT NULL,
       good_cost float NOT NULL,
       good_currency_id int REFERENCES currency(id)
);

CREATE TABLE IF NOT EXISTS owners (
       owner_id int REFERENCES clients (id),
       good_id int REFERENCES goods (id),
       UNIQUE(owner_id, good_id)
);

-- 'banking' table is for capturing the banking information necessary for transaction,
-- and wire transaction, but for simplicity, only a single id is used in transaction,
-- 'id' is analogous to credit card UUID
-- 'balance_dt' is the datetime of the last update of the account balance
-- note that both (balance, balance_dt) gets updated with every transaction for that client
CREATE TABLE IF NOT EXISTS banking (
       id SERIAL PRIMARY KEY,
       client_id int REFERENCES clients (id),
       balance float,
       balance_dt timestamp UNIQUE NOT NULL,
       UNIQUE(client_id)
);

CREATE TABLE IF NOT EXISTS ledger (
       id SERIAL PRIMARY KEY,
       trx_dest int REFERENCES banking(id),
       trx_src int REFERENCES banking(id),
       good_id int REFERENCES goods(id),
       trx_dt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
       UNIQUE(trx_dest, trx_src, trx_dt)
);

CREATE TABLE IF NOT EXISTS credentials (
       id  int REFERENCES clients (id),
       passcode VARCHAR(9) UNIQUE NOT NULL,
       cred_id bigint UNIQUE NOT NULL
);