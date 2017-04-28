import GDAX
import eth.gdax_msg as gmsg
import eth.gdax_keys as gdax_keys
import eth.gdax_priv as gdax_priv
import eth.num_utils as num_utils
import os

class WsClient(GDAX.WebsocketClient):
    def __init__(self):
        GDAX.WebsocketClient.__init__(self, products=['ETH-USD'])
        self.onOpenCB = None
        self.onMessageCB = None
        self.onCloseCB = None
    def onMessage(self, msg):
        typ = msg['type']
        if(typ == "received"):
            res = gmsg.ReceivedMessage(msg)
        elif(typ == "match"):
            res = gmsg.MatchMessage(msg)
        elif(typ == "done"):
            res = gmsg.DoneMessage(msg)
        elif(typ == "open"):
            res = gmsg.OpenMessage(msg)
        elif(typ == "change"):
            res = gmsg.ChangeMessage(msg)
        elif(typ == "error"):
            res = gmsg.ErrorMessage(msg)
        elif(typ == "heartbeat"):
            res = gmsg.HeartbeatMessage(msg)
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
            

class AuthClient(GDAX.AuthenticatedClient):
    def __init__(self, auth_path="~/.gdax"):
        fname = os.path.expanduser("~/.gdax")
        key, secret, passphrase = gdax_keys.GetAPIKeys(fname)
        GDAX.AuthenticatedClient.__init__(self, key, secret, passphrase, product_id='ETH-USD')
        
    def getAccounts(self):
        msg = GDAX.AuthenticatedClient.getAccounts(self)
        return {x['currency']: gdax_priv.Account(x) for x in msg}
    
    def getAccount(self, accountId):
        x = GDAX.AuthenticatedClient.getAccount(self, accountId)
        return gdax_priv.Account(x)
    
    def getAccountHistory(self, accountId):
        x = GDAX.AuthenticatedClient.getAccountHistory(self, accountId)
        return [gdax_priv.AccountHistoryItem(y) for y in x[0]]
    
    def getAccountHolds(self, accountId):
        x = GDAX.AuthenticatedClient.getAccountHolds(self, accountId)
        return [gdax_priv.AccountHoldItem(y) for y in x[0]]
    
    def getOrders(self):
        msg = GDAX.AuthenticatedClient.getOrders(self)
        return [gdax_priv.OrderResponse(x) for x in msg[0]]
    
    def getOrder(self, orderId):
        msg = GDAX.AuthenticatedClient.getOrder(self, orderId)
        return gdax_priv.OrderResponse(msg)
    
    def getFills(self):
        msg = GDAX.AuthenticatedClient.getFills(self)
        return [gdax_priv.Fill(x) for x in msg[0]]
    
    def getProductTicker(self, json = None, product=''):
        msg = GDAX.AuthenticatedClient.getProductTicker(self, json, product)
        return gdax_priv.Ticker(msg)
    
    def getProductHistoricRates(self, json=None, product='', start=None, end=None,granularity=None):
        msg = GDAX.AuthenticatedClient.getProductHistoricRates(self, json, product, 
                    start.isoformat() if start else None,
                    end.isoformat() if end else None,
                    str(granularity))
        return [gdax_priv.RateInfo(x) for x in msg]
 
    def getProductOrderBook(self, json=None, level=2, product=''):
        msg = GDAX.AuthenticatedClient.getProductOrderBook(self,json, level, product)
        return gdax_priv.OrderBook(msg)
        
    def getProductTrades(self, json = None, product='', before=None, after=None, limit=None):
        msg = GDAX.AuthenticatedClient.getProductTrades(self, json, product, before=before, after=after, limit=limit)
        return [gdax_priv.Trade(x) for x in msg]
        
 
    def buy(self, buy_params):
        d = buy_params.ToDict()
        msg = GDAX.AuthenticatedClient.buy(self,d)
        return gdax_priv.OrderResponse(msg)
            
    
    def sell(self, sell_params):
        d = sell_params.ToDict()
        msg = GDAX.AuthenticatedClient.sell(self,d)
        return gdax_priv.OrderResponse(msg)

        
    def cancelOrder(self, order_id = ''):
        msg = GDAX.AuthenticatedClient.cancelOrder(self,order_id)
        return msg
#







if __name__ == "__main__":
    auth = AuthClient()
















