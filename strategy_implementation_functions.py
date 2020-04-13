# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 16:10:57 2020

@author: tomw1
"""

import numpy as np
import pandas as pd
import pickle
import re

folder = "ETF_Analysis"

def get_details(cur1="GBP", cur2="USD"):
    
    def get_list(my_list, pattern = "'(.*?)'"):
        return re.findall(pattern, my_list)
        
    with open('universe_tickers.pickle', 'rb') as f:
        tickers = pickle.load(f)
        
    dfList = pd.read_csv(folder+'/WML_Old.csv')
    
    prices = pd.read_csv(folder+'/All_data.csv')
    prices = prices.set_index('Date')
    prices = pd.DataFrame.fillna(prices, 0)
    
    forex = pd.read_csv('forex_{}_{}.csv'.format(cur1, cur2)).set_index('Date')
#    forex = forex
    
    returns = pd.read_csv(folder+'/log_returns.csv')
    returns = pd.DataFrame.fillna(returns, 0)
    returns = returns.set_index('Date')

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
    
    return tickers, prices, returns, winners, losers, startF, endF, startH, endH, startS, endS, forex
    
def scaling_variance(returns, winners, losers, startS, endS, targetSD = np.sqrt(12)/100, momentumWeight = 0.5):
    """
        Inputs:
            returns - returns for all investment horizon across all ETFs
            winners(losers) - set of winners(losers) for the (t+1)-th investment period
            startS, endS - scaling start and end dates for the (t+1)-th investment period
            targetSD - target standard deviation/volatility for the portfolio which could be changed to an input and set by the user
            
        Function:
            Gets the returns for the dummy WML portfolio over the scaling period and returns the weight of portfolio on the
            momentum strategy
        
        Returns:
            Single Value (weight) to be invested in the momentum strategy
    """
    
    # Set i equal to zero to separate first winner(loser) and the rest of the winners(losers) for time period t
    i = 0
    # Loop through the all the winners and losers for time period t
    for win, lose in zip(winners, losers):
        # Check if in first loop of winners and losers
        if i == 0:
            # Set the scaling period returns equal to the returns of the first winner minus the first loser for the t-th scaling period
            scaling_returns = returns[startS:endS][win]-returns[startS:endS][lose]
            # Add one to i such that we never enter this case again
            i += 1
        else:
            # Add WML returns for each of the remaining winners and losers for time period t with the t-th scaling period dates
            scaling_returns += (returns[startS:endS][win]-returns[startS:endS][lose])

    # As we are investing in 4 long ETFs and 4 short ETFs, we divide the returns by 4  
    scaling_returns /= 4
    # To get the scaling period standard deviation (volatility), we square all the scaling period returns then sum and 
    # divide by 6 to get the monthly variance for the equally-weighted WML dummy portfolio for the t-th scaling period
    scalingSD = np.sqrt(sum(scaling_returns**2)/6)
    
    # Return the volatility-scaled weight for the momentum strategy with target variance equal to 12%
    # and multiply the weight by 0.5 as this is 50% of our portfolio strategy
    return round(targetSD/scalingSD * momentumWeight,2), scalingSD

def New_Portfolio(tickers, hedge, winners, losers, momWeight):
    positions = {ticker:0 for ticker in (tickers+hedge)}
    
    for win, lose in zip(winners, losers):
        positions[win] = momWeight/4
        positions[lose] = -momWeight/4 # have to check if divide by 4 is correct or should it be 8?
    
    positions['VTV'] = (1-momWeight)/2
    positions['SPY'] = -(1-momWeight)/2
    return positions

def costChanges(positions, pos_changes, value, prices, date, vol_charge_per_share=0.0035, clear_charge_per_share = 0.002, quoteDriven = True, totalCost = 0):
    
    """
        Volume
        0.0035$ per share
        0.35$ < fee < 1% of trade value
        1% if fee < 0.35$, so if < 100 shares
        
        No sales, so no transaction costs
        Unclear as to pass-through fees, assumed to apply to purchases
        0.0035*0.000175* number of shares
        
        Clearing
        0.0002$ per share
        
        Exchange
        0.003$ per quote driven order
        -0.002$ per order driver order (a rebate)
        
        My interpretation:
            - Volume cost:
                If 0.0035*shares < 0.35 then charged 0.35
                If 1% of invested capital < 0.35 then charged 1% of invested capital
            
            - Transaction cost:
                If shorting then charged 0.0000207*invested capital
            
            - Clearing cost:
                Charged 0.002 * absolute number of shares
            
            - Pass Through Cost
                0.0035 * 0.000175 * absolute number of shares 
                
            - Exchange Cost
                If quoteDriven which we assume we are, 0.003
                Else -0.002
    
    """
    
    shares = {ticker:0 for ticker in (pos_changes.keys())}
    
    for ticker in pos_changes.keys():
        if pos_changes[ticker] != 0:

            price = prices[ticker][date]
            invested = value*abs(pos_changes[ticker])
            shares[ticker] = invested/price # Not sure if we can invest in fractions but very small difference I assume
            
            # Volume Costs
            volume_charge = vol_charge_per_share*shares[ticker]
            if volume_charge < 0.35:
                volume_charge = 0.35
            if invested/100 < 0.35:
                volume_charge = invested/100
            
            # Transaction Costs
            trans_charge = 0
            if positions[ticker] < 0:
                trans_charge = 0.0000207*invested
            else:
                trans_charge = 0
            
            # Clearing Costs            
            clearing_charge = clear_charge_per_share * abs(shares[ticker])
            
            # Pass Through Cost
            pass_thru_charge = 0.0035 * 0.000175 * abs(shares[ticker])
            
            # Exchange Cost
            if quoteDriven:
                exchange_charge = 0.003
            else:
                exchange_charge = -0.002
                
            Cost = (volume_charge+trans_charge+clearing_charge+pass_thru_charge+exchange_charge)
#            print("Cost for {} is {}".format(ticker, Cost))
            totalCost += Cost
#            print("Volume Charge: ", volume_charge)
#            print("Transaction Charge: ", trans_charge)
#            print("Clearing Charge: ", clearing_charge)
#            print("Pass-Thru Charge: ", pass_thru_charge)
#            print("Exchange Charge: ", exchange_charge)
#            print("Total Cost: ", totalCost)
    
    return round(totalCost,2)

def invest(prices, tickers, hedge, winners, losers, investment, momWeight, startH):
    
    hedgeWeight = 1 - momWeight
    
    shares = {ticker:0 for ticker in (tickers+hedge)}
    for win, lose in zip(winners, losers):
        shares[win] = (investment*momWeight/4)/prices[win][startH]
        shares[lose] = -(investment*momWeight/4)/prices[lose][startH]
    
    shares['VTV'] = investment*hedgeWeight/prices['VTV'][startH]
    shares['SPY'] = -investment*hedgeWeight/prices['SPY'][startH]

    return shares
    
def get_value(prices, shares, winners, losers, hedge, dfValue, forex, value):
    dates = list(prices.index.values)
    port_value_USD, port_value_GBP = [], []
    for date in dates:
        port_value_USD.append(sum([shares[ticker]*prices[ticker][date] for ticker in (winners+losers+hedge)])+value)
        port_value_GBP.append(port_value_USD[-1]/forex['FX'][date])
    
    port_value = pd.DataFrame({'Date':dates, 'Port. Value (USD)': port_value_USD, 'Port. Value (GBP)': port_value_GBP}).set_index('Date')
    
    port_value = pd.concat([dfValue, port_value])
    
    monthlyReturn = np.log(port_value_USD[-1]/value)
    momReturn = sum([shares[ticker]*prices[ticker][date] for ticker in (winners+losers)])
    hedgeReturn = sum([shares[ticker]*prices[ticker][date] for ticker in hedge])
    
    return port_value, monthlyReturn, momReturn, hedgeReturn



"""
    Functions:
        
        - Get winners and losers for current period
            - XXX Get scaling period variance for momentum scaling using winners and losers
            
            - XXX Get weights function using scaling period variance
            
            - if first investment period, calculate cost of implementing strategy
            - else calculate change in investments and calculate cost of changing portfolio
            
            - Get costs for changing investments
            
            - Choice to do cumulative or Chris' way of investing
            
            - Return RiskMetrics, Cumulative Return, Monthly Returns, Monthly Standard Deviation, Daily Return
            
        - Allow optional changes to hedge dynamics
        - Smooth weight investing, only perform if weight/investment is significantly different

"""