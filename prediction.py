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

import strategy_implementation_functions
import plot_data

def get_cum_returns(universe, cum_log_ret_universe, start, end):
    cumulative = dict()
    for u in universe:
        cumulative[u] = cum_log_ret_universe.loc[end, u]-cum_log_ret_universe.loc[start, u]
        if np.isnan(cumulative[u]):
            del cumulative[u]    
    return cumulative

def predict_investment(data, tickers, clr, win_los, future_month, folder="ETF_Analysis"):
    
#    def get_cum_returns(universe, cum_log_ret_universe, start, end):
#        cumulative = dict()
#        for u in universe:
#            cumulative[u] = cum_log_ret_universe.loc[end, u]-cum_log_ret_universe.loc[start, u]
#            if np.isnan(cumulative[u]):
#                del cumulative[u]    
#        return cumulative
    
    def get_future(d, future_month):
        month = int(d[5:7])+future_month
        if month > 12:
            year = str(int(d[:4]) + 1)
            month = "%02d"%(month%12)
        else:
            year = d[:4]
            month = "%02d"%month
        return year+"-"+month+"-01"

    # Find Holding Period
    dates=list(data.index.values)[-31:] + [dt.datetime.now().strftime("%Y-%m-%d")]
    
    start_pred_hold = get_future(dates[-1],future_month)
    
    # Find Formation Period
    months = pd.read_csv("ETF_Analysis/months.csv",usecols=['StartH', 'EndH'])
    start_pred_form = months['StartH'].iloc[-13+future_month] # Get Next Formation Start Date
    if (-2+future_month) < 0:
        end_pred_form = months['EndH'].iloc[-2+future_month] # Get Next Formation End Date
    else:
        end_pred_form = dates[-2]
    
    cum_pred = get_cum_returns(tickers[:-2], clr, start_pred_form, end_pred_form) 
    cums_pred=OrderedDict(sorted(cum_pred.items(), key = itemgetter(1), reverse = True))
    order_pred = list(cums_pred.keys())
    pred_winners, pred_losers = order_pred[:win_los], order_pred[-win_los:]    
    
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
    
def current_investment(data, tickers, clr, win_los, future_month, cur1="GBP", cur2="USD", folder="ETF_Analysis"):
    
    dates=list(data.index.values)[-31:] + [dt.datetime.now().strftime("%Y-%m-%d")]
    months = pd.read_csv("ETF_Analysis/months.csv",usecols=['StartH', 'EndH'])

    current_month = int(dates[-1][5:7])
    # Get current month start and end
    for d in range(len(dates)):
        if int(dates[d][5:7]) == current_month:
            start_current_hold = dates[d] # Get Next Holding Start Date
            break
#    end_current_hold = dates[-1]
    start_current_form = months['StartH'].iloc[-13]
    end_current_form = months['EndH'].iloc[-2]
    start_current_scale = months['StartH'].iloc[-6]
    end_current_scale = months['EndH'].iloc[-1]
    
    cum_current = get_cum_returns(tickers[:-2], clr, start_current_form, end_current_form) 
    cums_current=OrderedDict(sorted(cum_current.items(), key = itemgetter(1), reverse = True))
    order_current = list(cums_current.keys())
    curr_winners, curr_losers = order_current[:win_los], order_current[-win_los:]    

    prices = pd.read_csv(folder+'/All_data.csv').set_index('Date')[start_current_hold:]
    returns = pd.read_csv(folder+'/log_returns.csv')
    returns = pd.DataFrame.fillna(returns, 0).set_index('Date')
    forex = pd.read_csv('forex_{}_{}.csv'.format(cur1, cur2)).set_index('Date')[start_current_hold:]
    
    portfolio_value = pd.DataFrame([("Initial Investment", 10000, 10000/forex['FX'][start_current_hold])], columns = ["Date", "Port. Value (USD)", "Port. Value (GBP)"]).set_index("Date")

    weight, scalingSD = strategy_implementation_functions.scaling_variance(returns, curr_winners, curr_losers, start_current_scale, end_current_scale)
    shares = strategy_implementation_functions.invest(prices, tickers[:-2], tickers[-2:], curr_winners, curr_losers, 10000, weight, start_current_hold)   
    portfolio_value, monthReturn, momReturn, hedgeReturn = strategy_implementation_functions.get_value(prices, shares, curr_winners, curr_losers, tickers[-2:], portfolio_value, forex, 10000)
    
    USD_value = (portfolio_value['Port. Value (USD)']/portfolio_value['Port. Value (USD)'][start_current_hold]-1)[start_current_hold:]
    GBP_value = (portfolio_value['Port. Value (GBP)']/portfolio_value['Port. Value (GBP)'][start_current_hold]-1)[start_current_hold:]
    benchmark_value = prices['SPY']/prices['SPY'][start_current_hold]-1
    
    monthReturn = pd.concat([USD_value, GBP_value, benchmark_value], axis=1, join='inner')
    
    plot_data.plot_same_axis(monthReturn)
    


    
    
    
    
    
    
    