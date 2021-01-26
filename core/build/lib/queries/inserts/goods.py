from core.connection_cursor import cur
from core.utils import db_log
from psycopg2 import sql

def add_good(gname, gquality, gcost, gcid=1):
    """ INSERT new good into the goods table

    @param gname: good name
    @param gquality: good quality
    @param gcost: good cost
    @param gcid: good currency id
    """
    stat=sql.SQL("INSERT INTO goods (good_name, good_quality, good_cost, good_currency_id) VALUES ({gname}, {gquality}, {gcost}, {gcid});").\
        format(gname=sql.Literal(gname), \
               gquality=sql.Literal(gquality), \
               gcost=sql.Literal(gcost), \
               gcid=sql.Literal(gcid))
    db_log.debug(stat)
    cur.execute(stat)
    stat="SELECT currval(pg_get_serial_sequence('goods', 'id'));"
    cur.execute(stat)
    db_log.debug(stat)
    return cur.fetchone()[0]
