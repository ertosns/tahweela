import pandas as pd
import datetime as dt
from core.connection_cursor import conn, cur
from core.utils import db_log
from psycopg2 import sql

def get_transactions(st_dt, end_dt=dt.datetime.now()):
    """ get the transactions within the given period exclusively

    @param st_dt: the start datetime
    @param end_dt: the end datetime
    @return dataframe of the transactions
    """
    stat = sql.SQL("SELECT * FROM ledger WHERE trx_dt>{st_dt} AND trx_dt<{end_dt};").\
        format(st_dt=sql.Literal(st_dt), \
               end_dt=sql.Literal(end_dt))
    db_log.debug(stat)
    return pd.read_sql(conn, stat)

def get_sells(dest, st_dt, end_dt=None):
    """ get sells transaction within the st_dt, end_dt period, while there destined to dest (CALLED AT SERVER SIDE)
    @param dest: the destination credential id
    @return sells transactions
"""
    trx=get_transactions(st_dt, end_dt).to_json()
    trx.apply(lambda x:x['trx_dest']==dest, inplace=True)
    return trx

def get_last_timestamp():
    """ retrieve the timestamp of the last transaction (CALLED FROM THE CLIENT SIDE)

    @return timestamp
    """
    query="SELECT currval(pg_get_serial_sequence('ledger', 'trx_id'));"
    db_log.debug(query)
    cur.execute(query)
    return cur.fetchone()[0]
