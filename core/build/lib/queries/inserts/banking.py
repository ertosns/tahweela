from core.connection_cursor import cur
import datetime as dt
from core.utils import TIMESTAMP_FORMAT, db_log
from psycopg2 import sql

def insert_banking(cid, balance):
    """ give the client with the given id (cid) banking account (CALLED AT SERVER SIDE)

    @param cid: client id
    @param balance: client account balance
    """
    stat=sql.SQL("INSERT INTO banking (client_id, balance, balance_dt) VALUES ({cid}, {balance}, {dt});"). \
        format(cid=sql.Literal(cid), \
               balance=sql.Literal(balance), \
               dt=sql.Literal(dt.datetime.now().strftime(TIMESTAMP_FORMAT)))
    db_log.debug(stat)
    cur.execute(stat)
    stat="SELECT currval(pg_get_serial_sequence('banking', 'id'));"
    db_log.debug(stat)
    cur.execute(stat);
    return cur.fetchone()[0]
