

import sqlite3
import eth.gdax_msg as gm
import datetime
import numpy as np


class Match():

    Cols = {
            "id": 0,
            "side": 1,
            "time": 2,
            "price": 3,
            "size": 4,
            "trade_id": 5
            }

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
        CREATE TABLE Match(
            id INTEGER PRIMARY KEY, 
            side TEXT, 
            time INTEGER, 
            price REAL, 
            size REAL, 
            trade_id TEXT)
        ''')

        #just the one table for now
        db.commit()

    return db

class Trade():
    def __init__(self, id, side, time, price, size, trade_id):
        self.id = id
        self.side = side
        self.time = time
        self.price = price
        self.size = size
        self.trade_id = trade_id

    def FromDbRow(row):
        return Trade(
                row[Match.Cols['id']],
                row[Match.Cols['side']],
                row[Match.Cols['time']],
                row[Match.Cols['price']],
                row[Match.Cols['size']],
                row[Match.Cols['trade_id']],
                )        

class Candle():
    def __init__(self, startTime, endTime, trades):
        self.high = np.max(trades, key=lambda x: x.price)
        self.low = np.min(trades, key=lambda x: x.price)
        self.open = None if len(trades == 0) else trades[0].price
        self.close = None if len(trades == 0) else trades[len(trades)-1].price
        self.totalVolume = np.sum([x.size for x in trades])
        self.mean = np.sum([x.price*x.size for x in trades]) / self.totalVolume
        self.buyVolume = np.sum([x.size for x in trades if x.side=='sell'])
        self.sellVolume = np.sum([x.size for x in trades if x.side=='buy'])
        self.startTime = startTime
        self.endTime = endTime

class DbWrapper():
    def __init__(self, db_conn):
        self.db = db_conn

    def GetLargestTradeId(self):
        c = self.db.cursor()
        
        c.execute('''SELECT trade_id FROM Match''')
        
        x = np.max([int(x[0]) for x in c.fetchall()])
        
        return x
        
    def InsertMatch(self, msg, onlyInsertNew = True):
        c = self.db.cursor()
        
        if(onlyInsertNew):
            c.execute('''
            SELECT * FROM Match WHERE trade_id like :trade_id
            ''', msg.__dict__)
            
            if(len(c.fetchall()) > 0):
                #It's already in there. abort!
                return
        
        c.execute('''
        INSERT INTO Match(side, time, price, size, trade_id)
        VALUES (:side, :time, :price, :size, :trade_id)
        ''', msg.__dict__)

        self.db.commit()

    def GetMatch(self, id):
        c = self.db.cursor()
        c.execute('''SELECT * FROM Match WHERE id=?''', [id])
        return Trade(c.fetchone())

    def GetMatches_ByTime(self, startTime=None, endTime= None, action = None):
        """Get all Matches between two times. Times must be datetimes."""
        if(not startTime):
            startTime = datetime.datetime.fromtimestamp(0)
        if(not endTime):
            endTime = datetime.datetime.now()
                
        c = self.db.cursor()
        c.execute('''SELECT * FROM Match WHERE time >= ? AND time <= ? ORDER BY time ASC''', [startTime, endTime] )

        if(not action):
            return [Trade(x) for x in c.fetchall()]

        res = c.fetchone()
        while(res!=None):
            action(Trade(res))
            res = c.fetchone()
    
    def GetCandle(self, startTime, endTime):
        trades = self.Getmatches_ByTime(startTime, endTime)
        return Candle(startTime, endTime, trades)

    def GetCandles(self, endTime, stepSize, periods, action = None):
        
        if(action == None):
            data = []
        for i in range(periods):
            start = endTime - stepSize
            candle = self.GetCandle(start,endTime)
            
            if(action == None):
                data.insert(0, candle)
            else:
                action(candle)
        
        if(action == None):
            return data









