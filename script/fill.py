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


parser = argparse.ArgumentParser(description='Get information on order fills')

subparsers = parser.add_subparsers(title='Actions', dest='command', 
                                    description='Available Actions', 
                                    help='These are the sub-actions available to the order command.')
#subparsers.required = True

list_parser = subparsers.add_parser("list",   
                                    help='Get a list of order fills')
list_group = list_parser.add_mutually_exclusive_group()
list_group.add_argument("-d","--details", action='store_const', dest='list_type', const='details',
                            help='Use this flag to show detailed information on each fill.')
list_group.add_argument("-b", "--brief", action='store_const', dest='list_type', const='brief',
                            help='Use this flag to show a brief summary of each fill. (Default)')
list_parser.set_defaults(list_type='brief')

list_parser.add_argument("-n", "--limit", type=int, nargs=1,default=[100],
                            help="The maximum number of entries to show")
list_parser.add_argument("-v", "--descending", action='store_true',
                            help='Use this flag to indicate results should be printed oldest first.')

show_parser = subparsers.add_parser("show", help='Show details above a specific order fill')
show_group = show_parser.add_mutually_exclusive_group()
show_group.required = True
show_group.add_argument("-o", "--order_id", type=str, help='The order ID associated with the fill')
show_group.add_argument("-t", "--trade_id", type=str, help='The trade ID associated with the fill')


#parser.add_argument('n_orders',type=int, help='Number of orders to create',nargs='?', default=None)


args = parser.parse_args()

if(args.command == None):
    parser.print_help()
    sys.exit(-1)


auth = gcl.AuthClient()

def printFillDetails(fill):
     print("Side: %s" % fill.side)
     print("Price: $%.2f" % fill.price)
     print("Size: %f ETH" % fill.size)
     print("Fee: $%.2f" % (fill.fee))
     print("Executed value: $%.2f" % (fill.price*fill.size + fill.fee))
     print("Product: %s" % fill.product_id)
     print("Created at: %s" % fill.created_at)
     print("Liquidity: %s" % fill.liquidity)
     print("Order ID: %s" % fill.order_id)
     print("Trade ID: %s" % fill.trade_id)
     print("Settled: %s" % fill.settled)




def ListCommand():
    fills = auth.getFills()
    if(args.descending):
        fills.reverse()

    if(args.limit != None):
        limit = args.limit[0]
        fills = fills[:limit]

    for fill in fills:
        if(args.list_type == 'brief'):
            print(fill)
        elif(args.list_type == 'details'):
            print("===================================")
            printFillDetails(fill)
        else:
            print("Error.. unknown list type.")
            sys.exit(-1)



def ShowCommand():
    order_id = args.order_id
    trade_id = args.trade_id

    fills = auth.getFills()
   
    fills = [f for f in fills if ((order_id != None 
                                      and f.order_id.startswith(order_id))
                               or (trade_id != None 
                                      and (str(f.trade_id)).startswith(trade_id)))]
    if(len(fills) == 0):
        print("Could not find any order matching the specified ID.")
        sys.exit(-1)
    elif(trade_id != None and len(fills) > 1):
        print("Found more than one fill with ID matching specified trade ID. You may need to provide more characters of the ID.")
        for f in fills:
            print(f.trade_id)
        sys.exit(-1)

    for f in fills:
        printFillDetails(f)


    return


commands = {
        "list": ListCommand,
        "show": ShowCommand,
        }


commands[args.command]()


