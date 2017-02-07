
import numpy as np
import GDAX
from dateutil import parser
import time
import eth.num_utils as num_utils



class Account():
    """
    Represents a single user account.
    """
    def __init__(self, msg):
        self.original_msg = msg
        self.id = msg['id']
        self.currency = msg['currency']
        self.balance = float(msg['balance'])
        self.available = float(msg['available'])
        self.hold = float(msg['hold'])
        self.profile_id = msg['profile_id']
	
    def __str__(self):
        return "(%s) Balance: %f\tAvailable: %f\t [%s]" % (self.currency, self.balance, self.available, self.id)
    def __repr__(self):
        return self.__str__()

class AccountHistoryItem():
    """Represents a single record in an account history"""
    def __init__(self, msg):
        self.original_msg = msg
        self.id = msg['id']
        self.created_at = parser.parse(msg['created_at'])
        self.amount = float(msg['amount'])
        self.balance = float(msg['balance'])
        self.type = msg['type']
        self.details = msg.get('details')
	
    def __str__(self):
        return "(%s) %s: %f\t [%s]" % (self.created_at, self.type, self.amount, self.id)
    def __repr__(self):
        return self.__str__()
        
class AccountHholdItem():
    """Represents a single account hold"""
    def __init__(self, msg):
        self.original_msg = msg
        self.id = msg['id']
        self.account_id     = msg['account_id']
        self.created_at     = parser.parse(msg['created_at'])
        self.updated_at     = parser.parse(msg['updated_at'])
        self.amount         = float(msg['amount'])
        self.type           = msg['type']
        self.ref            = msg['ref']
	
    def __str__(self):
        return "(%s) %s: %f\t [%s]" % (self.created_at, self.type, self.amount, self.id)
    def __repr__(self):
        return self.__str__()
        
        

        
class LimitOrderParams():
    def __init__(self, price, size, side = 'buy', product_id = 'ETH-USD'):
        self.side = side
        self.product_id = product_id
        self.size = size
        self.price = price
        self.post_only = True
        
    def ToDict(self):
        res = dict()
        res['side'] = self.side
        res['product_id'] = self.product_id
        res['type'] = 'limit'
        res['size'] = "%.6f" % self.size
        res['price'] = "%.2f" % self.price
        res['post_only'] = self.post_only
        return res;
	
    def __str__(self):
        return "%s: %f ETH @ $%f (limit)" % (self.side, self.size, self.price)
    def __repr__(self):
        return self.__str__()
                
class MarketOrderParams():
    def __init__(self, funds = None, size = None, side = 'buy', product_id = 'ETH-USD'):
        self.side = side
        self.product_id = product_id
        
        if((not size and not funds) or (size and funds)):
            raise "Error: only size xor funds may be specified."
            
        if(size):
            self.size = size
        elif(funds):
            self.funds = funds
        
    def ToDict(self):
        res = dict()
        res['side'] = self.side
        res['product_id'] = self.product_id
        res['type'] = 'market'
        
        if('size' in self.__dict__):
            res['size'] = self.size
        else:
            res['funds'] = self.funds
            
        return res;   
	
    def __str__(self):
        if('size' in self.__dict__):
            return "%s: %f ETH (market)" % (self.side, self.size)
        else:
            return "%s: $%f (market)" % (self.side, self.funds)
    def __repr__(self):
        return self.__str__()
        
class StopOrderParams():
    def __init__(self, price, size = None, funds = None, side = 'buy', product_id = 'ETH-USD'):
        self.side = side
        self.product_id = product_id
        self.price = price
        
        if((not size and not funds) or (size and funds)):
            raise "Error: only size xor funds may be specified."
        
        if(size):
            self.size = size
        elif(funds):
            self.funds = funds
        
    def ToDict(self):
        res = dict()
        res['side'] = self.side
        res['product_id'] = self.product_id
        res['type'] = 'stop'
        res['price'] = self.price
        
        if('size' in self.__dict__):
            res['size'] = self.size
        else:
            res['funds'] = self.funds
        return res;
	

    def __str__(self):
        if('size' in self.__dict__):
            return "%s: %f ETH @ %f (stop)" % (self.side, self.size, self.price)
        else:
            return "%s: $%f @ %f(stop)" % (self.side, self.funds, self.price)
    def __repr__(self):
        return self.__str__()
    
class OrderResponse():
    def __init__(self, msg):
        
        self.original_msg = msg
        
        if('message' in msg):
            self.isError = True
            self.message = msg['message']
        else:
            self.isError = False
            self.id = msg['id']
            self.price = float(msg['price'])
            self.size = float(msg['size'])
            self.product_id = msg['product_id']
            self.side = msg['side']
            self.stp = msg.get('stp')
            self.type = msg['type']
            self.time_in_force = msg.get('time_in_force')
            self.post_only = bool(msg.get('post_only'))
            self.created_at = parser.parse(msg['created_at'])
            self.fill_fees = float(msg['fill_fees'])
            self.filled_size = float(msg['filled_size'])
            self.executed_value = float(msg['executed_value'])
            self.status = msg['status']
            self.settled = bool(msg['settled'])
	
    def __str__(self):
        if(self.isError):
            return "Error: %s" % self.message
        else:
            return "(%s) %s: %f ETH @ $%f\t(%s)" % (self.type, self.side, self.size, self.price, self.status)
    def __repr__(self):
        return self.__str__()
        
        
class Fill():
    def __init__(self, msg):
        self.original_msg = msg
        self.trade_id     = (msg['trade_id'])
        self.product_id   = (msg['product_id'])
        self.price        = float(msg['price'])
        self.size         = float(msg['size'])
        self.order_id     = (msg['order_id'])
        self.created_at   = parser.parse(msg['created_at'])
        self.liquidity    = (msg['liquidity'])
        self.fee          = float(msg['fee'])
        self.settled      = bool(msg['settled'])
        self.side         = (msg['side'])
	
    def __str__(self):
        return "%s: %f ETH @ $%f" % (self.side, self.size, self.price)
    def __repr__(self):
        return self.__str__()
        
class Trade():
    def __init__(self, msg):
        self.original_msg = msg
        self.price = float(msg['price'])
        self.side = msg['side']
        self.size = float(msg['size'])
        self.time = parser.parse(msg['time'])
        self.trade_id = msg['trade_id']
	
    def __str__(self):
        return "(%s) %f ETH @ $%f" % (self.time, self.size, self.price)
    def __repr__(self):
        return self.__str__()
        
class Ticker():
    def __init__(self, msg):
        self.original_msg = msg
        self.ask = float(msg['ask'])
        self.buy = float(msg['bid'])
        self.price = float(msg['price'])
        self.volume = float(msg['volume'])
        self.size = float(msg['size'])
        self.time = parser.parse(msg['time'])
        self.trade_id = msg['trade_id']
	
    def __str__(self):
        return "%s: $%f (A/B: $%f/$%f) (V: %f)" % (self.time, self.price, self.ask, self.buy, self.volume)
    def __repr__(self):
        return self.__str__()
#

class RateInfo():
    def __init__(self, msg):
        self.time = int(msg[0])
        self.low = float(msg[1])
        self.high = float(msg[2])
        self.open = float(msg[3])
        self.close = float(msg[4])
        self.volume = float(msg[5])
	
    def __str__(self):
        return "H:%f|L:%f|O:%f|C:%f|V:%f (%s)" % (self.high, self.low, self.open, self.close, self.volume, self.time)
    def __repr__(self):
        return self.__str__()

class SimpleOrder():
    def __init__(self, msg = None, level = 2):
        self.price = float(msg[0]) if msg else 0.0
        self.size = float(msg[1]) if msg else 0.0
        
        if(level == 2):
            self.num_orders = int(msg[2]) if msg else 0
        if(level == 3):
            self.order_id = msg[2] if msg else None

class OrderBook():
    def __init__(self, msg):
        self.sequence = int(msg['sequence'])
        self.bids = [SimpleOrder(x, level=2) for x in msg['bids']]
        self.asks = [SimpleOrder(x, level=2) for x in msg['asks']]

    def getBestPrices(self):
        """Returns best bid/ask"""
        return (np.max([x.price for x in self.bids]),
                np.min([x.price for x in self.asks]))
        
    def getMidMarketPrice(self):
        return (np.min([x.price for x in self.asks]) 
              + np.max([x.price for x in self.bids])) / 2.0














