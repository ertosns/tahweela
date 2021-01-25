from core.connection_cursor import conn, cur
import pandas as pd
from core.utils import db_log
from psycopg2 import sql

def get_client_id(bid):
    """ retrieve the corresponding client_id of the given banking_id (bid) (called at the server side)

    @param bid: banking id
    @return cid: contact id
    """
    query=sql.SQL("SELECT (client_id) FROM banking WHERE id={bid} LIMIT 1").format(bid=sql.Literal(bid))
    db_log.debug(query)
    return pd.read_sql(query, conn).ix[0]

def get_banking_id(cid):
    """retrieve the corresponding banking_id of the given  client_id (cid) (called at the server side)

    @param cid: client id
    @return bid: banking id
    """
    query=sql.SQL("SELECT (id) FROM banking WHERE client_id={cid} LIMIT 1").format(cid=sql.Literal(cid))
    db_log.debug(query)
    return pd.read_sql(query, conn).ix[0]

def get_balance_by_cid(cid):
    """called at the server side to retrieve the account balance d of the given client_id (cid)

    @param cid: client id
    @return bid: banking id
    """
    query=sql.SQL("SELECT (balance) FROM banking WHERE client_id={cid} LIMIT 1").format(cid=sql.Literal(cid))
    db_log.debug(query)
    return pd.read_sql(query, conn).ix[0]

def get_balance_by_credid(cred_id):
    """ get balance of client with given credential id

    @param cred_id: client credential id
    """
    query=sql.SQL("SELECT (b.balance) FROM banking as b JOIN WITH credentials AS c WHERE c.cred_id={credid} AND c.id==b.client_id;").format(credid=sql.Literal(cred_id))
    db_log.debug(query)
    cur.execute(query)
    return cur.fetchone()[0]
