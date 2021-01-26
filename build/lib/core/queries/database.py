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
    def account_byemail(self, email):
        """verify that account with corresponding email doesn't exists

        @param email: client email
        @return boolean for hypothesis test, that it exists
        """
        stat=sql.SQL("SELECT EXISTS (SELECT 1 FROM clients WHERE client_email={email}) FOR UPDATE SKIP LOCKED;")\
            .format(email=sql.Literal(email))
        self.cur.execute(stat)
        fet=self.cur.fetchone()
        print('exists.account_byemail {} fet: {}'.format(email, fet))
        return fet[0]
    def account_byname(self, name, passcode):
        """verify that account with corresponding email doesn't exists

        @param name: client name
        @param passcode: client passcode
        @return boolean for hypothesis test, that it exists
        """
        stat=sql.SQL("SELECT EXISTS(SELECT 1 FROM clients AS c JOIN credentials AS cred ON cred.id=c.client_id WHERE c.client_name={name} AND cred.passcode={passcode}) FOR UPDATE SKIP LOCKED;")\
            .format(name=sql.Literal(name),\
                    passcode=sql.Literal(passcode))
        self.cur.execute(stat)
        fet=self.cur.fetchone()
        print('exists.account_byname {} fet: {}'.format(name, fet))
        return fet[0]
    def bank_account_bycid(self, cid):
        """verify that a banking account with the given client id is available (CALLED AT THE SERVER SIDE)

        @param cid: client id
        @return boolean wither the banking account for give client exists or note
        """
        stat=sql.SQL("SELECT EXISTS (SELECT 1 FROM banking WHERE client_id={cid}) FOR UPDATE SKIP LOCKED;").\
            format(cid=sql.Literal(cid))
        self.cur.execute(stat)
        return self.cur.fetchone()[0]
    def client_exists(self, cid):
        """verify that  a client with given id is available (CALLED AT THE SERVER SIDE)

        @param cid: client id
        @return boolean wither the client exists or note
        """
        stat=sql.SQL("SELECT EXISTS (SELECT 1 FROM clients WHERE client_id={cid}) FOR UPDATE SKIP LOCKED;").\
            format(cid=sql.Literal(cid))
        self.cur.execute(stat)
        return self.cur.fetchone()[0]
    def contact_exists(self, cid):
        """verify that a contact with given id is available (CALLED AT THE CLIENT SIDE)

        @param cid: contact id
        @return boolean wither the contact exists or note
        """
        stat=sql.SQL("SELECT EXISTS (SELECT 1 FROM contacts WHERE contact_id={cid}) FOR UPDATE SKIP LOCKED;").\
            format(cid=sql.Literal(cid))
        self.cur.execute(stat)
        return self.cur.fetchone()[0]
    def credential_exists(self, cid):
        """ verify the credential for the client with given cid(CALLED FROM SERVER SIDE),
        or get the single row for client with cid=1 (CALLED FROM CLIENT SIDE)

        @param cid: client id, or 1 (in case of call from client side for it's own credential)
        @return boolean for wither the client (with given cid) is registered or not
        """
        stat=sql.SQL("SELECT EXISTS (SELECT 1 FROM credentials WHERE id={cid}) FOR UPDATE SKIP LOCKED;").\
            format(cid=sql.Literal(cid))
        self.cur.execute(stat)
        return self.cur.fetchone()[0]
    '''
    def exists(self, gid):
        """verify that a good with given id is available

        @param gid: good id
        @return boolean wither the good exists or note
        """
        stat=sql.SQL("SELECT EXISTS (SELECT 1 FROM goods WHERE id={gid}) FOR UPDATE SKIP LOCKED;").\
            format(gid=sql.Literal(gid))
        self.cur.execute(stat)
        return self.cur.fetchone()[0]
    '''
class gets(object):
    def __init__(self, conn, cur, logger):
        self.conn=conn
        self.cur=cur
        self.db_log=logger
    def get_client_id_byemail(self, email):
        """ retrieve the corresponding client_id of the given banking_id (bid) (called at the server side)

        @param bid: banking id
        @return cid: contact id
        """
        query=sql.SQL("SELECT (client_id) FROM clients WHERE client_email={email} LIMIT 1 FOR UPDATE SKIP LOCKED;").\
            format(email=sql.Literal(email))
        self.db_log.debug(query)
        self.cur.execute(query)
        ret=self.cur.fetchone()
        if None:
            return False
        return ret[0]
    #pd.read_sql(query, self.conn).ix[0]
    def get_client_id_byname(self, name, passcode):
        """ retrieve the corresponding client_id of the given banking_id (bid) (called at the server side)

        @param bid: banking id
        @return cid: contact id
        """
        query=sql.SQL("SELECT (c.client_id) FROM clients AS c INNER JOIN credentials   ON (credentials.id=c.client_id) WHERE c.client_name={name} AND credentials.passcode={passcode} LIMIT 1  FOR UPDATE SKIP LOCKED;").\
            format(name=sql.Literal(name),\
                   passcode=sql.Literal(passcode))
        self.db_log.debug(query)
        self.cur.execute(query)
        return self.cur.fetchone()
        #return pd.read_sql(query, self.conn).iloc[0]
    def get_client_id(self, bid):
        """ retrieve the corresponding client_id of the given banking_id (bid) (called at the server side)

        @param bid: banking id
        @return cid: contact id
        """
        query=sql.SQL("SELECT (client_id) FROM banking WHERE id={bid} LIMIT 1 FOR UPDATE SKIP LOCKED;").\
            format(bid=sql.Literal(bid))
        self.db_log.debug(query)
        self.cur.execute(query)
        return self.cur.fetchone()[0]
        #return pd.read_sql(query, self.conn).ix[0]

    def get_banking_id(self, cid):
        """retrieve the corresponding banking_id of the given  client_id (cid) (called at the server side)

        @param cid: client id
        @return bid: banking id
        """
        query=sql.SQL("SELECT (id) FROM banking WHERE client_id={cid} LIMIT 1 FOR UPDATE SKIP LOCKED;").\
            format(cid=sql.Literal(cid))
        self.db_log.debug(query)
        self.cur.execute(query)
        return self.cur.fetchone()[0]
        #return pd.read_sql(query, self.conn).ix[0]

    def get_balance_by_cid(self, cid):
        """called at the server side to retrieve the account balance d of the given client_id (cid)

        @param cid: client id
        @return bid: banking id
        """
        query=sql.SQL("SELECT (balance) FROM banking WHERE client_id={cid} LIMIT 1 FOR UPDATE SKIP LOCKED;").\
            format(cid=sql.Literal(cid))
        self.db_log.debug(query)
        self.cur.execute(query)
        return self.cur.fetchone()[0]
        #return pd.read_sql(query, self.conn).ix[0]

    def get_balance_by_credid(self, cred_id):
        """ get balance of client with given credential id

        @param cred_id: client credential id
        """
        query=sql.SQL("SELECT (b.balance) FROM banking as b JOIN  credentials AS c ON c.id=b.client_id WHERE c.cred_id={credid} FOR UPDATE SKIP LOCKED;").\
            format(credid=sql.Literal(cred_id))
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
        query="SELECT * FROM clients FOR UPDATE NOWAIT;"
        self.db_log.debug(query)
        return pd.read_sql(query, self.conn).to_json
    def get(self, cid):
        """retrieve client into with given client id (cid)

        @param cid: client id
        @return tuple (id, name, join date)
        """
        query=sql.SQL("SELECT * FROM clients WHERE client_id={cid} LIMIT 1 FOR UPDATE SKIP LOCKED;").\
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
        #query = "SELECT * FROM contacts FOR UPDATE NOWAIT;"
        self.db_log.debug(query)
        return pd.read_sql(query, self.conn).to_json()
    '''
    def get_banking_id(self, cid):
        """ called at the client side, to retrieve the stored banking id in the contacts(called from client s)

        @param cid: contact id
        @return banking_id or the associated banking id for the given contact id
        """
        query=sql.SQL("SELECT (bank_account_id) FROM contacts WHERE contact_id='{cid}' LIMIT 1 FOR UPDATE SKIP LOCKED;").\
            format(cid=sql.Literal(cid))
        self.db_log.debug(query)
        return pd.read_sql(query, self.conn).ix[0]
    '''
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
        query=sql.SQL("SELECT * FROM credentials WHERE id={cid} LIMIT 1 FOR UPDATE SKIP LOCKED;)").\
            format(cid=sql.Literal(cid))
        self.db_log.debug(query)
        ret = pd.read_sql(query, self.conn)

    def credid2cid(self, cred_id):
        """ get client id

        @param cred_id: credential id
        @return the id, or None if doesn't exist
        """
        query=sql.SQL("SELECT id FROM credentials WHERE cred_id={credid}  FOR UPDATE SKIP LOCKED;").\
            format(credid=sql.Literal(cred_id))
        self.db_log.debug(query)
        self.cur.execute(query)
        fet=self.cur.fetchone()
        print("cred2cid fet: ", fet)
        return fet[0]
    def cid2credid(self, cid):
        """ get credential id

        @param cid: client's id
        @return credidid
        """
        query=sql.SQL("SELECT cred_id FROM credentials WHERE id={cid}  FOR UPDATE SKIP LOCKED;").\
            format(cid=sql.Literal(cid))
        self.db_log.debug(query)
        self.cur.execute(query)
        fet=self.cur.fetchone()
        print("cid2credid fet: ", fet)
        return fet[0]
    def get_password(self, cred_id):
        """ get user's passcode for authentication

        @param cred_id: credential id
        @return list of the id, or empty list of doesn't exist
        """
        query=sql.SQL("SELECT (passcode) FROM credentials WHERE cred_id={credid}  FOR UPDATE SKIP LOCKED;").\
            format(credid=sql.Literal(cred_id))
        self.db_log.debug(query)
        self.cur.execute(query)
        return self.cur.fetchone()[0]
    '''
    def get_credid_with_gid(self, gid):
        """cross reference credential id, with good's id

        @param gid: good's id
        @return credential id credid
        """
        query=sql.SQL("SELECT (c.cred_id) FROM goods, credentials as c JOIN owners as o ON c.id=o.owner_id  WHERE goods.id={gid} LIMIT 1 FOR UPDATE SKIP LOCKED;").\
            format(gid=sql.Literal(gid))
        self.db_log.debug(query)
        self.cur.execute(query)
        fet=self.cur.fetchone()
        self.db_log.debug("fetched credid with gid: "+str(fet))
        return fet
    '''
    def to_dollar(self, cid):
        """ convert currency of the corresponding id to dollar ratio

        for example if currency A = 2 dollars, then the conversion would be 0.5,
        for another currency B = 0.5 dollar, then the conversion to dollar would be 2
        such that for given cost of xA, would be 0.5x$.
        @param cid is the id of the corresponding currency
        @return transformation ratio to dollar
        """
        query = sql.SQL("SELECT * FROM currency WHERE id=cid FOR UPDATE SKIP LOCKED;").\
            format(cid=sql.Literal(cid))
        self.db_log.debug(query)
        ratio = 1.0/pd.read_sql(query, self.conn)['currency_value'].ix[0]
        return ratio
    '''
    def get_all_goods(self):
        query="SELECT * FROM goods FOR UPDATE NOWAIT;"
        #return pd.read_sql(query, conn, index_col='id').to_json()
        return pd.read_sql(query, self.conn).to_json()

    def get_good(self, gid):
        """retrive good for the given goods id (gid)

        @param gid: goods id
        @return pandas data series of the corresponding row
        """
        query = sql.SQL("SELECT * FROM goods WHERE id={gid} FOR UPDATE SKIP LOCKED;").\
            format(gid=sql.Literal(gid))
        self.db_log.debug(query)
        return pd.read_sql(query, self.conn)
    def get_commodity(self, gname, quality=0):
        """retrive good for the given goods constraints

        @param gname: goods name
        @param quality: retrieve goods with quality > given threshold
        @return pandas data frame of the corresponding constrains
        """
        query = sql.SQL("SELECT * FROM goods WHERE good_name={gname} AND good_quality>={gquality} FOR UPDATE SKIP LOCKED;").\
            format(gname=sql.Literal(gname), \
                   gquality=sql.Literal(gquality))
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
    '''
    def get_transactions(self, st_dt, end_dt=dt.datetime.now()):
        """ get the transactions within the given period exclusively

        @param st_dt: the start datetime
        @param end_dt: the end datetime
        @return dataframe of the transactions
        """
        stat = "SELECT * FROM ledger;"
        if st_dt==None:
            stat=sql.SQL("SELECT * FROM ledger WHERE trx_dt>{st_dt} AND trx_dt<{end_dt}  FOR UPDATE SKIP LOCKED;").\
            format(st_dt=sql.Literal(st_dt), end_dt=sql.Literal(end_dt))
        self.db_log.debug(stat)
        return pd.read_sql(stat, self.conn)
    #TODO if not transactions available return 0
    def get_transactions_sum(self, \
                             trx_with_credid, \
                             st_dt=None, \
                             end_dt=None):
        """ get the transactions within the given period inclusively

        @param trx_with_credid: the credential id of the client of interest
        @param st_dt: the start datetime
        @param end_dt: the end datetime
        @return dataframe of the transactions
        """
        if end_dt==None:
            end_dt=dt.datetime.now().strftime(TIMESTAMP_FORMAT)

        stat = "SELECT SUM(trx_cost) FROM ledger WHERE (trx_dest={to_credid} OR trx_src={from_credid});".\
            format(to_credid=sql.Literal(trx_with_credid),\
                   from_credid=sql.Literal(trx_with_credid))

        if not st_dt==None:
            #note! FOR UPDATE is not allowed with aggregate functions
            stat=sql.SQL("SELECT SUM(trx_cost) FROM ledger WHERE (trx_dt>={st_dt} AND trx_dt<{end_dt} AND trx_dest={to_credid}) OR (trx_dt>={st_dt} AND trx_dt<{end_dt} AND trx_src={from_credid});").\
            format(st_dt=sql.Literal(st_dt),\
                   end_dt=sql.Literal(end_dt),\
                   to_credid=sql.Literal(trx_with_credid), \
                   from_credid=sql.Literal(trx_with_credid))
        self.db_log.debug(stat)
        self.cur.execute(stat)
        fet=self.cur.fetchone()[0]
        if fet==None:
            return 0
        return fet
        #return pd.read_sql(stat, self.conn)
    def get_sells(self, dest, st_dt, end_dt=None):
        """ get sells transaction within the st_dt, end_dt period, while there destined to dest (CALLED AT SERVER SIDE)

        @param dest: the destination credential id
        @return sells transactions
        """
        ###
        stat = sql.SQL("SELECT * FROM ledger WHERE trx_dest={dest};")\
                  .format(dest=sql.Literal(dest))
        if st_dt==None:
            stat=sql.SQL("SELECT * FROM ledger WHERE trx_dt>{st_dt} AND trx_dt<{end_dt} AND trx_dest={dest} FOR UPDATE SKIP LOCKED;").\
            format(st_dt=sql.Literal(st_dt),\
                   end_dt=sql.Literal(end_dt),\
                   dest=dest)
        self.db_log.debug(stat)
        return pd.read_sql(stat, self.conn)
        ###
        trx=self.get_transactions(st_dt, end_dt)
        #trx.apply(lambda x:x['trx_dest']==dest, inplace=True)
        trx=trx.apply(lambda x:x['trx_dest']==dest)
        return trx

    def get_last_timestamp(self):
        """ retrieve the timestamp of the last transaction (CALLED FROM THE CLIENT SIDE)

        @return timestamp
        """
        query="SELECT currval(pg_get_serial_sequence('ledger', 'trx_id')) FOR UPDATE SKIP LOCKED;"
        self.db_log.debug(query)
        self.cur.execute(query)
        return self.cur.fetchone()[0]
    '''
    def get_all_owners(self):
        query="SELECT * FROM owner FOR UPDATE NOWAIT;"
        return pd.read_sql(query, self.conn, index_col='id')

    def get_good_owner(self, gid):
        """return owner id (oid) for the given gid

        @param gid: good
        @return the owner id
        """
        query = sql.SQL("SELECT (owner_id) FROM owners WHERE good_id={gid} FOR UPDATE SKIP LOCKED;").\
            format(gid=sql.Literal(gid))
        self.db_log.debug(query)
        return pd.read_sql(query, self.conn).ix[0]

    def get_owner_goods(self, oid):
        """return the good assigned to the given owner id (oid)

        @param oid: is the owner id
        @return json dict of good's ids
        """
        query = sql.SQL("SELECT (good_id) FROM owners WHERE owner_id={oid} FOR UPDATE SKIP LOCKED;").\
            format(oid=sql.Literal(oid))
        self.db_log.debug(query)
        return pd.read_sql(query, self.conn).to_json()
    '''
class inserts(object):
    def __init__(self, conn, cur, logger):
        self.conn=conn
        self.cur=cur
        self.db_log=logger
    def add_bank_account(self, cid, balance, bank_name, branch_number, account_number, name_reference):
        """ give the client with the given id (cid) banking account (CALLED AT SERVER SIDE)

        @param cid: client id
        @param balance: client account balance
        """
        stat=sql.SQL("INSERT INTO banking (client_id, balance,  bank_name, branch_number, account_number, name_reference) VALUES ({cid}, {balance}, {bname}, {bnum}, {anum}, {nr});"). \
            format(cid=sql.Literal(cid), \
                   balance=sql.Literal(balance), \
                   bname=sql.Literal(bank_name),
                   bnum=sql.Literal(branch_number),
                   anum=sql.Literal(account_number),
                   nr=sql.Literal(name_reference)
                   )
        self.db_log.debug(stat)
        self.cur.execute(stat)
        stat="SELECT currval(pg_get_serial_sequence('banking', 'id'));"
        self.db_log.debug(stat)
        self.cur.execute(stat);
        return self.cur.fetchone()[0]
    '''
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
    '''
    def add_client(self, name, email):
        """ add new client to the network (CALLED AT THE SERVER SIDE),

        note that some clients might not have banking id yet
        @param name: client name
        @param email: client email
        """
        stat=sql.SQL("INSERT INTO clients (client_name, client_email) VALUES ({name}, {email})").\
            format(name=sql.Literal(name),\
                   email=sql.Literal(email))
        self.cur.execute(stat)
        self.cur.execute("SELECT currval(pg_get_serial_sequence('clients', 'client_id'));")
        return self.cur.fetchone()[0]
    def insert_contact(self, email, name, credid):
        """ insert new contact (CALLED AT THE CLIENT SIDE)


        @param email: contact's email
        @param name: contact's name
        @param credid: contact's credid
        """
        stat=sql.SQL("INSERT INTO contacts (contact_id, contact_name, contact_email) VALUES ({credid}, {email}, {name})").\
            format(credid=sql.Literal(credid), \
                   email=sql.Literal(email), \
                   name=sql.Literal(name))
        self.db_log.debug(stat)
        self.cur.execute(stat)

    def register(self, cid, passcode, cred_id):
        """add client credentials returned from the server

        @param cid: client id
        @param passcode: client password
        @param cred_id: credential id
        """
        stat=sql.SQL("INSERT INTO credentials (id, passcode, cred_id) VALUES ({cid}, {passcode}, {credid});").\
            format(cid=sql.Literal(cid),\
                   passcode=sql.Literal(passcode), \
                   credid=sql.Literal(cred_id))
        self.db_log.debug(stat)
        self.cur.execute(stat)
    '''
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
    '''
    def insert_trx(self, des, src, cost):
        """ insert transaction from 'src' to 'des' for good with 'gid'

        @param des: the transaction destination
        @param src: the transaction source
        @param cost: the transaction amount
        """
        stat=sql.SQL("INSERT INTO ledger (trx_dest, trx_src, trx_cost) VALUES ({des}, {src}, {cost});").\
            format(des=sql.Literal(des), \
                   src=sql.Literal(src), \
                   cost=sql.Literal(cost))
        self.db_log.debug(stat)
        self.cur.execute(stat)
    '''
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
    '''
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
    '''
    def update_owner(self, oid, gid):
        """reassign the good's ownership with corresponding gid

        @param gid: good id
        """
        stat = sql.SQL("UPDATE owners SET (owner_id) = {oid} WHERE good_id={gid}").\
            format(oid=sql.Literal(oid), \
                   bid=sql.Literal(gid))
        self.cur.execute(stat)
    '''
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
    def commit(self, lock=None):
        self.conn.commit()
        self.logger.info("database committed")
        #self.repeatable_read()
        if not lock==None:
            self.unlock_advisory(lock)
    def rollback(self, lock=None):
        self.conn.rollback()
        self.logger.info("database rollback")
        if not lock==None:
            self.unlock_advisory(lock)
    def init(self):
        self.conn=psycopg2.connect(self.db_configs) #TODO (res) should it be called?!
        self.cur=self.conn.cursor()
        self.logger.info("database initialized")
    def repeatable_read(self):
        self.cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;")
    def committed_read(self):
        self.cur.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED;")
    def lock_advisory(self, lock):
        stat="SELECT pg_advisory_lock({});".format(lock)
        self.cur.execute(stat)
    def unlock_advisory(self, lock):
        stat="SELECT pg_advisory_unlock({});".format(lock)
        self.cur.execute(stat)
    def close(self):
        self.conn.close()
