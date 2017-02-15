

import eth.db.structure as eds
import numpy as np
from datetime import datetime, timedelta

_defaultKey = lambda x: x.close

def SimpleMovingAverage(candleData, key = _defaultKey):
    return np.sum([key(x) for x in candleData])/len(candleData)
            
def ExpMovingAverage(candleData, startEMA = None, key = _defaultKey):
    if(startEMA == None):
        startEMA = key(candleData[0])

    mult = 2. / (len(candleData)+1)
    ema = startEMA

    emas = []

    for candle in candleData:
        val = key(candle)
        diff = val - ema
        ema = diff*mult + ema
        emas.append(ema)

    return emas

def MACD(candleData, macdShortPeriod = 10, macdLongPeriod = 26, signalPeriod = 9, key = _defaultKey):
    a = macdShortPeriod
    b = macdLongPeriod
    c = signalPeriod

    macdShort = np.concatenate((np.zeros(a-1),np.asarray(ExpMovingAverage(candleData[a:],key=key))))
    macdLong = np.concatenate((np.zeros(b-1), np.asarray(ExpMovingAverage(candleData[b:],key=key))))

    macd = macdShort - macdLong

    signal = np.concatenate((np.zeros(c-1), np.asarray(ExpMovingAverage(macd[b:],key=lambda x: x))))

    hist = macd - signal

    return (macd, signal, hist)

def RSI(candleData, rsiPeriod = 14, key = _defaultKey):
    N = len(candleData)
    if(N < rsiPeriod + 1):
        raise Exception("Not enough data to give any good results..")
    

    diffs = [key(y)-key(x) for (x,y) in zip(candleData[0:N-1],candleData[1:])]
    diffs.insert(0, 0)

    gains = [x if (x>0.0) else 0 for x in diffs]
    losses = [-x if (x<0.0) else 0 for x in diffs]

    ave_gain = np.sum(gains[0:rsiPeriod])/float(rsiPeriod)
    ave_loss = np.sum(losses[0:rsiPeriod])/float(rsiPeriod)

    rs = [0 for _ in range(rsiPeriod-1)]
    rs.append(ave_gain/ave_loss)

    for (gain,loss) in zip(gains[rsiPeriod:],losses[rsiPeriod:]):
        ave_gain = (ave_gain * (rsiPeriod-1) + gain)/rsiPeriod
        ave_loss = (ave_loss * (rsiPeriod-1) + loss)/rsiPeriod
        rs.append(ave_gain/ave_loss)

    rsi = np.asarray([100 - (100./(1+x)) for x in rs])

    return rsi






