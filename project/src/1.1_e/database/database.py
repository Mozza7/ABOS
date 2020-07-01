import sqlite3
from sqlite3 import Error
import os
from configparser import ConfigParser
from main_ import root_location

config_loc = root_location+'\\config.ini'
print(config_loc)
dconfig = ConfigParser()
dconfig.read(root_location+'\\config.ini')

config_database = dconfig.get('options', 'database_loc')
config_database_toggle = dconfig.get('options', 'database_loc_on')

if config_database_toggle == 'NO':
    dbDir = os.path.abspath(os.path.join(os.getcwd(), 'sql\\aboscust.db'))
else:
    print('Database location = ' + config_database)
    dbDir = config_database


def sqlconnection():
    if config_database is None:
        try:
            conn = sqlite3.connect(dbDir + '\\aboscust.db')
            print(sqlite3.version)
            return conn
        except Error as e:
            print(e)
    else:
        try:
            conn = sqlite3.connect(dbDir)
            print(sqlite3.version)
            return conn
        except Error as e:
            print(e)


def sqltable(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE customers(company text PRIMARY KEY, ip text, username text, password text)")
        conn.commit()
    except Error:
        print('Database connected')


if __name__ == '__main__':
    rootLoc = os.path.abspath(os.path.join(os.getcwd(), '..'))
