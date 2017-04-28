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


parser = argparse.ArgumentParser(description='Place a single ETH buy orders at a specified price.')

group1 = parser.add_mutually_exclusive_group()

group1.add_argument("-e", "--eth", action="store_const", dest="vol_type", const="vol_eth", 
        help="Use this flag to indicate the volume is specified in ETH, rather than USD.")
group1.add_argument("-u", "--usd", action="store_const", dest="vol_type", const="vol_usd", 
        help="Use this flag to indicate the volume is specified in USD, rather than ETH (default)")


parser.add_argument('volume', type=str, help='The amount of USD to spend or ETH to buy. If "all" is specified, all available USD will be used.')
parser.add_argument('bid_price',type=float, help='The bid price to buy at')
parser.add_argument("ask_price",type=float, help='The ask price to sell at')

parser.set_defaults(vol_type='vol_usd')

args = parser.parse_args()


#let's check that we have enough USD to place this order
auth = gcl.AuthClient()
usd_acct = auth.getAccounts()['USD']

if(args.volume == 'all'):
    args.volume = usd_acct.available
    args.vol_type = "vol_usd"
else:
    args.volume = float(args.volume)

if(args.vol_type == 'vol_usd'):
    usd_cost = args.volume
else:
    usd_cost = args.volume*args.price

if(usd_acct.available < usd_cost):
    print("Insufficient USD in account.")
    print("Balance: $%.2f" % usd_acct.balance)
    print("Available: $%.2f" % usd_acct.available)
    sys.exit(1)

size = args.volume if(args.vol_type == 'vol_eth') else args.volume / args.bid_price

size = nu.floor_size(size)

print("Total cost: $%.2f" % usd_cost)
print("Total value if all bought: %f ETH" % size)

params = gpr.LimitOrderParams(args.bid_price, size, side='buy')

print("Placing buy order: %s" % params)

order = auth.buy(params)

if(order.isError):
    print("... error placing order: %s" % order)
    sys.exit(-1)
else:
    print("... order placed: %s" % order)
    print("Order ID: %s" % order.id)


order_id = order.id

while(True):
    order = auth.getOrder(order_id)

    if(order.isError):
        print("Error occurred: %s" % order)
        sys.exit(-1)

    if(order.status == 'done'):
        print("ETH bought!")
        break
    elif(order.status != 'open'):
        print("Error. Unknown status: %s" % order.status)
        sys.exit(-1)

    time.sleep(5.0)

print("Selling the ETH..")

params = gpr.LimitOrderParams(args.ask_price, size, side='sell')

print("Placing sell order: %s" % order)

order = auth.sell(params)

if(order.isError):
    print("... error placing order: %s" % order)
    sys.exit(-1)
else:
    print("... order placed: %s" % order)
    print("Order ID: %s" % order.id)


order_id = order.id

while(True):
    order = auth.getOrder(order_id)

    if(order.isError):
        print("Error occurred: %s" % order)
        sys.exit(-1)

    if(order.status == 'done'):
        print("ETH sold!")
        break
    elif(order.status != 'open'):
        print("Error. Unknown status: %s" % order.status)
        sys.exit(-1)

    time.sleep(5.0)
















