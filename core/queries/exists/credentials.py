from core.connection_cursor import cur
from psycopg2 import sql

def exists(cid):
    """ verify the credential for the client with given cid(CALLED FROM SERVER SIDE),
    or get the single row for client with cid=1 (CALLED FROM CLIENT SIDE)

    @param cid: client id, or 1 (in case of call from client side for it's own credential)
    @return boolean for wither the client (with given cid) is registered or not
    """
    stat=sql.SQL("SELECT EXISTS (SELECT 1 FROM credentials WHERE id={cid})").\
        format(cid=sql.Literal(cid))
    cur.execute(stat)
    return cur.fetchone()[0]

'''
def exists(cred_id, passcode):
    """ verify the credential for the client with given cid(CALLED FROM SERVER SIDE),
    or get the single row for client with cid=1 (CALLED FROM CLIENT SIDE)

    @param cid: client id, or 1 (in case of call from client side for it's own credential)
    @return boolean for wither the client (with given cid) is registered or not
    """
    stat="SELECT EXISTS (SELECT 1 FROM credentials WHERE cred_id={} AND passcode={})".\
        format(cred, passcode)
    cur.execute(cid)
    return cur.fetchone()[0]
'''
