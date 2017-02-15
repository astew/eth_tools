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


parser = argparse.ArgumentParser(description='Place a set of ETH sell orders distributed over a price range.')


group1 = parser.add_mutually_exclusive_group()
group1.add_argument("-h", "--high", action="store_const", dest="price_hilo", const="high",
                help="Use this flag to indicate higher-priced orders have greater volume")
group1.add_argument("-l", "--low", action="store_const", dest="price_hilo", const="low",
                help="Use this flag to indicate lower-priced orders have greater volume (Default)")

group2 = parser.add_mutually_exclusive_group()
group2.add_argument('-f', '--flat', action='store_const', dest="vol_dist", const="flat",
                help='Use this flag to indicate that the order volumes should be uniformly distributed (Default)')
group2.add_argument('-x', '--exp', action='store_const', dest='vol_dist', const='exp',
                help='Use this flag to indicate that the order volumes should be exponentially distributed')
group2.add_argument('-n', '--lin', action='store_const', dest='vol_dist', const='lin',
                help='Use this flag to indicate that the order volumes should be linearly distributed')

parser.add_argument('total_amount', type=float, help='The amount of ETH to sell')
parser.add_argument('min_ask',type=float, help='The lower bound for ask price')
parser.add_argument('max_ask',type=float, help='The upper bound for ask price')
parser.add_argument('n_orders',type=int, help='Number of orders to create',nargs='?', default=None)

parser.set_defaults(price_hilo="low")
parser.set_defaults(vol_dist="flat")

args = parser.parse_args()

if(args.n_orders == None):
    args.n_orders = int((args.max_ask-args.min_ask)*100)

#make sure that max_ask and min_ask are at least n_orders
#cents apart
if(np.round((args.max_ask-args.min_ask)*100) < args.n_orders-1):
    print("Constraint violation: 100*(max_ask-min_ask) < n_orders-1")
    print("min_ask and max_ask must be far enough apart such that no two orders will have the same price")
    sys.exit(2)

#let's check that we have enough ETH to place this order

auth = gcl.AuthClient()

eth_acct = auth.getAccounts()['ETH']

if(eth_acct.available < args.total_amount):
    print("Insufficient ETH in account.")
    print("Balance: %f ETH" % eth_acct.balance)
    print("Available: %f ETH" % eth_acct.available)
    sys.exit(1)

#find our set of prices:
prices = np.linspace(args.min_ask, args.max_ask, args.n_orders)

#find our set of weights

if(args.vol_dist == "flat"):
    weights = np.ones(args.n_orders)
elif(args.vol_dist == "lin"):
    weights = np.arange(1, args.n_orders)
elif(args.vol_dist == "exp"):
    weights = np.exp(np.linspace(1, 3, args.n_orders))
else:
    print("Invalid volume distribution type.")
    sys.exit(4)

weights = weights / float(np.sum(weights))

if(args.price_hilo == "low"):
    weights = np.fliplr([weights])[0]

volumes = weights*args.total_amount

prices = np.asarray([np.round(x,2) for x in prices])
volumes = np.asarray([nu.floor_size(x) for x in volumes])

print("Total value if all sold: $%.2f" % np.sum(prices*volumes))

orders = []

for price,size in zip(prices, volumes):
    params = gpr.LimitOrderParams(price, size, side='sell')

    print("Placing order: %s" % params)
    order =  auth.sell(params)

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

