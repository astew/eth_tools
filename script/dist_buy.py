#!/usr/bin/python3
import sys
import eth.gdax_client as gcl
import eth.gdax_priv as gpr
import eth.num_utils as nu
import time
import argparse
import numpy as np

if (__name__ != '__main__'):
    print("This should only be called as a script.")
    sys.exit(1)


parser = argparse.ArgumentParser(description='Place a set of ETH buy orders distributed over a price range.')

group1 = parser.add_mutually_exclusive_group()

group1.add_argument("--high", action="store_const", dest="price_hilo", const="high", 
        help="Use this flag to indicate higher-priced orders have greater volume (Default)")
group1.add_argument("--low", action="store_const", dest="price_hilo", const="low", 
        help="Use this flag to indicate lower-priced orders have greater volume")

group2 = parser.add_mutually_exclusive_group()
group2.add_argument('--flat', action='store_const', dest="vol_dist", const="flat", 
        help='Use this flag to indicate that the order volumes should be uniformly distributed (Default)')
group2.add_argument('--exp', action='store_const', dest='vol_dist', const='exp',
        help='Use this flag to indicate that the order volumes should be exponentially distributed')
group2.add_argument('--lin', action='store_const', dest='vol_dist', const='lin',
        help='Use this flag to indicate that the order volumes should be linearly distributed')

parser.add_argument('total_amount', type=float, help='The amount of USD to convert to ETH')
parser.add_argument('min_bid',type=float, help='The lower bound for bid price')
parser.add_argument('max_bid',type=float, help='The upper bound for bid price')
parser.add_argument('n_orders',type=int, help='Number of orders to create',nargs='?', default=None)

parser.set_defaults(price_hilo='high')
parser.set_defaults(vol_dist='flat')

args = parser.parse_args()

if(args.n_orders == None):
    args.n_orders = int((args.max_bid-args.min_bid)*100)

#make sure that max_bid and min_bid are at least n_orders
#cents apart
if(np.round((args.max_bid-args.min_bid)*100) < args.n_orders-1):
    print("Constraint violation: 100*(max_bid-min_bid) < n_orders-1")
    print("min_bid and max_bid must be far enough apart such that no two orders will have the same price")
    sys.exit(2)

#let's check that we have enough USD to place this order

auth = gcl.AuthClient()

usd_acct = auth.getAccounts()['USD']

if(usd_acct.available < args.total_amount):
    print("Insufficient USD in account.")
    print("Balance: $%.2f" % usd_acct.balance)
    print("Available: $%.2f" % usd_acct.available)
    sys.exit(1)

#find our set of prices:
prices = np.linspace(args.min_bid, args.max_bid, args.n_orders)

#find our set of weights

if(args.vol_dist == 'flat'):
    weights = np.ones(args.n_orders)    
elif(args.vol_dist == 'lin'):
    weights = np.linspace(1, 100, args.n_orders)
elif(args.vol_dist == 'exp'):
    weights = np.exp(np.linspace(1, 3, args.n_orders))
else:
    print("Invalid volume distribution type.")
    sys.exit(4)

weights = weights / float(np.sum(weights))

if(args.price_hilo == 'low'):
    weights = np.fliplr([weights])[0]

price_weights = weights*args.total_amount
prices = np.asarray([np.round(x,2) for x in prices])

volumes = price_weights / prices
volumes = np.asarray([nu.floor_size(x) for x in volumes])

orders = []

print("Total cost: $%.2f" % np.sum(prices*volumes))
print("Total value if all bought: %f ETH" % np.sum(volumes))

for price,size in zip(prices, volumes):
    params = gpr.LimitOrderParams(price, size, side='buy')

    print("Placing order: %s" % params)
    order =  auth.buy(params)

    if(order.isError):
        #error placing order
        #cancel all previous orders
        print("... error placing order: %s" % order)
        sys.exit(3)

        for o in orders:
            print("Canceling %s" % o.id)
            auth.cancelOrder(o.id)
            time.sleep(0.25)


    orders.append(order)
    time.sleep(0.18)

print("Orders placed:")
for o in orders:
    print(o)

