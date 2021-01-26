-- currency table relative to dollar
-- 'currency_value' is the value relative to American dollar.
-- all calculations in the are done in dollar.
CREATE TABLE IF NOT EXISTS currency (
       id SERIAL PRIMARY KEY,
       currency_name varchar(10) UNIQUE NOT NULL,
       currency_value float NOT NULL
);

-- 'contacts' table is records of connections
-- 'contact_id' is the corresponding id in server's clients credential (cred_id), and it's used to facilitate bank transfer by contact name, rather than by email only.
-- the first contact is expected to be the client contacts info, and credentials.
CREATE TABLE IF NOT EXISTS contacts (
       contact_id  bigint UNIQUE NOT NULL,
       contact_name text NOT NULL,
       contact_email text UNIQUE NOT NULL,
       UNIQUE(contact_id, contact_email)
);

--- this table includes a single credential row for the registered client
--- cred_id is  big integer added for securing the authentication
CREATE TABLE IF NOT EXISTS credentials (
       id SERIAL PRIMARY KEY,
       passcode text UNIQUE NOT NULL,
       cred_id bigint UNIQUE NOT NULL
);


-- trx_dest is recipient credential id
-- trx_src is the sender credential id
CREATE TABLE IF NOT EXISTS ledger (
       id SERIAL PRIMARY KEY,
       trx_dest bigint,
       trx_src bigint,
       trx_cost int NOT NULL,
--       good_id int REFERENCES goods(id),
       trx_dt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- CREATE  INDEX IF NOT EXISTS contacts_id_name ON contacts (contact_name);
-- credit card
-- market is a goods, and owners, and customers.
-- cost is the corresponding cost for product with 100% quality (new product)
-- TODO (UPDATE) for simplicity goods are assumed to be of single quantity 1,
-- such that goods are assigned from one owner to another after each transaction
-- for simplicity we assume that all goods are available for trade
--CREATE TABLE IF NOT EXISTS goods (
--id SERIAL PRIMARY KEY,
--good_name varchar(15) NOT NULL,
--good_quality float NOT NULL,
--good_cost float NOT NULL,
--good_currency_id int REFERENCES currency(id)
--);

--CREATE TABLE IF NOT EXISTS chat (
--sender_id int REFERENCES contacts(contact_id),
--recipient_id int REFERENCES contacts(contact_id),
--dt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
--message text NOT NULL,
--UNIQUE(dt, sender_id, recipient_id)
--);
