-- CREATE extension IF NOT EXISTS pgcrypto;
-- alter extension pgcrypto set schema public;

-- currency table of the supported currency rates to base dollar
-- 'currency_value' is the value relative to American dollar.
-- all calculations in are done in dollar.
CREATE TABLE IF NOT EXISTS currency (
       id SERIAL PRIMARY KEY NOT NULL,
       currency_name varchar(10) UNIQUE NOT NULL,
       currency_value float NOT NULL
);
-- 'client' table is the graph of the whole network of users
-- 'contact_name' is the name of the contact, and can be null for anonymous contacts
-- 'contact_email' user's email
-- 'client_join_dt' the timestamp at which the client joined the network
-- currency_id default currency used for specific user
-- TODO add email, country, address, etc
CREATE TABLE IF NOT EXISTS clients (
       client_id SERIAL PRIMARY KEY,
       client_name text NOT NULL,
       client_email text UNIQUE NOT NULL,
       client_join_dt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
       currency_id int REFERENCES currency(id) NOT NULL
);
-- 'banking' table is for capturing the banking information necessary for transaction,
-- and wire transaction, but for simplicity, only a single id is used in transaction,
-- 'id' is analogous to credit card UUID
-- 'client_id' cross referenced client id
-- 'balance' is the user's balance
-- 'balance_dt' is the datetime of the last update of the account balance
-- note that both (balance, balance_dt) gets updated with every transaction for that client
-- TODO is the bank_number, and bank_name unique globally
-- 'balance' note that the balance is saved in the bank account preference, such that the bank assign this value, not the user, but the client can choose to retrieve data in any value,.
-- 'currency_id' is fixed, doesn't change.
CREATE TABLE IF NOT EXISTS banking (
       id SERIAL PRIMARY KEY,
       client_id int REFERENCES clients (client_id),
       balance float NOT NULL,
       balance_dt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
       bank_name text NOT NULL,
       branch_number int NOT NULL,
       account_number bigint NOT NULL,
       name_reference text,
       currency_id int REFERENCES currency(id) NOT NULL
);

-- 'passcode' is the hash of the password for authentication is done with name/email and pass-code
-- 'cred_id' cred_id is an extra id, for example public key for encrypted communication, user create this key locally (in case of public-key encryption), or receive it from the server upon registering, or login in new application install (in single key encryption), also used as session secret key, as well as the transaction key, although this key will be exposed in the ledger, but it never used in authentication, in case of compromised server, the attacker will still need to authenticate with valid username/password combination in order to get the credid. finally it can be extracted as hash of the user email. the following case might  be insecure, for large numbers of known email/credid=hash(email) combination a moderate hash function can be reversed, if the attacker compromised the server, reading the hash tables of the password, with the known hash reverse (cracked), the attacker will get a hold of the password hashs! this can be easily solved by using different hash methods for each case. since this identifier still isn't determined, it's better to be assigned to be random number(as general as possible) for now.
CREATE TABLE IF NOT EXISTS credentials (
       id  int REFERENCES clients (client_id),
       passcode text UNIQUE NOT NULL,
       cred_id text UNIQUE NOT NULL
);
-- not that this has changed, trx_dest, trx_src now refers to the credentials(cred_id)
-- 'trx_cost' is the transaction amount
-- 'trx_cur_id' is the cross reference with the currency id of the trx_cost
-- 'trx name' is the transaction description.
CREATE TABLE IF NOT EXISTS ledger (
       id SERIAL PRIMARY KEY,
       trx_dest text REFERENCES credentials(cred_id),
       trx_src text REFERENCES credentials(cred_id),
       trx_cost int NOT NULL,
--       good_id int REFERENCES goods(id),
       trx_dt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
       trx_cur_id int REFERENCES currency(id) NOT NULL,
       trx_name text
);
--CREATE  INDEX IF NOT EXISTS contacts_id_name ON contacts (contact_name);

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

--CREATE TABLE IF NOT EXISTS owners (
--owner_id int REFERENCES clients (id),
--good_id int REFERENCES goods (id),
--UNIQUE(owner_id, good_id)
--);

--CREATE TABLE IF NOT EXISTS chat (
--sender_id int REFERENCES clients(id),
--recipient_id int REFERENCES clients(id),
--dt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
--message text NOT NULL,
--UNIQUE(dt, sender_id, recipient_id)
--);
