import pandas as pd
from core.queries.gets.currency import to_dollar
from core.connection_cursor import conn
from core.utils import db_log

def get_all():
    query="SELECT * FROM goods;"
    #return pd.read_sql(query, conn, index_col='id').to_json()
    return pd.read_sql(query, conn).to_json()

def get_good(gid):
    """retrive good for the given goods id (gid)

    @param gid: goods id
    @return pandas data series of the corresponding row
    """
    query = sql.SQL("SELECT * FROM goods WHERE id={gid};").\
        format(gid=sql.Literal(gid))
    db_log.debug(query)
    return pd.read_sql(query, conn)

def get_commodity(gname, quality=0):
    """retrive good for the given goods constraints

    @param gname: goods name
    @param quality: retrieve goods with quality > given threshold
    @return pandas data frame of the corresponding constrains
    """
    query = sql.SQL("SELECT * FROM goods WHERE good_name={gname} AND good_quality>={gquality}").\
        format(gname=sql.Literal(gname), \
               quality=sql.Literal(gquality))
    db_log.debug(query)
    return pd.read_sql(query, conn)

def get_new_price(gid):
    """ get good price with given good's id

    @param gid: good's id
    @return price in dollar
    """
    df = get_good(gid)
    cur_id = df['good_currency_id'].ix[0]
    return df['good_cost'].ix[0]*to_dollar(cur_id)
