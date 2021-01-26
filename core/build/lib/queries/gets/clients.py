from core.connection_cursor import conn, cur
from core.queries.gets.banking import get_client_id, get_banking_id
from core.utils import db_log
import pandas as pd
from psycopg2 import sql

def get_all():
    """retrieve all clients info

    """
    query="SELECT * FROM clients;"
    db_log.debug(query)
    return pd.read_sql(query, conn)

def get(cid):
    """retrieve client into with given client id (cid)

    @param cid: client id
    @return tuple (id, name, join date)
    """
    query=sql.SQL("SELECT (id, contact_name, client_join_dt) FROM clients WHERE id={cid};").format(cid=sql.Literal(cid))
    db_log.debug(query)
    cur.execute(query)
    return cur.fetchone()

def get_name(cid):
    """retrieve client name corresponding to given client id (cid)

    @param cid: client id
    @return client name
    """
    return get(cid)[1]
