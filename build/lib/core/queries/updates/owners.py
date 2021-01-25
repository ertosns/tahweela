from core.connection_cursor import cur
from psycopg2 import sql

def update_owner(oid, gid):
    """reassign the good's ownership with corresponding gid

    @param gid: good id
    """
    stat = sql.SQL("UPDATE owners SET (owner_id) = {oid} WHERE good_id={gid}").\
        format(oid=sql.Literal(oid), \
               bid=sql.Literal(gid))
    cur.execute(stat)
