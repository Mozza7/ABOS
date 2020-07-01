def def_conn():
    import sys, os

    from database.database import sqlconnection, sqltable
    conn = sqlconnection()
    sqltable(conn)
    return conn
