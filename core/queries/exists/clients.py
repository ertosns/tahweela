from core.connection_cursor import cur
from psycopg2 import sql

def exists(cid):
    """verify that  a client with given id is available (CALLED AT THE SERVER SIDE)

    @param cid: client id
    @return boolean wither the client exists or note
    """
    stat=sql.SQL("SELECT EXISTS (SELECT 1 FROM clients WHERE id={cid});").\
        format(cid=sql.Literal(cid))
    cur.execute(stat)
    return cur.fetchone()[0]
