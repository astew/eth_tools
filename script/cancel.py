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


def IsBuyOrder(o):
    return o.side == 'buy'
def IsSellOrder(o):
    return o.side == 'sell'
def IsAnyOrder(o):
    return True

AllCondition = lambda o,p: True
AboveCondition = lambda o,p: o.price >= p
BelowCondition = lambda o,p: o.price <= p
EqualCondition = lambda o,p: o.price == p

parser = argparse.ArgumentParser(description='Cancel one or more active orders.')

group1 = parser.add_mutually_exclusive_group()

group1.add_argument("-x", "--all", action="store_const", dest="cancel_type", const=AllCondition,
       help="Use this flag to indicate all orders should be canceled.")
group1.add_argument("-n", "--above", action="store_const", dest="cancel_type", const=AboveCondition,
       help="Use this flag to indicate all orders at or above the specified price should be canceled.")
group1.add_argument("-u", "--below", action="store_const", dest="cancel_type", const=BelowCondition,
       help="Use this flag to indicate all orders at or below the specified price should be canceled.")
group1.add_argument("-e", "--exact", action="store_const", dest="cancel_type", const=EqualCondition, 
       help="Use this flag to indicate all orders with exactly the specified price should be canceled. (Default)")

group2 = parser.add_mutually_exclusive_group()
group2.add_argument("-b", "--buys", action="store_const", dest="order_type", const=IsBuyOrder,
        help="Use this flag to indicate only buy orders should be cancelled.")
group2.add_argument("-s", "--sells", action="store_const", dest="order_type", const=IsSellOrder,
        help="Use this flag to indicate only sell orders should be cancelled.")
group2.add_argument("-a", "--any", action="store_const", dest="order_type", const=IsAnyOrder,
        help="Use this flag to indicate any orders can be cancelled. (Default)")



parser.add_argument('price',type=float, help='The ask price', nargs='?', default=None)

parser.set_defaults(cancel_type=EqualCondition)
parser.set_defaults(order_type=IsAnyOrder)

args = parser.parse_args()

if(args.price == None and args.cancel_type != AllCondition):
    print("Unless the --all flag is used, a price must be specified.")
    sys.exit(-1)
elif(args.cancel_type == AllCondition and args.price != None):
    print("A price may not be specified if the --all flag is used.")
    sys.exit(-1)

price = args.price

auth = gcl.AuthClient()


print("Retrieving orders...")
orders = auth.getOrders()
count = 0
for order in orders:
    if(not args.order_type(order)):
        continue
    if(not args.cancel_type(order, args.price)):
        continue

    print("Canceling order: %s" % order)
    auth.cancelOrder(order.id)
    count += 1

print("Canceled %d orders" % count)


