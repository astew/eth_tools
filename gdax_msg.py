
import numpy as np
import GDAX
from dateutil import parser

            

class Message:
    def __init__(self, msg):
        self.sequence = msg['sequence']
        self.product_id = msg['product_id']
        self.side = msg['side']
        self.time = parser.parse(msg['time'])
        self.original_msg = msg

class ReceivedMessage(Message):
    def __init__(self, msg):
        Message.__init__(self, msg)
        self.order_type = msg['order_type']
        self.order_id = msg['order_id']
        self.order_oid = msg.get('order_oid')
        self.size = float(msg['size'])
        self.funds = float(msg.get('funds')) if ('funds' in msg) else None
        self.client_oid = msg.get('client_oid')
    
    def __str__(self):
        if(self.funds):
            return "Received: %s: %d ETH @ $%f" % (self.side, self.funds, self.size)
        else:
            return "Received: %s: %d ETH" % (self.order_type, self.size )
        
class MatchMessage(Message):
    def __init__(self, msg):
        Message.__init__(self, msg)
        self.taker_order_id = msg['taker_order_id']
        self.price = float(msg['price'])
        self.trade_id = msg['trade_id']
        self.maker_order_id = msg['maker_order_id']
        self.size = float(msg['size'])
        
    def __str__(self):
        return "Match: %s: %f ETH @ $%f" % (self.side, self.size, self.price)

class DoneMessage(Message):
    def __init__(self, msg):
        Message.__init__(self, msg)
        self.order_id = msg['order_id']
        self.reason = msg['reason']
        self.price = float(msg.get('price')) if ('price' in msg) else None
        self.remaining_size = float(msg.get('remaining_size')) if ('remaining_size' in msg) else None
        
    def __str__(self):
        if(self.price):
            return "Done: %s: %f ETH @ $%f (%s)" % (self.order_id, self.remaining_size, self.price, self.reason)
        else:
            return "Done: %s: (%s)" % (self.order_id, self.reason)
        
class OpenMessage(Message):
    def __init__(self, msg):
        Message.__init__(self, msg)
        self.order_id = msg['order_id']
        self.price = float(msg['price'])
        self.remaining_size = float(msg['remaining_size'])
        
    def __str__(self):
        return "Open: %d ETH @ $%f (%s)" % (self.remaining_size, self.price, self.side)
        
        
class ChangeMessage(Message):
    def __init__(self, msg):
        Message.__init__(self, msg)
        self.order_id = msg['order_id']
        self.new_size = float(msg['new_size'])
        self.old_size = float(msg['old_size'])
        self.price = float(msg.get('price')) if ('price' in msg) else None
        
    def __str__(self):
        return "Change: %s" % (self.order_id)

class HeartbeatMessage:
    def __init__(self, msg):
        self.sequence = msg['sequence']
        self.product_id = msg['product_id']
        self.time = parser.parse(msg['time'])
        self.last_trade_id = msg['last_trade_id']
        
        
    def __str__(self):
        return "Heartbeat: %s" % (self.last_trade_id)
        
class ErrorMessage:
    def __init__(self, msg):
        self.message = msg['message']
        
    def __str__(self):
        return "Error: %s" % (self.message)
