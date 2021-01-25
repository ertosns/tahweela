from core.connection_cursor import cur
from psycopg2 import sql

def exists(cid):
    """verify that a banking account with the given client id is available (CALLED AT THE SERVER SIDE)

    @param cid: client id
    @return boolean wither the banking account for give client exists or note
    """
    stat=sql.SQL("SELECT EXISTS (SELECT 1 FROM banking WHERE client_id={cid});").\
        format(cid=sql.Literal(cid))
    cur.execute(stat)
    return cur.fetchone()[0]
