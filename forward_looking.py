# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 17:19:50 2020

@author: tomw1
"""

import datetime as dt
import numpy as np
import pandas as pd
from collections import OrderedDict
from operator import itemgetter

import strategy_implementation_functions as sif
import plot_data

def get_cum_returns(universe, cum_log_ret_universe, start, end):
    """
        Gets cumulative returns between start and end dates using a list of tickers (universe)
        and already created cumulative log returns for universe
    """
    # Initializes a dictionary of the cumulative returns
    cumulative = dict()
    # Loops through universe calculating cumulative log return between dates
    for u in universe:
        # Adds value to dictionary
        cumulative[u] = cum_log_ret_universe.loc[end, u]-cum_log_ret_universe.loc[start, u]
        # If value is nan, meaning data isn't available for entire period start-end then deletes entry in dictionary
        if np.isnan(cumulative[u]):
            del cumulative[u]    
    return cumulative

def predict_investment(data, tickers, clr, win_los, future_month, folder="ETF_Analysis"):
    
    def get_future(d, future_month):
        """
            Inputs: d is a date, in this case will be today's date
                    future_month is the number of months you want to go into the future
                    
            Gets the first day (not necessarily trading day) in future_month's time
        """
        
        # Adds future_month to current month
        month = int(d[5:7])+future_month
        # If month is greater than 12, this means we have entered a new year
        if month > 12:
            # Enter new year and take mod12 of month calculated above
            # Both are converted to string
            year = str(int(d[:4]) + 1)
            month = "%02d"%(month%12)
        else:
            # Get current year and convert month into a string version (double digit)
            year = d[:4]
            month = "%02d"%month
        return year+"-"+month+"-01"

    # Get a list of all possible investment initializations from the data we have collected 
    dates=list(data.index.values)[-31:] + [dt.datetime.now().strftime("%Y-%m-%d")]
    # Get list of start and end holding dates to find future formation periods
    months = pd.read_csv(folder+"/months.csv",usecols=['StartH', 'EndH'])
    
    # Gets the future holding start date using today and user inputted future_month in Strategy_Main.py
    start_pred_hold = get_future(dates[-1],future_month)
    
    # Find Formation Period
    start_pred_form = months['StartH'].iloc[-13+future_month] # Get Formation Start Date for holding period identified above
    # Checks if we have data up to formation end, if yes then set this as the formation end, otherwise set to last data collection date
    if (-2+future_month) < 0:
        end_pred_form = months['EndH'].iloc[-2+future_month]
    else:
        # This is -2 because dates includes today's date which may be a non-trading date
        end_pred_form = dates[-2]
    
    # Get the cumulative returns for each possible investment over the formation period and order to get list of winners and losers
    cum_pred = get_cum_returns(tickers[:-2], clr, start_pred_form, end_pred_form) 
    cums_pred=OrderedDict(sorted(cum_pred.items(), key = itemgetter(1), reverse = True))
    order_pred = list(cums_pred.keys())
    pred_winners, pred_losers = order_pred[:win_los], order_pred[-win_los:]    
    
    # Form text to be printed showing the current winners and losers for the holding date specified
    a = "Predicted Investments for holding period starting " + start_pred_hold + ": "
    b=""
    c=""
    
    for i in range(2*win_los):
        if i == 0:
            b += pred_winners[i]
        elif i == (win_los-1):
            b += " and " + pred_winners[i]
        elif i < win_los:
            b += ", " + pred_winners[i]
        elif i == win_los:
            c += pred_losers[i-win_los]
        elif i == (win_los*2-1):
            c += " and " + pred_losers[i-win_los]
        else:
            c += ", " + pred_losers[i-win_los]
    
    print(a)
    print("Long: " + b)
    print("Short: " + c)    
    
def current_investment(data, tickers, clr, win_los, cur1="GBP", cur2="USD", folder="ETF_Analysis", start_value=10000):
    
    # Get a list of all possible investment initializations from the data we have collected 
    dates=list(data.index.values)[-31:] + [dt.datetime.now().strftime("%Y-%m-%d")]
    # Get list of start and end holding dates to find future formation periods
    months = pd.read_csv("ETF_Analysis/months.csv",usecols=['StartH', 'EndH'])

    # Find the current month
    current_month = int(dates[-1][5:7])
    # Get current month start trading period to run investment from then to data we have remaining
    for d in range(len(dates)):
        if int(dates[d][5:7]) == current_month:
            start_current_hold = dates[d]
            break

    # Get the formation and scaling periods for current month, in order to find list of winners and losers as well as momentum weight
    start_current_form = months['StartH'].iloc[-13]
    end_current_form = months['EndH'].iloc[-2]
    start_current_scale = months['StartH'].iloc[-6]
    end_current_scale = months['EndH'].iloc[-1]
    
    # Get the cumulative returns for each possible investment over the formation period and order to get list of winners and losers
    cum_current = get_cum_returns(tickers[:-2], clr, start_current_form, end_current_form) 
    cums_current=OrderedDict(sorted(cum_current.items(), key = itemgetter(1), reverse = True))
    order_current = list(cums_current.keys())
    curr_winners, curr_losers = order_current[:win_los], order_current[-win_los:]    

    # Get prices from current month's holding period as well as returns and exchange rate over same period
    prices = pd.read_csv(folder+'/All_data.csv').drop_duplicates(subset='Date').set_index('Date')[start_current_hold:].dropna()
    returns = pd.read_csv(folder+'/log_returns.csv').drop_duplicates(subset='Date')
    returns = pd.DataFrame.fillna(returns, 0).set_index('Date')
    forex = pd.read_csv('forex_{}_{}.csv'.format(cur1, cur2)).set_index('Date')[start_current_hold:]
    
    try:
        # Initialize portfolio_value with standard amount start_value set as default to 1
        portfolio_value = pd.DataFrame([("Initial Investment", start_value, start_value/forex['FX'][start_current_hold])], columns = ["Date", "Port. Value (USD)", "Port. Value (GBP)"]).set_index("Date")
    
        # Use scaling_variance function in strategy_implementation_functions.py to get momentum weight and scaling standard deviation
        weight, scalingSD = sif.scaling_variance(returns, curr_winners, curr_losers, start_current_scale, end_current_scale)
        # Use invest function in strategy_implementation_functions.py to get number of shares of each winner, loser and hedge given weight invested in momentum
        shares = sif.invest(prices, tickers[:-2], tickers[-2:], curr_winners, curr_losers, start_value, weight, start_current_hold)   
        # # Use get_value function in strategy_implementation_functions.py to get the portfolio value from current month's investment
        portfolio_value, monthReturn, momReturn, hedgeReturn = sif.get_value(prices, shares, curr_winners, curr_losers, tickers[-2:], portfolio_value, forex, start_value)
        
        # Calculate return of strategy in USD and GBP as well as the benchmark (SPY)
        USD_value = (portfolio_value['Port. Value (USD)']/portfolio_value['Port. Value (USD)'][start_current_hold]-1)[start_current_hold:]
        GBP_value = (portfolio_value['Port. Value (GBP)']/portfolio_value['Port. Value (GBP)'][start_current_hold]-1)[start_current_hold:]
        SPY_value = prices['SPY']/prices['SPY'][start_current_hold]-1
        VTV_value = prices['VTV']/prices['VTV'][start_current_hold]-1
        
        monthReturn = pd.concat([USD_value, GBP_value, SPY_value, VTV_value], axis=1, join='inner').reset_index()
        
        # Use plot_diff_axis function in plot_data.py to plot USD_value, GBP_value and benchmark on left y-axis and exchange rate over period on right y-axis
        plot_data.plot_diff_axis(monthReturn, forex.reset_index())
        print(curr_winners, weight)
    except KeyError:
        # Means a new month has started but data isn't available yet for that month
        pass
    
    
    
    
    
    