

import sqlite3
import eth.gdax_msg as gm
import datetime

def Connect(fname):
    db = sqlite3.connect(fname)

    #check for structure
    cur = db.cursor()

    cur.execute('''
    SELECT name FROM sqlite_master WHERE type='table' AND name='Match'
    ''')

    if(not cur.fetchone()):
        #need to create tables
        cur.execute('''
        CREATE TABLE Match(id INTEGER PRIMARY KEY, sequence INTEGER, side TEXT, time INTEGER, price REAL, size REAL, taker_order_id TEXT, maker_order_id TEXT, trade_id TEXT)
        ''')

        #just the one table for now
        db.commit()

    return db

class DbWrapper():
    def __init__(self, db_conn):
        self.db = db_conn

    def InsertMatch(self, msg):
        c = self.db.cursor()
        c.execute('''
        INSERT INTO Match(sequence, side, time, price, size, taker_order_id, maker_order_id, trade_id)
        VALUES (:sequence, :side, :time, :price, :size, :taker_order_id, :maker_order_id, :trade_id)
        ''', msg.__dict__)

        self.db.commit()

    def GetMatch(self, id):
        c = self.db.cursor()
        c.execute('''SELECT * FROM Match WHERE id=?''', [id])
        return c.fetchone()

    def GetMatches_ByTime(self, startTime=None, endTime= None, action = None):
        """Get all Matches between two times. Times must be datetimes."""
        if(not startTime):
            startTime = datetime.datetime.fromtimestamp(0)
        if(not endTime):
            endTime = datetime.datetime.now()
                
        c = self.db.cursor()
        c.execute('''SELECT * FROM Match WHERE time >= ? AND time <= ?''', [startTime, endTime] )

        if(not action):
            return c.fetchall()

        res = c.fetchone()
        while(res!=None):
            action(res)
            res = c.fetchone()

