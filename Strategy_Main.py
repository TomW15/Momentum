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

hedge = ["VTV", "SPY"]

# Set Price Data Dates - Sets the start and end dates you want to perform strategy
start = dt.datetime(2010, 1, 1)
end = dt.datetime.now()

# Set Cluster Dates - Allows you to customize the period of returns you want to cluster on
startC = start
endC = end
#startC = dt.datetime(2010, 1, 1)
#endC = dt.datetime(2014, 12, 31)

# Set custom settings
recluster = True # Checks if you want to recluster or use last cluster
cluster_on = 1.00 # The value of correlation you want to cluster up to
winners_losers = 4 # Number of Winners and Losers strategy invests in
investment_in = 1 # Allows you to see the current winners and losers in this "investment_in" months time so 0 is current month

print("In data_collection.py...")
tickers, data, clr = data_collection.get_data_from_yahoo(start, end, recluster, cluster_on, startC, endC, hedge)
print("In winners_minus_losers.py...")
winners_minus_losers.WinnersMinusLosers(tickers, data, clr, winners_losers)
print("In forex.py...")
load_forex.get_forex()
print("In implement_strategy.py...")
implement_strategy.strategy()
print("In forward_looking.py (current investment)...")
forward_looking.current_investment(data, tickers, clr, winners_losers)
print("In prediction.py (predict {} month investment)...".format(investment_in))
forward_looking.predict_investment(data, tickers, clr, winners_losers, investment_in)
print("Finished!")

###############################################################################







#    wMo = 1
#    
#    wMo each 1/2/4 = 1/8        1/2
#    wMo each -1/2/4 = -1/8      -1/2
#    wHedge each 1/2/1 = 1/2     1/2
#    wHedge each -1/2/1 = -1/2   -1/2

#    wMo each 1/2/8 = 1/16        1/4
#    wMo each -1/2/8 = -1/16      -1/4
#    wHedge each 1/2/2 = 1/4     1/4
#    wHedge each -1/2/2 = -1/4   -1/4

        
        





