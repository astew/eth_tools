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


parser = argparse.ArgumentParser(description='Check current market status.')

subparsers = parser.add_subparsers(title="Actions", dest='command',
                                description="Available actions",
                                help = "These are the sub-actions available to the market command")
subparsers.required = True

watch_parser = subparsers.add_parser("watch", help="Monitor the market order book.")
watch_parser.add_argument("-i", "--interval", type=float, default=5.0,
                                    help="The time (in seconds) to wait between requests to the GDAX server. Default 5.0 seconds.")
#watch_parser.add_argument("-a", "--alert", action='store_true',
#                                    help="Use this flag to indicate a big banner should be printed if and when the order finishes executing.")

alert_parser = subparsers.add_parser("alert", help="Monitor the market order book and alert when the best bid/ask prices exceed certain values.")
alert_parser.add_argument("-i", "--interval", type=float, default=5.0,
                                            help="The time (in seconds) to wait between requests to the GDAX server. Default 5.0 seconds.")
alert_parser.add_argument("-H", "--high", type=float, default=10000.0,
                        help="Alert if the best bid price becomes equal to or greater than this price.")
alert_parser.add_argument("-L", "--low", type=float, default=0.0,
                                help="Alert if the best ask price becomes equal to or below this price.")


args = parser.parse_args()

auth = gcl.AuthClient()


def WatchCommand():
    prev_bid = None
    prev_ask = None
    while(True):
        try:
            book = auth.getProductOrderBook(level=1)

            best_bid, best_ask = book.getBestPrices()

            if(prev_bid != best_bid or prev_ask != best_ask):
                print("Best BID/ASK:\t$%.2f / $%.2f\tSpread: $%.2f" % (best_bid, best_ask, best_ask-best_bid))

            prev_bid = best_bid
            prev_ask = best_ask
        
        except:
            continue
        time.sleep(args.interval)

alert_str = """
=========================================
=========================================
=========================================
=============== ALERT ===================
=========================================
=========================================
=========================================
"""

def AlertCommand():
        while(True):
            try:
                book = auth.getProductOrderBook(level=1)
                best_bid, best_ask = book.getBestPrices()
                
                if(best_bid >= args.high):
                    print(alert_str)
                    print("Best bid: $%.2f" % best_bid)
                    break
                elif(best_ask <= args.low):
                    print(alert_str)
                    print("Best ask: $%.2f" % best_ask)
                    break

            except Exception as ex:
                print(ex)
                continue
            
            time.sleep(args.interval)


commands = {
        "watch": WatchCommand,
        "alert": AlertCommand,
        }

commands[args.command]()
