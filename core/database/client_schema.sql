-- currency table relative to dollar
-- 'currency_value' is the value relative to American dollar.
-- all calculations in the are done in dollar.
CREATE TABLE IF NOT EXISTS currency (
id SERIAL PRIMARY KEY,
currency_name varchar(10) UNIQUE NOT NULL,
currency_value float NOT NULL
);

-- 'contacts' table is records of connections
-- 'contact_id' is the corresponding id in server's clients credential (cred_id)
-- 'bank_account_id' is the corresponding server's banking (id)
-- the first contact is expected to be the client contacts info, and credentials
CREATE TABLE IF NOT EXISTS contacts (
       contact_id  bigint UNIQUE NOT NULL,
       contact_name varchar(15),
       bank_account_id int UNIQUE NOT NULL,
       UNIQUE(contact_id, bank_account_id)
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


CREATE TABLE IF NOT EXISTS ledger (
       id SERIAL PRIMARY KEY,
       trx_dest int REFERENCES contacts(bank_account_id),
       trx_src int REFERENCES contacts(bank_account_id),
       good_id int REFERENCES goods(id),
       trx_dt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
       UNIQUE (trx_dest, trx_src, trx_dt)
);

--- this table includes a single credential row for the registered client
CREATE TABLE IF NOT EXISTS credentials (
       id SERIAL PRIMARY KEY,
       passcode VARCHAR(15) UNIQUE NOT NULL,
       cred_id bigint UNIQUE NOT NULL
);
