import pandas as pd
from core.connection_cursor import conn
from core.utils import db_log
from psycopg2 import sql

def get_all():
    query = "SELECT * FROM contacts;"
    db_log.debug(query)
    return pd.read_sql(query, conn)

def get_banking_id(cid):
    """ called at the client side, to retrieve the stored banking id in the contacts

    @param cid: contact id
    @return banking_id or the associated banking id for the given contact id
    """
    query=sql.SQL("SELECT (bank_account_id) FROM contacts WHERE contact_id='{cid}' LIMIT 1;").\
        format(cid=sql.Literal(cid))
    db_log.debug(query)
    return pd.read_sql(query, conn).ix[0]
