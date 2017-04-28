
import numpy as np
from eth.gdax_priv import *
from eth.gdax_client import *
from eth.gdax_msg import *
import eth.num_utils as nu
import time
from datetime import datetime, timedelta

def Print(txt):
    if(do_print):
        now = datetime.now()
        nowstr = now.strftime("%m/%d %H:%M:%S")
        print("%s -- %s" % (nowstr, txt))

def DoBuy(auth, price, size):
    params = LimitOrderParams(price = price, size = size, side = 'buy')
    return auth.buy(params)

def DoSell(auth, price, size):
    params = LimitOrderParams(price = price, size = size, side = 'sell')
    return auth.sell(params)

def PerformOrder(auth, price, size, poll_interval = 5.0, order_side=None, completion_callback = None , do_print = True):
    if(order_action != 'buy' and order_action != 'sell'):
        raise Exception("Order side must be specified.")

    if(do_print):
        Print("Placing %s order: %.4f ETH @ $%.2f" % (order_side, params.size, params.price))

    if(order_side == 'buy'):
        order = auth.DoBuy(price, size)
    else:
        order = auth.DoSell(price, size)

    if(order.isError):
        raise Exception("Error placing order: %s" % order)
    
    oid = order.id

    err_attempts = 3

    while(True):
        time.sleep(poll_interval)
        order = auth.getOrder(oid)
       
        
        if(order.isError):
            err_attempts -= 1
            if(err_attempts == 0):
                raise Exception("Error retrieving order info: %s" % order)
            continue
        else:
            err_attempts = 3

        if(order.status == 'open'):
            continue
        elif(order.status == 'done'):
            if(do_print):
                Print("The %s order has completed." % order_side)
            if(completion_callback != None):
                return completion_callback(auth, price, size)
        else:
            raise Exception("Received order status other than 'open' or 'done': %s" % order.status)


def PerformBuy(auth, price, size, poll_interval = 5.0, completion_callback = None ,do_print = True):
    PerformOrder(auth, price, size, 
            poll_interval = poll_interval, 
            completion_callback = completion_callback, 
            do_print = do_print, 
            order_side = 'buy')


def PerformSell(auth, price, size, poll_interval = 5.0, completion_callback = None ,do_print = True):
    PerformOrder(auth, price, size, 
            poll_interval = poll_interval, 
            completion_callback = completion_callback, 
            do_print = do_print, 
            order_side = 'sell')

def PerformBuySell(auth, buy_price, sell_price, size, poll_interval = 5.0, completion_callback = None, do_print = True):
    PerformBuy(auth, buy_price, size, poll_interval = poll_interval, do_print = do_print)
    PerformSell(auth, sell_price, size, poll_interval = poll_interval, do_print = do_print, completion_callback = completion_callback)

    
