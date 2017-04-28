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

watch_parser = subparsers.add_parser("watch", help="Watches the specified order, reporting updated until it's cancelled or filled.")
watch_parser.add_argument("order_ids", type=str, nargs='*',
                            help="The IDs of the orders to watch. This may be a prefix as well. If no order IDs are specified, all orders will be watched.")
watch_parser.add_argument("-i", "--interval", type=float, default=5.0,
                            help="The time (in seconds) to wait between requests to the GDAX server. Default 5.0 seconds.")
watch_parser.add_argument("-a", "--alert", action='store_true',
                            help="Use this flag to indicate a big banner should be printed if and when the order finishes executing.")



args = parser.parse_args()

if(args.command == None):
    parser.print_help()
    sys.exit(-1)


auth = gcl.AuthClient()

def printOrderDetails(order):
     print("Order ID: %s" % order.id)
     print("Side: %s\tType: %s" % (order.side, order.type))
     print("Size: %.6f ETH" % (order.size))
     print("Filled: %.6f ETH (%.2f%%)" % (order.filled_size, (order.filled_size/order.size) * 100))
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


alert_str = """
==================================================
==================================================
==================================================
=================== DONE =========================
==================================================
==================================================
==================================================\a
"""

def WatchCommand():
    order_ids = args.order_ids
    orders_last = auth.getOrders()

    if(order_ids == []):
        print("Watching all orders.")
    else:
        print("Watching orders with IDs starting with: %s" % ", ".join(order_ids))

    orders_last = {order.id: order for order in orders_last}

    if(order_ids == []):
        order_ids = [""]

    while(True):
        try:
            orders = auth.getOrders()

            orders = [o for o in orders if any([o.id.startswith(prefix) for prefix in order_ids])]
            orders = {o.id: o for o in orders}
            
            new_oids = [k for k in orders.keys() if not (k in orders_last)]
            old_oids = [k for k in orders_last.keys() if not (k in orders)]
            abc_oids = [k for k in orders.keys() if (k in orders_last)]

            #handle these sets one by one

            for oid in new_oids:
                oo = orders[oid]
                print("New\t | %s: %.4f ETH @ $%.2f\t\t(%s)" % (oo.side, oo.size, oo.price, oid))

            for oid in abc_oids:
                #check if any has been filled
                ff = orders[oid].filled_size > orders_last[oid].filled_size
                if(ff):
                    oo = orders[oid]
                    print("Update\t | %s: %.4f / %.4f ETH (%.2f%%)\t@ $%.2f\t(%s)" % (oo.side, oo.filled_size, oo.size, (oo.filled_size/oo.size) * 100, oo.price, oid))

            for oid in old_oids:
                oo = orders_last[oid]
                print("Complete | %s: %.4f ETH @ $%.2f\t\t(%s)" % (oo.side, oo.size, oo.price, oid))
                if(args.alert):
                    print(alert_str)

            orders_last = orders
        except Exception as ex:
            print("")
            print("Exception occurred:")
            print(ex)
            print("")
        
        time.sleep(args.interval)
    

commands = {
        "list": ListCommand,
        "show": ShowCommand,
        "watch": WatchCommand,
        }


commands[args.command]()


