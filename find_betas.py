# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 20:33:49 2020

@author: tomw1
"""

import pandas_datareader.data as web
import pandas as pd
import numpy as np


def prepare_for_R(start, end, monthlyReturns):
    folder1="ETF_Data"
    folder2="ETF_Analysis"
    
    def read_data(ticker):
        df = pd.read_csv(folder1+'/{}.csv'.format(ticker))
        df.set_index('Date', inplace=True)
        df = df[[ticker]]
        return df
    
    def save_data(ticker, start, end, yh='yahoo'):
        df = web.DataReader(ticker, yh, start, end)
        print('Getting {}'.format(ticker))
        df.rename(columns = {'Adj Close': ticker}, inplace=True)
        df = df[[ticker]]
        df.to_csv(folder1+'/{}.csv'.format(ticker)) 
        return read_data(ticker)
        
    wml = pd.read_csv(folder2+"/WML_Old.csv")
    startH, endH = wml["StartH"], wml["EndH"]
        
    ticker = "^GSPC"  
    mkt_data = web.DataReader(ticker, 'yahoo', start, end)
    mkt_data.rename(columns = {'Adj Close': ticker}, inplace=True)
    mkt_data = mkt_data[[ticker]]
    mkt_data.to_csv(folder2+"/mkt_data.csv")
    
    SPY = pd.read_csv(folder1+"/SPY.csv")
    VTV = pd.read_csv(folder1+"/VTV.csv")
    SPY = SPY.set_index("Date")
    VTV = VTV.set_index("Date")
    mkt_return, mom_return, vtv_return, spy_return = [], [], [], []
    
    
    for i in range(len(startH)):
        mom_return.append(np.sum(monthlyReturns[i]))
        mkt_return.append(mkt_data["^GSPC"][endH[i]]/mkt_data["^GSPC"][startH[i]]-1)
        vtv_return.append(VTV["VTV"][endH[i]]/VTV["VTV"][startH[i]]-1)
        spy_return.append(SPY["SPY"][endH[i]]/SPY["SPY"][startH[i]]-1)
        
    mkt_return = np.array(mkt_return)
    mom_return = np.array(np.exp(mom_return)-1)
    
    num = [i for i in range(108)]+[i for i in range(108)]+[i for i in range(108)]+[i for i in range(108)]
    
    li = ['Mom' for i in range(108)]+['Mkt' for i in range(108)]+['VTV' for i in range(108)]+['SPY' for i in range(108)]
    
    returns = pd.DataFrame({'Momentum': mom_return, 'Market': mkt_return, 'VTV': vtv_return, 'SPY':spy_return})
    returns.to_csv("returns_for_analysis.csv")
    
    returns=np.concatenate((mom_return, mkt_return, vtv_return, spy_return))
    
    retDf = pd.DataFrame({'Number': num, 'Investment':li, 'Return': returns})
    retDf.to_csv(folder2+"/all_returns_for_analysis.csv")


    
    