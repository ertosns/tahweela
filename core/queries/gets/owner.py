import pandas as pd
from core.connection_cursor import conn
from core.utils import db_log
from psycopg2 import sql

def get_all():
    query="SELECT * FROM owner;"
    return pd.read_sql(query, conn, index_col='id')

def get_good_owner(gid):
   """return owner id (oid) for the given gid

   @param gid: good
   @return the owner id
   """
   query = sql.SQL("SELECT (owner_id) FROM owners WHERE good_id={gid}").\
       format(gid=sql.Literal(gid))
   db_log.debug(query)
   return pd.read_sql(query, conn).ix[0]

def get_owner_goods(oid):
   """return the good assigned to the given owner id (oid)

   @param oid: is the owner id
   @return json dict of good's ids
   """
   query = sql.SQL("SELECT (good_id) FROM owners WHERE owner_id={oid}").\
       format(oid=sql.Literal(oid))
   db_log.debug(query)
   return pd.read_sql(query, conn).to_json()
