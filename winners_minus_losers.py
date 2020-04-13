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
        return dt.datetime.strptime(d, '%Y-%m-%d')
    
    def get_periods(data):
        filename = "/months.csv"
        path = folder + filename
        cols = ['StartF', 'EndF', 'StartH', 'EndH']
        try:
            months = pd.read_csv(path)
            
            f_start = list(months[cols[0]])
            f_end = list(months[cols[1]])
            i_start = list(months[cols[2]])
            i_end = list(months[cols[3]])      
            
            start_month, end_month = [], []
            dates=list(data.index.values)[1:]
            last_end = i_end[-1]
            
            last_end_m = int(last_end[5:7])
            
            #####
            last_entry_m = dt.datetime.now().month
            
            #####
            
#            last_entry_m = int(data.index[-1][6])
            last_end_index = dates.index(last_end)
            dates=list(data.index.values)[(last_end_index+2):]
            
            if last_end_m < (last_entry_m-1):
                n = last_end_m%12
                for d in dates:
                    date_time_obj = get_date(d).date()
                    m = date_time_obj.month
                    if m!=n:
                        start_month.append(d)
                        if n != 0:
                            end_month.append(dates[dates.index(d)-1])
                        n=m
                
                i_start += start_month
                i_end += end_month
                f_start += i_start[-14:(-14+len(start_month))]
                f_end += i_end[-3:(-3+len(end_month))]
         
        except FileNotFoundError as _:
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
             
            end_month = end_month[11:]
            f_start = start_month[:-13]   
            f_end = end_month[:-2]
            i_start = start_month[13:]
            i_end = end_month[2:]
            
        months = pd.DataFrame(list(zip(f_start, f_end, i_start, i_end)), columns =cols)
        months.to_csv(path)
        
        return start_month

###############################################################################
###############################################################################

    def get_WML(WML, L, clr, win_los):
        
        def get_cum_returns(universe, cum_log_ret_universe, start, end):
            cumulative = dict()
            for u in universe:
                cumulative[u] = cum_log_ret_universe.loc[end, u]-cum_log_ret_universe.loc[start, u]
                if np.isnan(cumulative[u]):
                    del cumulative[u]    
            return cumulative
        
        tickers = clr.keys()
        wml = []
        cols = ['StartF', 'EndF', 'StartH', 'EndH']
        months = pd.read_csv(folder+"/months.csv")
        f_start = list(months[cols[0]])[-L:]
        f_end = list(months[cols[1]])[-L:]
        i_start = list(months[cols[2]])[-L:]
        i_end = list(months[cols[3]])[-L:]
        s_start = (f_start[7:] + i_start[-13:-6])[-L:]
        s_end = (f_end[1:] + i_end[-2:-1])[-L:]  
        
        for FS, FE, SS, SE, IS, IE in zip(f_start, f_end, s_start, s_end, i_start, i_end):
            cum = get_cum_returns(tickers, clr, FS, FE) 
            cums=OrderedDict(sorted(cum.items(), key = itemgetter(1), reverse = True))
            order = list(cums.keys())
            winners, losers = order[:win_los], order[-win_los:]
    
            wml.append([FS, FE, SS, SE, IS, IE, winners, losers])
        
        col_names = ['StartF', 'EndF', 'StartS', 'EndS', 'StartH', 'EndH', 'Winners', 'Losers']
        WML_new = pd.DataFrame(wml, columns=col_names)
        WML = pd.concat([WML, WML_new], ignore_index = True)
        WML.to_csv (folder+"/WML_Old.csv", index = None, header=True)      

    def get_strategy(data, new_starts, clr, win_los):
        L=0
        try:
            WML = pd.read_csv(folder+"/WML_Old.csv")
            L = len(new_starts)
            if L > 0:
                get_WML(WML, L, clr, win_los)
                
        except FileNotFoundError as _:
            col_names = ['StartF', 'EndF', 'StartS', 'EndS', 'StartH', 'EndH', 'Winners', 'Losers']
            WML = pd.DataFrame(columns = col_names)
            get_WML(WML, L, clr, win_los)
            
    new_starts = get_periods(data[tickers[:-2]])  
    get_strategy(data[tickers[:-2]], new_starts, clr, win_los)

                
                
                
            
            
            
            
            
            
            
            
            
            
            
            