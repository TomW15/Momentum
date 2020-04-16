# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 16:45:14 2020

@author: tomw1
"""

import datetime as dt
import numpy as np
import pandas as pd
from collections import OrderedDict
from operator import itemgetter


def WinnersMinusLosers(tickers, data, clr, win_los, folder = 'ETF_Analysis'):
    
    def get_date(d):
        # Convert string date format to datetime
        return dt.datetime.strptime(d, '%Y-%m-%d')
    
    def get_periods(data, filename = "/months.csv"):
        # Set path for saving
        path = folder + filename
        # Set column names
        cols = ['StartF', 'EndF', 'StartH', 'EndH']
        try:
            months = pd.read_csv(path)
            # If programme previously run, months file will exist so gather dates from .csv file
            f_start = list(months[cols[0]])
            f_end = list(months[cols[1]])
            i_start = list(months[cols[2]])
            i_end = list(months[cols[3]])      
            
            # Initialize two lists which will contain the new starts and ends to months
            start_month, end_month = [], []
            # Gets dates from price data
            dates=list(data.index.values)[1:]
            # Get end of last investment period to start searching for new starts and ends
            last_end = i_end[-1]
            
            # Get the month of last investment month
            last_end_m = int(last_end[5:7])
            # Get the current month
            last_entry_m = dt.datetime.now().month
            
            # Get the index of last investment end in dates dataframe
            last_end_index = dates.index(last_end)
            # Set new dates list to be from the above index
            dates=list(data.index.values)[(last_end_index+2):]
            # Check if the current month less one is greater than the last investment month
            # i.e. check if another month has ended
            if last_end_m < (last_entry_m-1):
                # Get mod12 of last investment month loaded
                n = last_end_m%12
                # Loop through dates looking for a change in the month index
                for d in dates:
                    date_time_obj = get_date(d).date()
                    m = date_time_obj.month
                    if m!=n:
                        start_month.append(d)
                        if n != 0:
                            end_month.append(dates[dates.index(d)-1])
                        n=m
                
                # Add new found starts and ends with corresponding formation starts and ends
                i_start += start_month
                i_end += end_month
                f_start += i_start[-14:(-14+len(start_month))]
                f_end += i_end[-3:(-3+len(end_month))]
         
        except FileNotFoundError as _:
            # If months.csv does not exist, loop through all dates in price data to capture
            # all start and end dates throughout the investment horizon
            dates=list(data.index.values)[1:] + [dt.datetime.now().strftime("%Y-%m-%d")]
            n=0
            start_month = []
            end_month = []
            for d in dates:
                date_time_obj = get_date(d).date()
                m = date_time_obj.month
                if m!=n:
                    start_month.append(d)
                    if n != 0:
                        end_month.append(dates[dates.index(d)-1])
                    n=m
            # Retrieve all investment and formation periods from start and end month lists 
            end_month = end_month[11:]
            f_start = start_month[:-13]   
            f_end = end_month[:-2]
            i_start = start_month[13:]
            i_end = end_month[2:]
        # Create pandas dataframe using lists found and save the dataframe in a .csv file    
        months = pd.DataFrame(list(zip(f_start, f_end, i_start, i_end)), columns =cols)
        months.to_csv(path)
        # Return the list of start months
        return start_month

###############################################################################
###############################################################################

    def get_WML(WML, L, clr, win_los):
        
        def get_cum_returns(universe, cum_log_ret_universe, start, end):
            # Get cumulative returns between two dates
            cumulative = dict()
            for u in universe:
                cumulative[u] = cum_log_ret_universe.loc[end, u]-cum_log_ret_universe.loc[start, u]
                if np.isnan(cumulative[u]):
                    del cumulative[u]    
            return cumulative
        # Get the tickers from keys in clr dictionary
        tickers = clr.keys()
        # Initialize wml list
        wml = []
        # Define columns to get new months to loop through
        cols = ['StartF', 'EndF', 'StartH', 'EndH']
        months = pd.read_csv(folder+"/months.csv")
        f_start = list(months[cols[0]])[-L:]
        f_end = list(months[cols[1]])[-L:]
        i_start = list(months[cols[2]])[-L:]
        i_end = list(months[cols[3]])[-L:]
        s_start = (f_start[7:] + i_start[-13:-6])[-L:]
        s_end = (f_end[1:] + i_end[-2:-1])[-L:]  
        # Loop through each set of investment periods with required scaling and formation periods to find winners and losers for each month
        for FS, FE, SS, SE, IS, IE in zip(f_start, f_end, s_start, s_end, i_start, i_end):
            # Get cumulative returns over the formation period
            cum = get_cum_returns(tickers, clr, FS, FE) 
            # Order the cumulative returns in descending order
            cums=OrderedDict(sorted(cum.items(), key = itemgetter(1), reverse = True))
            # Create a list using the ordered keys
            order = list(cums.keys())
            # Get the top 'win_los' and bottom 'win_los' where 'win_los' is the number of long-short positions
            # taken defined by the user in 'Strategy_Main.py'
            winners, losers = order[:win_los], order[-win_los:]
            # Add the information to a list
            wml.append([FS, FE, SS, SE, IS, IE, winners, losers])
        # Add gathered information to a pandas dataframe which is then saved as "WML_Old.csv"
        col_names = ['StartF', 'EndF', 'StartS', 'EndS', 'StartH', 'EndH', 'Winners', 'Losers']
        WML_new = pd.DataFrame(wml, columns=col_names)
        WML = pd.concat([WML, WML_new], ignore_index = True)
        WML.to_csv (folder+"/WML_Old.csv", index = None, header=True)      

    def get_strategy(data, new_starts, clr, win_los):
        L=0
        try:
            WML = pd.read_csv(folder+"/WML_Old.csv")
            # Get the number of new start months
            L = len(new_starts)
            if L > 0:
                # Get the new winners and losers for the new start months
                get_WML(WML, L, clr, win_los)
                
        except FileNotFoundError as _:
            # As file does not exist, run function to gather all winners and losers
            # for the investment horizon found
            col_names = ['StartF', 'EndF', 'StartS', 'EndS', 'StartH', 'EndH', 'Winners', 'Losers']
            WML = pd.DataFrame(columns = col_names)
            get_WML(WML, L, clr, win_los)
    
    # Get the set of months for which we don't have the winners and losers        
    new_starts = get_periods(data[tickers[:-2]])  
    # Find the winners and losers for the new months
    get_strategy(data[tickers[:-2]], new_starts, clr, win_los)

                
                
                
            
            
            
            
            
            
            
            
            
            
            
            