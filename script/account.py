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


parser = argparse.ArgumentParser(description='Check acount balances.')

subparsers = parser.add_subparsers(title="Account Type", dest='acct_type', description="Available account types",
                                    help='These are the different currency accounts within the GDAX account')

eth_parser = subparsers.add_parser("eth", help="Ethereum account")
usd_parser = subparsers.add_parser("usd", help="US Dollar account")
btc_parser = subparsers.add_parser("btc", help="Bitcoin account")

parser.add_argument("-t", "--total", action='store_true',
                    help='Use this flag to indicate that the value of all accounts should be converted to the specified currency at current market rates. This can be used to estimate the total value of the GDAX profile.')

args = parser.parse_args()

auth = gcl.AuthClient()

accounts = auth.getAccounts()

if(args.acct_type == None):
    print("Acct\tBalance\t\tAvailable")
    print("USD\t$%.2f\t\t$%.2f" % (accounts["USD"].balance, accounts["USD"].available))
    print("ETH\t%.4f ETH\t%.4f ETH" % (accounts["ETH"].balance, accounts["ETH"].available))
    print("BTC\t%.4f BTC\t%.4f BTC" % (accounts["BTC"].balance, accounts["BTC"].available))
    sys.exit(0)

if(args.total):
    book = auth.getProductOrderBook(level=1)
    best_bid, best_ask = book.getBestPrices()

    if(args.acct_type == 'btc'):
        print("Sorry, this isn't supported for BTC at the moment.")
        sys.exit(-1)
    elif(args.acct_type == 'eth'):
        usd_as_eth = accounts["USD"].balance / best_ask
        total = usd_as_eth + accounts["ETH"].balance
        print("Total profile value: %.6f ETH" % total)
    elif(args.acct_type == 'usd'):
        eth_as_usd = accounts['ETH'].balance * best_bid
        total = eth_as_usd + accounts["USD"].balance
        print("Total profile value: $%.2f" % total)
    sys.exit(0)

acct = accounts[args.acct_type.upper()]
print("Currency: %s" % (acct.currency))
print("Account ID: %s" % (acct.id))
print("Profile ID: %s" % (acct.profile_id))
print("Balance: %f %s" % (acct.balance, acct.currency))
print("Available: %f %s" % (acct.available, acct.currency))
print("Held: %f %s" % (acct.hold, acct.currency))

