import os
import sqlite3 as sql

dataDir = "Data"
dbName = "NSHL.db" 

def connect():
    #create connection, create db if doesn't exist
    conn = None
    try:
        conn = sql.connect(os.path.join(data_dir, dbName))

        # enable write-ahead log for performance and resilience
        conn.execute('pragma journal_mode=wal')

        return conn
    except:
        print("oops, db connection no work")
        return conn
