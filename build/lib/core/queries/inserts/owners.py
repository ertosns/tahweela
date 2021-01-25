from core.connection_cursor import cur
from core.utils import db_log
from psycopg2 import sql

def add_owner(oid, gid):
    """assign ownership of owner with id (oid) to the good with id (gid)

    @param oid: owner id
    @param gid: good id
    """
    stat=sql.SQL("INSERT INTO owners (owner_id, good_id) VALUES ({oid}, {gid})").\
        format(oid=sql.Literal(oid), \
               gid=sql.Literal(gid))
    db.log(stat)
    cur.execute(stat)
