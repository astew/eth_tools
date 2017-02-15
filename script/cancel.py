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


parser = argparse.ArgumentParser(description='Cancel one or more active orders.')

group1 = parser.add_mutually_exclusive_group()

group1.add_argument("-x", "--all", action="store_const", dest="cancel_type", const="all",
       help="Use this flag to indicate all orders should be canceled.")
group1.add_argument("-a", "--above", action="store_const", dest="cancel_type", const="above",
       help="Use this flag to indicate all orders at or above the specified price should be canceled.")
group1.add_argument("-b", "--below", action="store_const", dest="cancel_type", const="below",
       help="Use this flag to indicate all orders at or below the specified price should be canceled.")
group1.add_argument("-e", "--exact", action="store_const", dest="cancel_type", const="exact", 
       help="Use this flag to indicate all orders with exactly the specified price should be canceled. (Default)")

parser.add_argument('price',type=float, help='The ask price', nargs='?', default=None)

parser.set_defaults(cancel_type='exact')

args = parser.parse_args()

if(args.cancel_type == 'exact' and args.price == None):
    print("Unless the --all flag is used, a price must be specified.")
    sys.exit(-1)

price = args.price

auth = gcl.AuthClient()

if(args.cancel_type == 'all'):
    print("Canceling all orders.")
    auth.cancelOrder()
    sys.exit(0)

print("Retrieving orders...")
orders = auth.getOrders()

for order in orders:
    cn = False
    if(args.cancel_type == 'above' and order.price >= args.price):
        cn = True
    elif(args.cancel_type == 'below' and order.price <= args.price):
        cn = True
    elif(args.cancel_type == 'exact' and order.price == args.price):
        cn = True

    if(not cn):
        continue

    print("Canceling order: %s" % order)
    auth.cancelOrder(order.id)



