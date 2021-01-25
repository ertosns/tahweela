import pandas as pd
from core.connection_cursor import conn, cur
from core.utils import db_log
from psycopg2 import sql

def get_all():
    query = "SELECT * FROM credentials;"
    db_log.debug(query)
    ret = pd.read_sql(conn, query)
    return ret

def get_credential(cid):
    """ get the credential for the client with given cid(CALLED FROM SERVER SIDE),
    or get the single row for client with cid=1 (CALLED FROM CLIENT SIDE)

    @param cid: client id, or 1 (in case of call from client side for it's own credential)
    """
    query=sql.SQL("SELECT * FROM credentials WHERE id={cid} LIMIT 1;)").\
        format(cid=sql.Literal(cid))
    db_log.debug(query)
    ret = pd.read_sql(conn, query)

def get_id(cred_id):
    """ get client id

    @param cred_id: credential id
    @return the id, or None if doesn't exist
    """
    query=sql.SQL("SELECT id FROM credentials WHERE cred_id={credid} LIMIT 1;").\
        format(credid=sql.Literal(cred_id))
    db_log.debug(query)
    cur.execute(query)
    return cur.fetchone()[0]

def get_password(cred_id):
    """ get user's passcode for authentication

    @param cred_id: credential id
    @return list of the id, or empty list of doesn't exist
    """
    query=sql.SQL("SELECT (passcode) FROM credentials WHERE cred_id={credid} LIMIT 1;").\
        format(credid=sql.Literal(cred_id))
    db_log.debug(query)
    cur.execute(query)
    return cur.fetchone()[0]

def get_credid_with_gid(gid):
    """cross reference credential id, with good's id

    @param gid: good's id
    @return credential id credid
    """
    query=sql.SQL("SELECT (C.cred_id) FROM credentials as c JOIN WITH goods AS g JOIN WITH owners as o WHERE g.id=={gid} AND o.owner_id==c.id LIMIT 1;").\
        format(gid=sql.Literal(gid))
    db_log.debug(query)
    cur.execute(query)
    return cur.fetchone()[0]
