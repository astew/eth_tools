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


parser.add_argument('volume', type=float, help='The amount of USD to spend or ETH to buy')
parser.add_argument('price',type=float, help='The bid price')

parser.set_defaults(vol_type='vol_usd')

args = parser.parse_args()


#let's check that we have enough USD to place this order
auth = gcl.AuthClient()
usd_acct = auth.getAccounts()['USD']

if(args.vol_type == 'vol_usd'):
    usd_cost = args.volume
else:
    usd_cost = args.volume*args.price

if(usd_acct.available < usd_cost):
    print("Insufficient USD in account.")
    print("Balance: $%.2f" % usd_acct.balance)
    print("Available: $%.2f" % usd_acct.available)
    sys.exit(1)

size = args.volume if(args.vol_type == 'vol_eth') else args.volume / args.price

size = nu.floor_size(size)

print("Total cost: $%.2f" % usd_cost)
print("Total value if all bought: %f ETH" % size)

params = gpr.LimitOrderParams(args.price, size, side='buy')

print("Placing order: %s" % params)

order = auth.buy(params)

if(order.isError):
    print("... error placing order: %s" % order)
else:
    print("... order placed: %s" % order)

