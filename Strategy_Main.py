# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 16:42:27 2020

@author: tomw1
"""
# Import packages from Python
import datetime as dt
import sys

# Import modules from files
import data_collection
import load_forex
import winners_minus_losers
import implement_strategy
import forward_looking

#import perform_strategy
#import find_betas

# Set Price Data Dates
start = dt.datetime(2010, 1, 1)
end = dt.datetime.now()

# Set Cluster Dates
#startC = start
#endC = end
startC = dt.datetime(2010, 1, 1)
endC = dt.datetime(2014, 12, 31)

recluster = True
cluster_on = 1.00 # i.e. don't cluster
winners_losers = 4 # Number of Winners and Losers strategy invests in
investment_in = 1 # Months time so 0 is current month

print("In data_collection.py...")
tickers, data, clr = data_collection.get_data_from_yahoo(start, end, recluster, cluster_on, startC, endC)
print("In winners_minus_losers.py...")
winners_minus_losers.WinnersMinusLosers(tickers, data, clr, winners_losers)
print("In forex.py...")
load_forex.get_forex()

#print("In perform_strategy.py...") 
#monthlyReturns = perform_strategy.momentum_strategy(winners_losers)

print("In implement_strategy.py...")
implement_strategy.strategy()
print("In forward_looking.py (current investment)...")
forward_looking.current_investment(data, tickers, clr, winners_losers)
print("In prediction.py (predict {} investment)...".format(investment_in))
forward_looking.predict_investment(data, tickers, clr, winners_losers, investment_in)

#print("In find_betas.py")
#find_betas.prepare_for_R(start, end, monthlyReturns)

print("Finished!")

"""
    Files in ETF_Data: 44 (All ETF Data)
    Files in ETF_Analysis: 5 (Data for Momentum Implementation)
    Files in Main: 1 (Forex Data)

To Do List:
XXX    - Shortest Path Algo (ETF Selection) <- Implement
XXX    - Figure out way to delete files if doing a complete recluster (WML may be different)
XXX    - Get next month's winners and losers (data is there...)
    - Investment Doesn't Change, so no compounding...
XXX    - Be Able To Change Number of Investments from Home
    - Upload to either Github or Atom - with added comments
XXX    - Fix Plots in perform_strategy_simplify (Almost done - need to fix one for cumulative return)
XXX    - Simplify perform_strategy_simplify
    - Sharpe Ratio
"""

###############################################################################











        
        





