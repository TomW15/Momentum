# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 18:09:40 2020

@author: tomw1
"""

import datetime as dt
import pandas as pd
from forex_python.converter import get_rate


def get_forex(cur1="GBP", cur2="USD", folder="ETF_Analysis"):
    
    def get_date(d):
        return dt.datetime.strptime(d, '%Y-%m-%d')
    
    data = pd.read_csv(folder+'/All_data.csv', index_col=0)
    dates=list(data.index.values)[1:]
    filename = '/forex_{}_{}.csv'.format(cur1, cur2)
    try:
        forex = pd.read_csv(folder+filename)
        data_dates = list(forex.loc[:, "Date"])
        for day, i in zip(dates, range(len(dates))):
            if day not in data_dates:
                print("Getting new rate: " + day)
                forex.loc[i] = [day]+[get_rate(cur1, cur2, get_date(day[:10]).date())]

    except FileNotFoundError as _:
        forex = pd.DataFrame(columns=["Date", "FX"])
        for day, i in zip(dates, range(len(dates))):
            print("Getting rate for " + day)
            forex.loc[i] = [day]+[get_rate(cur1, cur2, get_date(day[:10]).date())] 

    forex = forex.set_index("Date")
    forex.to_csv(folder+filename)  
    return forex