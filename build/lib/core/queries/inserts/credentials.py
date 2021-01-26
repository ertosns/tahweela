#TOOD move random to the __init__ in the start of package, and seed it randomly
import random as rand
import string
from core.utils import MAX_CRED_ID
from core.connection_cursor import cur
from core.utils import db_log
from psycopg2 import sql

def new_cred(passcode, cred_id):
    """add client credentials returned from the server

    @param cid: client id
    """
    stat=sql.SQL("INSERT INTO credentials (passcode, cred_id) VALUES ({passcode}, {credid});").\
        format(passcode=sql.Literal(passcode), \
               credid=sql.Literal(cred_id))
    db_log.debug(stat)
    cur.execute(stat)

def register(cid):
    """register new client credentials with given cid (CALLED FROM SERVER SIDE)

    @param cid: client id
    @return a tuple (cred_id, passcode)
    """
    cred_id=rand.random()*MAX_CRED_ID
    passcode=''.join(rand.choice(string.ascii_uppercase+\
                                 string.ascii_lowercase+string.digits)\
                     for _ in range(9))
    stat=sql.SQL("INSERT INTO credentials (id, passcode, cred_id) VALUES ({cid}, {passcode}, {credid});").\
        format(cid=sql.Literal(cid), \
               passcode=sql.Literal(passcode), \
               credid=sql.Literal(cred_id))
    db_log.debug(stat)
    cur.execute(stat)
    return (cred_id, passcode)

'''
def add_cred(passcode, cred_id):
    """add client credentials returned from the server(CALLED FROM SERVER SIDE)

    @param cid: client id
    """
    stat=sql.SQL("INSERT INTO credentials (passcode, cred_id) VALUES ({passcode}, {credid});").\
        format(passcode=sql.Literal(passcode), \
               credid=sql.Literal(cred_id))
    db_log.debug(stat)
    cur.execute(stat)
'''
