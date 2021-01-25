from core.connection_cursor import cur
from core.utils import db_log
from psycopg2 import sql

def insert_contact(cid, cname, bid):
    """ insert new contact (CALLED AT THE CLIENT SIDE)

    @param cid: contact id (the same as client id in the server side)
    @param cname: contact name
    @param bid: bank account id
    """
    stat=sql.SQL("INSERT INTO contacts (contact_id, contact_name bank_account_id) VALUES ({cid}, {cname}, {bid})").\
        format(cid=sql.Literal(cid), \
               cname=sql.Literal(cname), \
               bid=sql.Literal(bid))
    db_log.debug(stat)
    cur.execute(stat)
