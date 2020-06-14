# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 16:06:56 2020

@author: tomw1
"""

# Import From Python:
import datetime as dt
from datetime import timedelta
import numpy as np
import os
import pandas as pd
import pandas_datareader.data as web
import pandas_market_calendars as mcal
import pickle

import sys

def get_data_from_yahoo(start, end, recluster, cluster_on, startC, endC, hedge):          

    # Get current date and time to update prices
    now=dt.datetime.now()
    # Set where data is to be stored
    folder1 = 'ETF_Data'
    folder2 = 'ETF_Analysis'
    # Initialize an empty pandas dataframe
    main_df = pd.DataFrame()
    
    # Create a folder in source folder called "ETF_Analysis"
    if not os.path.exists(folder2):
        os.makedirs(folder2)  
    
    # Import From Files:
    import clustering_algo
    
################################################################################
################################################################################    

    def save_tickers():
        
        # Retrieve tickers to be invested in
        sym_AltEn=["NLR","FAN","PBD","TAN"]
        sym_Cons=["PBS","PBJ","PEJ","PMR","BJK","XHB","CARZ"]
        sym_Ener=["PXE","FRAK","PXJ"]
        sym_Fina=["KBWP","IAI","PSP","KBWR","KBWB"]
        sym_Heal=["IHI","IHF","PBE","PJP"]
        sym_Indu=["GII","PIO","PPA","IYT","SEA"]
        sym_Mate=["HAP","GDX","GDXJ","KOL","SLX","XME"]
        sym_Tech=["PSJ","SKYY","PXQ","PNQI","PSI","SOCL","ROBO"]#"FONE",
        sym_Util= ["GRID"]
    
        tickers = sym_AltEn+sym_Cons+sym_Ener+sym_Fina+sym_Heal+sym_Indu+sym_Mate+sym_Tech+sym_Util
        tickers = sorted(tickers)
        
#        data = pd.read_csv('ETF_details.csv', usecols=['Ticker'])
#        tickers = sorted(data['Ticker'].tolist())
#        with open('ETFtickers.pickle', 'wb') as f:
#            pickle.dump(tickers,f)
            
        return tickers

################################################################################
################################################################################

    def read_data(ticker):
        # Read price data for ETF: ticker and set index to date
        df = pd.read_csv(folder1+'/{}.csv'.format(ticker))
        df.set_index('Date', inplace=True)
        df = df[[ticker]]
        return df

    def save_data(ticker, start, end, yh='yahoo'):
        # Check if data is available for ticker between start and end for backtesting
        try:
            df = web.DataReader(ticker, yh, start, end)
            # Retrieve data from Yahoo Finance and apply filtering to dataset to get in proper format and save
            print('Getting {}'.format(ticker))
            df.rename(columns = {'Adj Close': ticker}, inplace=True)
            df = df[[ticker]]
            df.to_csv(folder1+'/{}.csv'.format(ticker)) 
            return read_data(ticker)
        except KeyError:
            # When no data is available
            print("No data for {} yet!".format(ticker))
            return 0
    
    def get_and_simplify_data(df, ticker, next_day, end, yh='yahoo'):
        # Check if additional data is available from the trading day after most recent data retrieval
        # to now
        try:
            df2 = web.DataReader(ticker, yh, next_day, end)
            # Retrieve additional data from Yahoo Finance and apply filtering and formatting
            print('Getting additional prices for {}'.format(ticker))
            df2.rename(columns = {'Adj Close': ticker}, inplace=True)
            df2 = df2[[ticker]]
            df = pd.concat([df, df2], ignore_index = False, sort=True)
            df = fix_dates(df)
            df.to_csv(folder1+'/{}.csv'.format(ticker))
            return df
        except KeyError:
            # When no more data is available, i.e. when run at a weekend
            print("No more data for {}".format(ticker))
            return 0
    
    def delete_data():
        # When reclustering the ETFs, one must first delete the previous analysis and returns of strategy
        # Try delete returns_for_analysis.csv
        try:
            os.remove("returns_for_analysis.csv")
        except FileNotFoundError as _:
            pass
        
        # Try delete Files in ETF_Analysis and ETF_Data
        folder = "ETF_Analysis"     
        for file in os.listdir("./"+folder):
            try:
                os.remove(folder+"/"+file)
            except FileNotFoundError as _:
                pass      
        
################################################################################
################################################################################
            
    def truncate(d):
        # Change from datetime to date
        return dt.date(d.year, d.month, d.day)
    
    def reduce(d):
        # Change from datetime to date string format
        d = truncate(d)
        return d.strftime("%Y-%m-%d")

################################################################################
################################################################################
    
    def get_date(d):
        # Convert from string format to datetime (inverse of reduce() function)
        return dt.datetime.strptime(d, '%Y-%m-%d')

    def fix_dates(df):
        # Fix dates of price data when programme is run twice in a day
        df = df.reset_index()
        for d in range(df.shape[0]):
            try:
                df.loc[d, 'Date'] = reduce(df.loc[d, 'Date'])
            except AttributeError:
                pass
        df = df.set_index('Date')
        return df

    def get_trading_days(start, end):
        # Get trading days between start and end dates
        nyse = mcal.get_calendar('NYSE')
        trading = nyse.schedule(start_date=start, end_date=end)
        trading_days=[]
        for t in range(len(trading)):
            trading_days.append(str(trading.index.values[t])[:10])
        return trading_days

################################################################################
################################################################################
    
    def get_cum_log_returns(main_df):
        # Get the cumulative returns of the price data available
        log_ret = pd.DataFrame()
        cum_log_ret = pd.DataFrame()
        tickers = main_df.columns
        for ticker in tickers:
            log_ret[ticker] = (np.log(main_df[ticker]) - np.log(main_df[ticker].shift(1)))
            cum_log_ret[ticker] = log_ret[ticker].cumsum()
        log_ret.to_csv(folder2+'/log_returns.csv')
        return log_ret, cum_log_ret
    
################################################################################
################################################################################
    
    if not recluster:
        # If user defines no repeat clustering, then get previous clustering result from storage and if none exists
        # then recluster tickers
        try:
            with open('universe_tickers.pickle', 'rb') as f:
                tickers = pickle.load(f)
        except FileNotFoundError as _:
            try:
                recluster = True
                with open('ETFatickers.pickle', 'rb') as f:
                    tickers = pickle.load(f)

            except FileNotFoundError as _:
                tickers = save_tickers() 
    else:
        # If user has defined to recluster tickers, then delete previous cluster analysis and recluster tickers using
        # specified cluster start and end dates
        delete_data()
        try:
            with open('ETFickers.pickle', 'rb') as f: 
                tickers = pickle.load(f)
        except FileNotFoundError as _:
            tickers = save_tickers() 
    
    # Check if "ETF_Data" exists in source file, then suggests programme has been run before, else run for first time     
    if os.path.exists(folder1):   
        # Loop through all ETFs to gather additional data
        for ticker in (tickers+hedge):
            try:
                df = read_data(ticker)
                n=0
                last_in_data = get_date(list(df.index)[-1][:10])
                
                if truncate(last_in_data) != truncate(end):
                    trading = get_trading_days(last_in_data+timedelta(days=1), end)
                else:
                    trading = []
                
                next_day = truncate(start)
                if n == 0 and len(trading)>0:
                    n+=1
                    for k in range(0,7):
                        next_day = get_date(trading[0])+timedelta(days=k)
                        next_day = truncate(next_day)
                        if next_day.weekday()<5:
                            break
                    
                if next_day<=truncate(end) and next_day != truncate(start):
                    if truncate(last_in_data)!=truncate(now) and len(trading)>1: 
                        df = get_and_simplify_data(df, ticker, next_day, end) 
                    else:
                        print('No new data for {} today!'.format(ticker))
                else:
                    print('Already have {}'.format(ticker)) 
                    
            except FileNotFoundError as _:
                df = save_data(ticker, start, end)
                
            try:
                if main_df.empty:
                    main_df = df
                else:
                    main_df = main_df.join(df, how='outer') 
            except TypeError:
                tickers.remove(ticker)

    else:
        os.makedirs(folder1)
        for ticker in (tickers+hedge):
            df = save_data(ticker, start, end)
            try:
                if main_df.empty:
                    main_df = df
                else:
                    main_df = main_df.join(df, how='outer')
            except TypeError:
                tickers.remove(ticker)
                
    main_df=main_df.reset_index()
    main_df=main_df.drop_duplicates(subset='Date', keep='first')
    main_df=main_df.set_index("Date")


    # Get log returns and cumulative log returns for available data
    log_ret, cum_log_ret = get_cum_log_returns(main_df)
    
    # Check if user wants to recluster, if so recluster the tickers using clustering_algo.py function cluster
    if recluster:
        startC, endC = reduce(startC), reduce(endC)
        tickers = clustering_algo.cluster(startC, endC, log_ret, cluster_on)
    
    # Simply data to only include the tickers according to clustering
    main_df = main_df[(tickers+hedge)]
    
    # Save pandas dataframe to memory, available for future processing 
    main_df.to_csv(folder2+"/All_Data.csv")

    # Return the clustered tickers with hedge strings, price data for clustered tickers 
    # only and cumulative log returns for clustered tickers only
    return (tickers+hedge), main_df[tickers], cum_log_ret[tickers]






