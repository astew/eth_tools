
import GDAX
import eth.gdax_priv as gdax_priv
from eth.gdax_msg import *
import queue
import threading
import numpy as np

class WsClient(GDAX.WebsocketClient):
    def __init__(self):
        GDAX.WebsocketClient.__init__(self, products=['ETH-USD'])
        self.onOpenCB = None
        self.onMessageCB = None
        self.onCloseCB = None
    def onMessage(self, msg):
        typ = msg['type']
        if(typ == "received"):
            res = ReceivedMessage(msg)
        elif(typ == "match"):
            res = MatchMessage(msg)
        elif(typ == "done"):
            res = DoneMessage(msg)
        elif(typ == "open"):
            res = OpenMessage(msg)
        elif(typ == "change"):
            res = ChangeMessage(msg)
        elif(typ == "error"):
            res = ErrorMessage(msg)
        elif(typ == "heartbeat"):
            res = HeartbeatMessage(msg)
        else:
            print("Unknown message type:", typ)
            print(msg)
        
        if(self.onMessageCB):
            self.onMessageCB(res)
            
    def onOpen(self):
        if(self.onOpenCB):
            self.onOpenCB()
            
    def onClose(self):
        if(self.onCloseCB):
            self.onCloseCB()


            
class RealTimeOrderBook():
    def __init__(self, authClient):
        self.authClient = authClient
        self.wsClient = WsClient()
        self.wsClient.onOpenCB = self.__onOpen
        self.wsClient.onCloseCB = self.__onClose
        self.wsClient.onMessageCB = self.__handleMessage
        self.keep_going = False
        self.connected = False
        self.lock = threading.Lock()
    
    def __onOpen(self):
        self.connected = True
    def __onClose(self):
        self.connected = False
    def __handleMessage(self, msg):
        self.msg_queue.put(msg)
    
    def __processQueue(self):
        while(self.keep_going):
            try:
                msg = self.msg_queue.get(block = True, timeout = 1)
            except queue.Empty:
                #nothing in queue at the moment, loop around to see if we
                #should quit
                continue
            
            self.lock.acquire()
            if(self.sequence < msg.sequence):
                
                try:
                    self.__processMessage(msg)
                    self.sequence = msg.sequence
                    
                    #occasionally verify the state of our book
                    if(self.sequence % 100 == 0):
                        assert(all([x > 0 for x in self.asks.keys()]))
                        assert(all([x > 0 for x in self.bids.keys()]))
                        assert(all([x.price > 0 for x in self.asks.values()]))
                        assert(all([x.price > 0 for x in self.bids.values()]))
                        assert(all([x.size >= 0 for x in self.asks.values()]))
                        assert(all([x.size >= 0 for x in self.bids.values()]))
                        assert(all([x.num_orders >= 0 for x in self.asks.values()]))
                        assert(all([x.num_orders >= 0 for x in self.bids.values()]))
                except Exception as e:
                    self.lock.release()
                    print("An error occurred while processing a message: {0}".format(e))
                    print("Stopping")
                    self.stop()
                    return

            self.lock.release()
    
    def __processMessage(self, msg):
        if(isinstance(msg, ReceivedMessage)):
            #do nothing
            return
        elif(isinstance(msg, MatchMessage)):
            #match occurred
            
            if(msg.side == 'sell'):
                if(not (msg.price in self.asks)):
                    print(msg.original_msg)
                    print(self.asks)
                    raise Exception("ERROR: match was made without an entry in our book to subtract from.")
                
                so = self.asks[msg.price]
                so.size -= msg.size
                self.asks[msg.price] = so
            elif(msg.side == 'buy'):
                if(not (msg.price in self.bids)):
                    print( msg.original_msg)
                    print( self.bids)
                    raise Exception("ERROR: match was made without an entry in our book to subtract from.")
                
                so = self.bids[msg.price]
                so.size -= msg.size
                self.bids[msg.price] = so
            else:
                raise Exception("ERROR: received MatchMessage with unknown side: %s" % msg.side)
            
        elif(isinstance(msg, OpenMessage)):
            #new order is on the book
            
            if(msg.side == 'sell'):
                if(not (msg.price in self.asks)):
                    self.asks[msg.price] = gdax_priv.SimpleOrder()
                
                so = self.asks[msg.price]
                so.size += msg.remaining_size
                so.num_orders += 1
                self.asks[msg.price] = so
            elif(msg.side == 'buy'):
                if(not (msg.price in self.bids)):
                    self.bids[msg.price] = gdax_priv.SimpleOrder()
                
                so = self.bids[msg.price]
                so.size += msg.remaining_size
                so.num_orders += 1
                self.bids[msg.price] = so
            else:
                raise Exception("ERROR: received OpenMessage with unknown side: %s" % msg.side)
            
        elif(isinstance(msg, DoneMessage)):
            #if the DoneMessage has a price or remaining_size, then it was in the order book
            #and should reduce num_orders
            if( not ('price' in msg.__dict__)):
                return
                
            if(msg.side == 'sell'):
                if(not (msg.price in self.asks)):
                    print( msg.original_msg)
                    print( self.asks)
                    raise Exception("ERROR: match was made without an entry in our book to subtract from.")
                
                so = self.asks[msg.price]
                so.num_orders -= 1
                
                if(so.num_orders <= 0):
                    self.asks[msg.price] = so
                else:
                    self.asks.pop(msg.price)
            elif(msg.side == 'buy'):
                if(not (msg.price in self.bids)):
                    print( msg.original_msg)
                    print( self.bids)
                    raise Exception("ERROR: match was made without an entry in our book to subtract from.")
                
                so = self.bids[msg.price]
                so.num_orders -= 1
                if(so.num_orders <= 0):
                    self.bids[msg.price] = so
                else:
                    self.bids.pop(msg.price)
            else:
                raise Exception("ERROR: received DoneMessage with unknown side: %s" % msg.side)
                
        elif(isinstance(msg, ChangeMessage)):
            #I'm not really sure what should be done here...
            #the GDAX API isn't really clean on when these can be ignored
            #and when they cannot be
            return
        else:
            return
            #don't care
        
    def __initializeFromOrderBook(self, book):
        print(book)
        self.sequence = book.sequence
        self.asks = {x.price: x for x in book.asks}
        self.bids = {x.price: x for x in book.bids}
    
    def start(self):
        self.lock.acquire()
        self.msg_queue = queue.Queue()
        #start the wsClient
        self.wsClient.start()
        self.keep_going = True
        
        #grab a copy of the order book (level 2 should be fine..?)
        self.__initializeFromOrderBook(self.authClient.getProductOrderBook(level=2))
        
        #now start the message processing thread
        self.msg_thread = threading.Thread(target = self.__processQueue, 
                                            name = "__processQueue")
        self.msg_thread.start()
        
        self.lock.release()
        
    def stop(self):
        if(self.keep_going):
            self.lock.acquire()
            self.keep_going = False
            
            #for some reason this crashes us
            #self.wsClient.close()
            
            self.msg_thread.join()
            
            self.asks = None
            self.bids = None
            self.sequence = None
            self.lock.release()
    
    def isConnected(self):
        self.lock.acquire()
        res = self.connected
        self.lock.release()
        return res
    
    def getBestAsk(self):
        self.lock.acquire()
        res = np.min([x for x in self.asks.keys() if self.asks[x].size > 0])
        self.lock.release()
        return res
        
    def getBestBid(self):
        self.lock.acquire()
        res = np.max([x for x in self.bids.keys() if self.bids[x].size > 0])
        self.lock.release()
        return res
#


















