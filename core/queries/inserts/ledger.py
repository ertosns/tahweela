from core.connection_cursor import cur
from core.utils import db_log
from psycopg2 import sql

def insert_trx(des, src, gid):
    """ insert transaction from 'src' to 'des' for good with 'gid'

    @param des: the transaction destination
    @param src: the transaction source
    @param gid: the good's id
    """
    stat=sql.SQL("INSERT INTO ledger (trx_dest, trx_src, good_id) VALUES ({des}, {src}, {gid});").\
        format(des=sql.Literal(des), \
               src=sql.Literal(src), \
               gid=sql.Literal(gid))
    db_log.debug(stat)
    cur.execute(stat)
