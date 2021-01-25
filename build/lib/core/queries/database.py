import psycopg2
import logging
import psycopg2
from psycopg2 import sql
import pandas as pd
import datetime as dt
import random as rand
import string
from core.utils import CONTACTS_URL, GOODS_URL, REGISTER_URL, LEDGER_URL, PURCHASE_URL, BALANCE_URL, MAX_GOODS, MAX_COST, STOCHASTIC_TRADE_THRESHOLD, MAX_CRED_ID, TIMESTAMP_FORMAT

class exists(object):
    def __init__(self, conn, cur):
        self.conn=conn
        self.cur=cur
    def account_exists(self, cid):
        """verify that a banking account with the given client id is available (CALLED AT THE SERVER SIDE)

        @param cid: client id
        @return boolean wither the banking account for give client exists or note
        """
        stat=sql.SQL("SELECT EXISTS (SELECT 1 FROM banking WHERE client_id={cid});").\
            format(cid=sql.Literal(cid))
        self.cur.execute(stat)
        return self.cur.fetchone()[0]
    def client_exists(self, cid):
        """verify that  a client with given id is available (CALLED AT THE SERVER SIDE)

        @param cid: client id
        @return boolean wither the client exists or note
        """
        stat=sql.SQL("SELECT EXISTS (SELECT 1 FROM clients WHERE id={cid});").\
            format(cid=sql.Literal(cid))
        self.cur.execute(stat)
        return self.cur.fetchone()[0]
    def contact_exists(self, cid):
        """verify that a contact with given id is available (CALLED AT THE CLIENT SIDE)

        @param cid: contact id
        @return boolean wither the contact exists or note
        """
        stat=sql.SQL("SELECT EXISTS (SELECT 1 FROM contacts WHERE contact_id={cid});").\
            format(cid=sql.Literal(cid))
        self.cur.execute(stat)
        return self.cur.fetchone()[0]
    def credential_exists(self, cid):
        """ verify the credential for the client with given cid(CALLED FROM SERVER SIDE),
        or get the single row for client with cid=1 (CALLED FROM CLIENT SIDE)

        @param cid: client id, or 1 (in case of call from client side for it's own credential)
        @return boolean for wither the client (with given cid) is registered or not
        """
        stat=sql.SQL("SELECT EXISTS (SELECT 1 FROM credentials WHERE id={cid})").\
            format(cid=sql.Literal(cid))
        self.cur.execute(stat)
        return self.cur.fetchone()[0]
    def exists(self, gid):
        """verify that a good with given id is available

        @param gid: good id
        @return boolean wither the good exists or note
        """
        stat=sql.SQL("SELECT EXISTS (SELECT 1 FROM goods WHERE id={gid});").format(gid=sql.Literal(gid))
        self.cur.execute(stat)
        return self.cur.fetchone()[0]

class gets(object):
    def __init__(self, conn, cur, logger):
        self.conn=conn
        self.cur=cur
        self.db_log=logger
    def get_client_id(self, bid):
        """ retrieve the corresponding client_id of the given banking_id (bid) (called at the server side)

        @param bid: banking id
        @return cid: contact id
        """
        query=sql.SQL("SELECT (client_id) FROM banking WHERE id={bid} LIMIT 1").format(bid=sql.Literal(bid))
        self.db_log.debug(query)
        return pd.read_sql(query, self.conn).ix[0]

    def get_banking_id(self, cid):
        """retrieve the corresponding banking_id of the given  client_id (cid) (called at the server side)

        @param cid: client id
        @return bid: banking id
        """
        query=sql.SQL("SELECT (id) FROM banking WHERE client_id={cid} LIMIT 1").format(cid=sql.Literal(cid))
        self.db_log.debug(query)
        return pd.read_sql(query, self.conn).ix[0]

    def get_balance_by_cid(self, cid):
        """called at the server side to retrieve the account balance d of the given client_id (cid)

        @param cid: client id
        @return bid: banking id
        """
        query=sql.SQL("SELECT (balance) FROM banking WHERE client_id={cid} LIMIT 1").format(cid=sql.Literal(cid))
        self.db_log.debug(query)
        return pd.read_sql(query, self.conn).ix[0]

    def get_balance_by_credid(self, cred_id):
        """ get balance of client with given credential id

        @param cred_id: client credential id
        """
        query=sql.SQL("SELECT (b.balance) FROM banking as b JOIN  credentials AS c ON c.id=b.client_id WHERE c.cred_id={credid} ;").format(credid=sql.Literal(cred_id))
        self.db_log.debug(query)
        self.cur.execute(query)
        fet=self.cur.fetchone()
        print("credid fet: ", fet)
        #TODO handle none! how to handle this in the transaction itself
        if fet==None:
            return 0
        return fet[0]
    def get_all_clients(self):
        """retrieve all clients info

        """
        query="SELECT * FROM clients;"
        self.db_log.debug(query)
        return pd.read_sql(query, self.conn).to_json
    def get(self, cid):
        """retrieve client into with given client id (cid)

        @param cid: client id
        @return tuple (id, name, join date)
        """
        query=sql.SQL("SELECT (id, contact_name, client_join_dt) FROM clients WHERE id={cid};").\
            format(cid=sql.Literal(cid))
        self.db_log.debug(query)
        self.cur.execute(query)
        return self.cur.fetchone()
    def get_name(self, cid):
        """retrieve client name corresponding to given client id (cid)

        @param cid: client id
        @return client name
        """
        return self.get(cid)[1]
    def get_all_contacts(self):
        query = "SELECT * FROM contacts;"
        self.db_log.debug(query)
        return pd.read_sql(query, self.conn)
    def get_banking_id(self, cid):
        """ called at the client side, to retrieve the stored banking id in the contacts

        @param cid: contact id
        @return banking_id or the associated banking id for the given contact id
        """
        query=sql.SQL("SELECT (bank_account_id) FROM contacts WHERE contact_id='{cid}' LIMIT 1;").\
            format(cid=sql.Literal(cid))
        self.db_log.debug(query)
        return pd.read_sql(query, self.conn).ix[0]
    def get_all_credentials(self):
        query = "SELECT * FROM credentials;"
        self.db_log.debug(query)
        ret = pd.read_sql(query, self.conn)
        return ret

    def get_credential(self, cid):
        """ get the credential for the client with given cid(CALLED FROM SERVER SIDE),
        or get the single row for client with cid=1 (CALLED FROM CLIENT SIDE)

        @param cid: client id, or 1 (in case of call from client side for it's own credential)
        """
        query=sql.SQL("SELECT * FROM credentials WHERE id={cid} LIMIT 1;)").\
            format(cid=sql.Literal(cid))
        self.db_log.debug(query)
        ret = pd.read_sql(query, self.conn)

    def credid2cid(self, cred_id):
        """ get client id

        @param cred_id: credential id
        @return the id, or None if doesn't exist
        """
        query=sql.SQL("SELECT id FROM credentials WHERE cred_id={credid} LIMIT 1;").\
            format(credid=sql.Literal(cred_id))
        self.db_log.debug(query)
        self.cur.execute(query)
        fet=self.cur.fetchone()
        return fet

    def get_password(self, cred_id):
        """ get user's passcode for authentication

        @param cred_id: credential id
        @return list of the id, or empty list of doesn't exist
        """
        query=sql.SQL("SELECT (passcode) FROM credentials WHERE cred_id={credid} LIMIT 1;").\
            format(credid=sql.Literal(cred_id))
        self.db_log.debug(query)
        self.cur.execute(query)
        return self.cur.fetchone()[0]

    def get_credid_with_gid(self, gid):
        """cross reference credential id, with good's id

        @param gid: good's id
        @return credential id credid
        """
        query=sql.SQL("SELECT (c.cred_id) FROM goods, credentials as c JOIN owners as o ON c.id=o.owner_id  WHERE goods.id={gid} LIMIT 1;").\
            format(gid=sql.Literal(gid))
        self.db_log.debug(query)
        self.cur.execute(query)
        fet=self.cur.fetchone()
        self.db_log.debug("fetched credid with gid: "+str(fet))
        return fet
    def to_dollar(self, cid):
        """ convert currency of the corresponding id to dollar ratio

        for example if currency A = 2 dollars, then the conversion would be 0.5,
        for another currency B = 0.5 dollar, then the conversion to dollar would be 2
        such that for given cost of xA, would be 0.5x$.
        @param cid is the id of the corresponding currency
        @return transformation ratio to dollar
        """
        query = sql.SQL("SELECT * FROM currency WHERE id=cid;").\
            format(cid=sql.Literal(cid))
        self.db_log.debug(query)
        ratio = 1.0/pd.read_sql(query, self.conn)['currency_value'].ix[0]
        return ratio
    def get_all_goods(self):
        query="SELECT * FROM goods;"
        #return pd.read_sql(query, conn, index_col='id').to_json()
        return pd.read_sql(query, self.conn).to_json()

    def get_good(self, gid):
        """retrive good for the given goods id (gid)

        @param gid: goods id
        @return pandas data series of the corresponding row
        """
        query = sql.SQL("SELECT * FROM goods WHERE id={gid};").\
            format(gid=sql.Literal(gid))
        self.db_log.debug(query)
        return pd.read_sql(query, self.conn)

    def get_commodity(self, gname, quality=0):
        """retrive good for the given goods constraints

        @param gname: goods name
        @param quality: retrieve goods with quality > given threshold
        @return pandas data frame of the corresponding constrains
        """
        query = sql.SQL("SELECT * FROM goods WHERE good_name={gname} AND good_quality>={gquality}").\
            format(gname=sql.Literal(gname), \
                   quality=sql.Literal(gquality))
        self.db_log.debug(query)
        return pd.read_sql(query, self.conn)

    def get_new_price(self, gid):
        """ get good price with given good's id

        @param gid: good's id
        @return price in dollar
        """
        df = self.get_good(gid)
        print("length: ", len(df))
        print(df)
        if len(df)==0:
            return 0
        cur_id = df.iloc[0]['good_currency_id']
        return df.iloc[0]['good_cost']*to_dollar(cur_id)
    def get_transactions(self, st_dt, end_dt=dt.datetime.now()):
        """ get the transactions within the given period exclusively

        @param st_dt: the start datetime
        @param end_dt: the end datetime
        @return dataframe of the transactions
        """
        stat = "SELECT * FROM ledger;" if st_dt==None else  sql.SQL("SELECT * FROM ledger WHERE trx_dt>{st_dt} AND trx_dt<{end_dt};").format(st_dt=sql.Literal(st_dt), end_dt=sql.Literal(end_dt))
        self.db_log.debug(stat)
        return pd.read_sql(stat, self.conn)

    def get_sells(self, dest, st_dt, end_dt=None):
        """ get sells transaction within the st_dt, end_dt period, while there destined to dest (CALLED AT SERVER SIDE)

        @param dest: the destination credential id
        @return sells transactions
        """
        trx=self.get_transactions(st_dt, end_dt)
        trx.apply(lambda x:x['trx_dest']==dest, inplace=True)
        return trx

    def get_last_timestamp(self):
        """ retrieve the timestamp of the last transaction (CALLED FROM THE CLIENT SIDE)

        @return timestamp
        """
        query="SELECT currval(pg_get_serial_sequence('ledger', 'trx_id'));"
        self.db_log.debug(query)
        self.cur.execute(query)
        return self.cur.fetchone()[0]
    def get_all_owners(self):
        query="SELECT * FROM owner;"
        return pd.read_sql(query, self.conn, index_col='id')

    def get_good_owner(self, gid):
        """return owner id (oid) for the given gid

        @param gid: good
        @return the owner id
        """
        query = sql.SQL("SELECT (owner_id) FROM owners WHERE good_id={gid}").\
            format(gid=sql.Literal(gid))
        self.db_log.debug(query)
        return pd.read_sql(query, self.conn).ix[0]

    def get_owner_goods(self, oid):
        """return the good assigned to the given owner id (oid)

        @param oid: is the owner id
        @return json dict of good's ids
        """
        query = sql.SQL("SELECT (good_id) FROM owners WHERE owner_id={oid}").\
            format(oid=sql.Literal(oid))
        self.db_log.debug(query)
        return pd.read_sql(query, self.conn).to_json()

class inserts(object):
    def __init__(self, conn, cur, logger):
        self.conn=conn
        self.cur=cur
        self.db_log=logger
    def add_account(self, cid, balance):
        """ give the client with the given id (cid) banking account (CALLED AT SERVER SIDE)

        @param cid: client id
        @param balance: client account balance
        """
        stat=sql.SQL("INSERT INTO banking (client_id, balance, balance_dt) VALUES ({cid}, {balance}, {dt});"). \
            format(cid=sql.Literal(cid), \
                   balance=sql.Literal(balance), \
                   dt=sql.Literal(dt.datetime.now().strftime(TIMESTAMP_FORMAT)))
        self.db_log.debug(stat)
        self.cur.execute(stat)
        stat="SELECT currval(pg_get_serial_sequence('banking', 'id'));"
        self.db_log.debug(stat)
        self.cur.execute(stat);
        return self.cur.fetchone()[0]
    def add_client(self, name):
        """ add new client to the network (CALLED AT THE SERVER SIDE),

        note that some clients might not have banking id yet
        @param name: client name
        """
        stat=sql.SQL("INSERT INTO clients (contact_name) VALUES ({name})").\
            format(name=sql.Literal(name))
        self.cur.execute(stat)
        self.cur.execute("SELECT currval(pg_get_serial_sequence('clients', 'id'));")
        return self.cur.fetchone()[0]
    def insert_contact(self, cid, cname, bid):
        """ insert new contact (CALLED AT THE CLIENT SIDE)

        @param cid: contact id (the same as client id in the server side)
        @param cname: contact name
        @param bid: bank account id
        """
        stat=sql.SQL("INSERT INTO contacts (contact_id, contact_name bank_account_id) VALUES ({cid}, {cname}, {bid})").\
            format(cid=sql.Literal(cid), \
                   cname=sql.Literal(cname), \
                   bid=sql.Literal(bid))
        self.db_log.debug(stat)
        self.cur.execute(stat)

    def add_cred(self, passcode, cred_id):
        """add client credentials returned from the server

        @param cid: client id
        """
        stat=sql.SQL("INSERT INTO credentials (passcode, cred_id) VALUES ({passcode}, {credid});").\
            format(passcode=sql.Literal(passcode), \
                   credid=sql.Literal(cred_id))
        self.db_log.debug(stat)
        self.cur.execute(stat)

    def register(self, cid):
        """register new client credentials with given cid (CALLED FROM SERVER SIDE)

        @param cid: client id
        @return a tuple (cred_id, passcode)
        """
        cred_id=rand.random()*MAX_CRED_ID
        passcode=''.join(rand.choice(string.ascii_uppercase+\
                                     string.ascii_lowercase+\
                                     string.digits)\
                         for _ in range(9))
        stat=sql.SQL("INSERT INTO credentials (id, passcode, cred_id) VALUES ({cid}, {passcode}, {credid});").\
            format(cid=sql.Literal(cid), \
                   passcode=sql.Literal(passcode), \
                   credid=sql.Literal(cred_id))
        self.db_log.debug(stat)
        self.cur.execute(stat)
        return (cred_id, passcode)
    def add_good(self, gname, gquality, gcost, gcid=1):
        """ INSERT new good into the goods table

        @param gname: good name
        @param gquality: good quality
        @param gcost: good cost
        @param gcid: good currency id
        """
        stat=sql.SQL("INSERT INTO goods (good_name, good_quality, good_cost, good_currency_id) VALUES ({gname}, {gquality}, {gcost}, {gcid});").\
            format(gname=sql.Literal(gname[:15]), \
                   gquality=sql.Literal(gquality), \
                   gcost=sql.Literal(gcost), \
                   gcid=sql.Literal(gcid))
        self.db_log.debug(stat)
        self.cur.execute(stat)
        stat="SELECT currval(pg_get_serial_sequence('goods', 'id'));"
        self.cur.execute(stat)
        self.db_log.debug(stat)
        return self.cur.fetchone()[0]
    def insert_trx(self, des, src, gid):
        """ insert transaction from 'src' to 'des' for good with 'gid'

        @param des: the transaction destination
        @param src: the transaction source
        @param gid: the good's id
        """
        stat=sql.SQL("INSERT INTO ledger (trx_dest, trx_src, good_id) VALUES ({des}, {src}, {gid});").\
            format(des=sql.Literal(des), \
                   src=sql.Literal(src), \
                   gid=sql.Literal(gid))
        self.db_log.debug(stat)
        self.cur.execute(stat)
    def add_owner(self, oid, gid):
        """assign ownership of owner with id (oid) to the good with id (gid)

        @param oid: owner id
        @param gid: good id
        """
        stat=sql.SQL("INSERT INTO owners (owner_id, good_id) VALUES ({oid}, {gid})").\
            format(oid=sql.Literal(oid), \
                   gid=sql.Literal(gid))
        self.db_log.debug(stat)
        self.cur.execute(stat)

class updates(object):
    def __init__(self, conn, cur, logger):
        self.conn=conn
        self.cur=cur
        self.db_log=logger
    def update_account(self, cid, balance):
        """update the banking account with the calculated new balance (CALLED FROM SERVER SIDE)

        @param cid: client id
        @param balance: the account balance
        """
        stat = sql.SQL("UPDATE banking SET (balance, balance_dt) = ({balance}, {dt}) WHERE client_id={cid}").\
            format(balance=sql.Literal(balance), \
                   dt=sql.Literal(dt.datetime.now().strftime(TIMESTAMP_FORMAT)), \
                   cid=sql.Literal(cid))
        self.cur.execute(stat)
    def update_owner(self, oid, gid):
        """reassign the good's ownership with corresponding gid

        @param gid: good id
        """
        stat = sql.SQL("UPDATE owners SET (owner_id) = {oid} WHERE good_id={gid}").\
            format(oid=sql.Literal(oid), \
                   bid=sql.Literal(gid))
        self.cur.execute(stat)

class database(object):
    def __init__(self, dbconfigs):
        #cursor
        self.db_configs=dbconfigs
        self.conn = psycopg2.connect(self.db_configs)
        self.cur = self.conn.cursor()
        #logger
        logging.basicConfig(filename="db.log", \
                            format='%(asctime)s %(message)s', \
                            filemode='w')
        self.logger=logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.exists=exists(self.conn, self.cur)
        self.gets=gets(self.conn, self.cur, self.logger)
        self.inserts=inserts(self.conn, self.cur, self.logger)
        self.updates=updates(self.conn, self.cur, self.logger)
    def commit(self):
        self.conn.commit()
        self.logger.info("database committed")
    def rollback(self):
        self.conn.rollback()
        self.logger.info("database rollback")
    def init(self):
        self.conn=psycopg2.connect(self.db_configs) #TODO (res) should it be called?!
        self.cur=self.conn.cursor()
        self.logger.info("database initialized")
    def close(self):
        self.conn.close()
