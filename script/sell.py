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


parser = argparse.ArgumentParser(description='Place a single ETH sell order at a specified price.')

group1 = parser.add_mutually_exclusive_group()

group1.add_argument("-e", "--eth", action="store_const", dest="vol_type", const="vol_eth", 
        help="Use this flag to indicate the volume is specified in ETH, rather than USD. (Default)")
group1.add_argument("-u", "--usd", action="store_const", dest="vol_type", const="vol_usd", 
        help="Use this flag to indicate the volume is specified in USD, rather than ETH.")


parser.add_argument('volume', type=float, help='The amount of ETH to sell or USD to recover')
parser.add_argument('price',type=float, help='The ask price')

parser.set_defaults(vol_type='vol_eth')

args = parser.parse_args()


#let's check that we have enough ETH to place this order
auth = gcl.AuthClient()
eth_acct = auth.getAccounts()['ETH']

if(args.vol_type == 'vol_eth'):
    eth_cost = args.volume
else:
    eth_cost = args.volume/args.price

if(eth_acct.available < eth_cost):
    print("Insufficient ETH in account.")
    print("Balance: $%.2f" % eth_acct.balance)
    print("Available: $%.2f" % eth_acct.available)
    sys.exit(1)

size = args.volume if(args.vol_type == 'vol_eth') else args.volume / args.price

size = nu.floor_size(size)
print("Total cost: $%.2f" % (size*args.price))
print("Total value if all sold: %f ETH" % size)

params = gpr.LimitOrderParams(args.price, size, side='sell')

print("Placing order: %s" % params)

order = auth.sell(params)

if(order.isError):
    print("... error placing order: %s" % order)
else:
    print("... order placed: %s" % order)

