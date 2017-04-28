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


parser.add_argument('volume', type=str, help='The amount of USD to spend or ETH to buy. If "all" is specified, all available USD will be used. If a percentage is specified, that percentage of available funds will be used.')
parser.add_argument('price',type=float, help='The bid price')


args = parser.parse_args()


#let's check that we have enough USD to place this order
auth = gcl.AuthClient()
usd_acct = auth.getAccounts()['USD']

usd_cost = nu.interp_float_str(args.volume, usd_acct.available)

if(usd_acct.available < usd_cost):
    print("Insufficient USD in account.")
    print("Balance: $%.2f" % usd_acct.balance)
    print("Available: $%.2f" % usd_acct.available)
    sys.exit(1)

size = usd_cost / args.price

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
    print("Order ID: %s" % order.id)

