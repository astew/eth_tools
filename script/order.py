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


parser = argparse.ArgumentParser(description='Get information on open buy or sell orders.')

subparsers = parser.add_subparsers(title='Actions', dest='command', 
                                    description='Available Actions', 
                                    help='These are the sub-actions available to the order command.')
#subparsers.required = True

list_parser = subparsers.add_parser("list",   
                                    help='Get a list of open orders')
list_group = list_parser.add_mutually_exclusive_group()
list_group.add_argument("-d", "--details", action='store_const', dest='list_type', const='details',
                            help='Use this flag to show detailed information on each open order.')
list_group.add_argument("-b", "--brief", action='store_const', dest='list_type', const='brief',
                            help='Use this flag to show a brief summary of each open order. (Default)')
list_parser.set_defaults(list_type='brief')

show_parser = subparsers.add_parser("show", help='Show details above a specific order')
show_parser.add_argument("order_id", type=str,
                            help='The ID of the order to show. This may be a prefix so long as it is unambiguous among open orders.')

#parser.add_argument('n_orders',type=int, help='Number of orders to create',nargs='?', default=None)


args = parser.parse_args()

if(args.command == None):
    parser.print_help()
    sys.exit(-1)


auth = gcl.AuthClient()

def printOrderDetails(order):
     print("Order ID: %s" % order.id)
     print("Side: %s\tType: %s" % (order.side, order.type))
     print("Size (Filled): %.6f ETH (%.2f%%)" % (order.size, (order.filled_size/order.size) * 100))
     print("Price: $%.2f\t\tFill Fees: $%.2f" % (order.price, order.fill_fees))
     print("Product: %s" % order.product_id)
     print("Post Only: %s" % order.post_only)
     print("Created at: %s" % order.created_at)
     print("Status: %s" % order.status)



def ListCommand():
    orders = auth.getOrders()
    for order in orders:
        if(args.list_type == 'brief'):
            print(order)
        elif(args.list_type == 'details'):
            print("===================================")
            printOrderDetails(order)
        else:
            print("Error.. unknown list type.")
            sys.exit(-1)



def ShowCommand():
    order_id = args.order_id
    
    orders = auth.getOrders()
    #find orders that start with order_id
    orders = [o for o in orders if o.id.startswith(order_id)]
    if(len(orders) == 0):
        print("Could not find an order matching the specified order ID.")
        sys.exit(-1)
    elif(len(orders) > 1):
        print("Found more than one order with ID matching specified order ID. You may need to provide more of the ID.")
        sys.exit(-1)

    order = orders[0]
    
    printOrderDetails(order)


    return


commands = {
        "list": ListCommand,
        "show": ShowCommand,
        }


commands[args.command]()


