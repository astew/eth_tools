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
    print("Usage: force_buy.py <funds>")
    sys.exit(1)



auth = gcl.AuthClient()

usd_acct = auth.getAccounts()['USD']

if(sys.argv[1] == 'all'):
    funds = usd_acct.available
elif(sys.argv[1].endswith('%')):
    funds = usd_acct.available * float(sys.argv[1][:-1])/100.
else:
    funds = float(sys.argv[1])

if(usd_acct.available < funds):
    print("You have insufficient available funds to execute this action.")
    print("USD Balance: $%.2f\t\tAvailable: $%.2f" % (usd_acct.balance, usd_acct.available))
    sys.exit(2)

print("Attempting to buy $%.2f worth of ETH." % funds)

#The basic strategy here is going to be to find the current greatest buy
#price and put in our order for that amount, so we'll be one of the first
#to get processed.
#We'll track our order and the order book to see if our order has gone through.
#Or, if the buy price has changed, we'll cancel our order and put in another
#   at the new price.


while(funds >= 0.01):
    print("Attempting to place order for $%.2f" % funds)
    #grab the order book
    book = auth.getProductOrderBook(level=1)
    #find our buy price
    best_buy, _ = book.getBestPrices()
    
    #create an order
    size = funds / best_buy
    size = nu.floor_size(size) 
    prms = gpr.LimitOrderParams(best_buy, size, side='buy')

    print("Placing buy order: %s" % prms)
    order = auth.buy(prms)

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

        print("Status: %s\t\tFilled: $%.2f" % (order.status, order.executed_value))

        #check the status to see if it's been filled
        if(order.status == "done"):
            #great, we're done.
            print("Order completed!")
            funds = funds - order.executed_value
            break

        #order hasn't completed, check the current buy price
        book = auth.getProductOrderBook(level=1)
        bb, _ = book.getBestPrices()
        
        #if bb is greater than best_buy, we need to cancel the order
        #and create a new one
        if(bb > best_buy):
            #cancel the existing order
            print("Best bid has increased. Canceling order.")
            idd = order.id
            resp = None
            while(resp != [idd]):
                resp = auth.cancelOrder(order.id)
                time.sleep(0.5)

            #check if it filled at all
            order = auth.getOrder(order.id)
            if(order.isError and order.message=="NotFound"):
                ex_val = 0.0
            else:
                ex_val = order.executed_value
                    
            #subtract any filled funds
            funds = funds - ex_val
            
            #now go back to the outer loop where we'll
            #place a new order
            break
        
        time.sleep(5)



        
