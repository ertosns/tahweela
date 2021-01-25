import pandas as pd
from core.connection_cursor import conn
from core.utils import db_log
from psycopg2 import sql

def to_dollar(cid):
    """ convert currency of the corresponding id to dollar ratio

    for example if currency A = 2 dollars, then the conversion would be 0.5,
    for another currency B = 0.5 dollar, then the conversion to dollar would be 2
    such that for given cost of xA, would be 0.5x$.
    @param cid is the id of the corresponding currency
    @return transformation ratio to dollar
    """
    query = sql.SQL("SELECT * FROM currency WHERE id=cid;").\
        format(cid=sql.Literal(cid))
    db_log.debug(query)
    ratio = 1.0/pd.read_sql(query, conn)['currency_value'].ix[0]
    return ratio
