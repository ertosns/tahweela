from core.connection_cursor import cur
from psycopg2 import sql

def exists(cid):
    """verify that a contact with given id is available (CALLED AT THE CLIENT SIDE)

    @param cid: contact id
    @return boolean wither the contact exists or note
    """
    stat=sql.SQL("SELECT EXISTS (SELECT 1 FROM contacts WHERE contact_id={cid});").\
        format(cid=sql.Literal(cid))
    cur.execute(stat)
    return cur.fetchone()[0]
