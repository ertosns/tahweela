from core.connection_cursor import cur
from psycopg2 import sql

def exists(gid):
    """verify that a good with given id is available

    @param gid: good id
    @return boolean wither the good exists or note
    """
    stat=sql.SQL("SELECT EXISTS (SELECT 1 FROM goods WHERE id={gid});").format(gid=sql.Literal(gid))
    cur.execute(stat)
    return cur.fetchone()[0]
