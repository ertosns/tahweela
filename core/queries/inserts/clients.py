from core.connection_cursor import cur
from psycopg2 import sql

def insert_client(name):
    """ add new client to the network (CALLED AT THE SERVER SIDE),

    note that some clients might not have banking id yet
    @param name: client name
    """
    stat=sql.SQL("INSERT INTO clients (contact_name) VALUES ({name})").\
        format(name=sql.Literal(name))
    cur.execute(stat)
    cur.execute("SELECT currval(pg_get_serial_sequence('clients', 'id'));")
    return cur.fetchone()[0]
