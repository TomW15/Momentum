# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 15:23:39 2020

@author: tomw1
"""

import numpy as np
import pandas as pd
import pandas_datareader.data as web
import pickle
import re


def get_details(cur1="GBP", cur2="USD", folder="ETF_Analysis"):
    
    def get_list(my_list, pattern = "'(.*?)'"):
        return re.findall(pattern, my_list)
    
    with open('universe_tickers.pickle', 'rb') as f:
        tickers = pickle.load(f)
        
    dfList = pd.read_csv(folder+'/WML_Old.csv')
    
    dfP = pd.read_csv(folder+'/All_data.csv')
    dfP = dfP.set_index('Date')
    dfP = pd.DataFrame.fillna(dfP, 0)
    
    forex = pd.read_csv(folder+'/forex_{}_{}.csv'.format(cur1, cur2))
    forex = forex.set_index('Date')
    
    dfRet = pd.read_csv(folder+'/log_returns.csv')
    dfRet = pd.DataFrame.fillna(dfRet, 0)
    dfRet = dfRet.set_index('Date')

    winners = []
    losers = []

    for i in range(dfList.shape[0]):
        winners.append(get_list(dfList['Winners'][i]))
        losers.append(get_list(dfList['Losers'][i]))

    startF = dfList['StartF']
    endF = dfList['EndF']
    startH = dfList['StartH']
    endH = dfList['EndH']
    startS = dfList['StartS']
    endS = dfList['EndS']
    
    return tickers, dfP, dfRet, winners, losers, startF, endF, startH, endH, startS, endS, forex

tickers, dfP, dfRet, winners, losers, startF, endF, startH, endH, startS, endS, forex = get_details()

holding_period = 0
returns = []
for date in dfRet.index:
    try:
        winList, losList = winners[holding_period], losers[holding_period]
        
        day_return = 0
        
        for i, j in zip(winList, losList):
            day_return += dfRet[i][date]-dfRet[j][date]
        
        day_return /= 4
        
        returns.append(day_return)
            
        if date==endH[holding_period]:
            holding_period += 1
    except IndexError as _:
        pass

days = len(returns)

mkt_data = web.DataReader('^GSPC', 'yahoo', dfRet.index[0], dfRet.index[days])['Adj Close']
mkt_data = np.log(mkt_data/mkt_data.shift(1))
mkt_data = mkt_data.fillna(0)
  
SPY = dfRet['SPY'][dfRet.index[:days]].values
VTV = dfRet['VTV'][dfRet.index[:days]].values
MKT = mkt_data[:len(returns)].values

num = [i for i in range(days)]+[i for i in range(days)]+[i for i in range(days)]+[i for i in range(days)]

identity = ['Mom' for i in range(days)]+['Mkt' for i in range(days)]+['VTV' for i in range(days)]+['SPY' for i in range(days)]

returns=np.concatenate((returns, SPY, VTV, MKT))

daily = pd.DataFrame({'Date': dfRet.index[:days], 'Momentum': returns, 'SPY': SPY, 'VTV': VTV, 'MKT':MKT})
daily.to_csv("ETF_Analysis/MOM_SPY_VTV_MKT_returns.csv")

daily_ret = pd.DataFrame({'Number': num, 'Investment':identity, 'Returns': returns})
daily_ret.to_csv("ETF_Analysis/beta_checker.csv")




















