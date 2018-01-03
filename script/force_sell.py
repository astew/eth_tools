#!/usr/bin/python3
import sys
import eth.gdax_client as gcl
import eth.gdax_priv as gpr
import eth.num_utils as nu
import time

if (__name__ != '__main__'):
    print("This should only be called as a script.")
    sys.exit(1)

if(len(sys.argv) < 2):
    print("Error: missing arguments.")
    print("Usage: force_sell.py <funds>")
    sys.exit(1)



auth = gcl.AuthClient()

eth_acct = auth.getAccounts()['ETH']

if(sys.argv[1] == 'all'):
    size = eth_acct.available
elif(sys.argv[1].endswith('%')):
    size = eth_acct.available * float(sys.argv[1][:-1])/100.
else:
    size = float(sys.argv[1])

if(len(sys.argv) > 2):
    min_price = float(sys.argv[2])
    print("Min price set to $%.2f" % min_price)
else:
    min_price = 0.0

if(eth_acct.available < size):
    print("You have insufficient available funds to execute this action.")
    print("ETH Balance: %f ETH\t\tAvailable: %f ETH" % (eth_acct.balance, eth_acct.available))
    sys.exit(2)

print("Attempting to sell %f ETH." % size)

#The basic strategy here is going to be to find the current best sell
#price and put in our order for that amount, so we'll be one of the first
#to get processed.
#We'll track our order and the order book to see if our order has gone through.
#Or, if the buy price has changed, we'll cancel our order and put in another
#   at the new price.


while(size >= 0.00001):
    print("Attempting to place order for %f ETH" % size)
    #grab the order book
    book = auth.getProductOrderBook(level=1)
    #find our ask price
    best_bid, best_ask = book.getBestPrices()
    
    #best_ask = best_ask - 0.01 if (best_ask-best_bid > 0.02) else best_ask

    #create an order
    current_size = nu.floor_size(size) 
    prms = gpr.LimitOrderParams(best_ask, current_size, side='sell')

    prms.price = max(best_ask, min_price)

    print("Placing sell order: %s" % prms)
    order = auth.sell(prms)

    if(order.isError):
        print("...error placing order: %s" % order)
        sys.exit(4)
    else:
        print("...order placed: %s" % order)

    #now, loop until the status changes in
    #an important way (either we're done, or
    #we need to update the order)
    
    time.sleep(1)
    while(True):
        print("Checking order: %s" % order.id)
        order = auth.getOrder(order.id)
        
        if(order.isError):
            print("Error getting order status: %s" % order.message)
            print("This may be a result of the order being cancelled externally.")
            sys.exit(3)

        print("Status: %s\t\tFilled: %f ETH" % (order.status, order.filled_size))

        #check the status to see if it's been filled
        if(order.status == "done"):
            #great, we're done.
            print("Order completed!")
            size = size - order.filled_size
            break

        #order hasn't completed, check the current buy price
        book = auth.getProductOrderBook(level=1)
        _, ba = book.getBestPrices()
        
        #if ba is less than best_buy, we need to cancel the order
        #and create a new one
        if(ba < best_ask):
            #cancel the existing order
            print("Best ask has changed. Canceling order.")
            idd = order.id
            resp = None
            while(resp != [idd]):
                resp = auth.cancelOrder(order.id)
                time.sleep(0.5)

            #check if it filled at all
            order = auth.getOrder(order.id)
            if(order.isError and order.message=="NotFound"):
                fill_siz = 0.0
            else:
                fill_siz = order.filled_size
                    
            #subtract any filled funds
            size = size - fill_siz
            
            #now go back to the outer loop where we'll
            #place a new order
            break
        
        time.sleep(5)



        
