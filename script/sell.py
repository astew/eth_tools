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


parser.add_argument('volume', type=str, help='The amount of ETH to sell or USD to recover. Use "all" to specify that all of the given currency should be used. If a percentage is specified, then that percentage of available ETH will be used.')
parser.add_argument('price',type=float, help='The ask price')


args = parser.parse_args()

#let's check that we have enough ETH to place this order
auth = gcl.AuthClient()
eth_acct = auth.getAccounts()['ETH']

eth_cost = nu.interp_float_str(args.volume, eth_acct.available)

if(eth_acct.available < eth_cost):
    print("Insufficient ETH in account.")
    print("Balance: $%.2f" % eth_acct.balance)
    print("Available: $%.2f" % eth_acct.available)
    sys.exit(1)

size = eth_cost

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
    print("Order ID: %s" % order.id)

