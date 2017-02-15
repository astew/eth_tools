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

args = parser.parse_args()

auth = gcl.AuthClient()


book = auth.getProductOrderBook(level=1)

best_bid, best_ask = book.getBestPrices()

print("Best bid: $%.2f" % best_bid)
print("Best ask: $%.2f" % best_ask)

