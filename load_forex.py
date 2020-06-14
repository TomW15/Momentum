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
        # Convert string date format to datetime
        return dt.datetime.strptime(d, '%Y-%m-%d')
    # Get the data collected so far and extrapolate the dates
    data = pd.read_csv(folder+'/All_data.csv', index_col=0)
    dates=list(data.index.values)[1:]
    # Set filename between the two currencies (GBP --> USD)
    filename = 'forex_{}_{}.csv'.format(cur1, cur2)
    try:
        # Check if the file exists
        forex = pd.read_csv(filename)
        # Get all the dates for which we have an exchange rate
        data_dates = list(forex.loc[:, "Date"])
        # Loop through all the dates
        for day, i in zip(dates, range(len(dates))):
            # Check if we have the exchange rate for day
            if day not in data_dates:
                print("Getting new rate: " + day)
                # Add exchange rate to the i-th row of forex dataframe 
                forex.loc[i] = [day]+[get_rate(cur1, cur2, get_date(day[:10]).date())]

    except FileNotFoundError as _:
        # Since the file does not exist, loop through all dates and gather the exchange rate for each date
        forex = pd.DataFrame(columns=["Date", "FX"])
        for day, i in zip(dates, range(len(dates))):
            print("Getting rate for " + day)
            forex.loc[i] = [day]+[get_rate(cur1, cur2, get_date(day[:10]).date())] 
            
    # Set the index of forex dataframe to the date and save to filename
    forex = forex.set_index("Date")
    forex.to_csv(filename)