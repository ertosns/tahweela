import datetime as dt
from core.connection_cursor import cur
from core.utils import TIMESTAMP_FORMAT
from psycopg2 import sql

def update_account(cid, balance):
    """update the banking account with the calculated new balance (CALLED FROM SERVER SIDE)

    @param cid: client id
    @param balance: the account balance
    """
    stat = sql.SQL("UPDATE banking SET (balance, balance_dt) = ({balance}, {dt}) WHERE client_id={cid}").\
        format(balance=sql.Literal(balance), \
               dt=dt.datetime().strftime(TIMESTAMP_FORMAT), \
               cid=sql.Literal(cid))
    cur.execute(stat)
