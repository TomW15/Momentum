# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 21:07:02 2020

@author: tomw1
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
import re
import statistics
import sys

from tabulate import tabulate
from scipy.stats import norm
import scipy.stats as st

import plot_data
import RiskMetrics

def strategy():
    
    def get_details(cur1="GBP", cur2="USD", folder="ETF_Analysis"):
        
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
        return targetSD/scalingSD * momentumWeight, scalingSD
    
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
        
        return totalCost
    
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
                
                - if first investment period, calculate cost of implementing strategy: potentially start with ["ICLSIF"]x4
                - else calculate change in investments and calculate cost of changing portfolio
                
                - Get costs for changing investments
                
                - Choice to do cumulative or Chris' way of investing
                
                - Return RiskMetrics, Cumulative Return, Monthly Returns, Monthly Standard Deviation, Daily Return
                
            - Allow optional changes to hedge dynamics
            - Smooth weight investing, only perform if weight/investment is significantly different
    
    """
    
    print("Getting analysis...")
    tickers, prices, returns, winners, losers, startF, endF, startH, endH, startS, endS, forex = get_details()
    hedge = list(set(prices.keys())-set(tickers))
    print("Got analysis...")
    
    positions = {ticker:0 for ticker in (tickers+hedge)}
    shares = positions
    value = 10000
    portfolio_value = pd.DataFrame([("Initial Investment", value, value/forex['FX'][startH[0]])], columns = ["Date", "Port. Value (USD)", "Port. Value (GBP)"]).set_index("Date")
    
    historic_costs = []
    historic_weights = []
    monthlyReturns = []
    momReturns = []
    hedgeReturns = []
    vol_scalingSD = []
    
    for t in range(len(winners)):
        
        momWeight, scalingSD = scaling_variance(returns, winners[t], losers[t], startS[t], endS[t])
        historic_weights.append(momWeight)
        vol_scalingSD.append(scalingSD)
    
        new_positions = New_Portfolio(tickers, hedge, winners[t], losers[t], momWeight)
        position_changes = {ticker:(new_positions[ticker]-positions[ticker]) for ticker in (tickers+hedge)}
        
        cost = costChanges(new_positions, position_changes, value, prices, startH[t])
        historic_costs.append(cost)
        
        # calculate cost of investment and subtract from possible Investment
        value -= cost
        
        # invest remaining cash (value of portfolio minus costs) in strategy
        shares = invest(prices, tickers, hedge, winners[t], losers[t], value, momWeight, startH[t])
        
        # zoom through holding period to find daily returns for investment strategy
        portfolio_value, monthReturn, momReturn, hedgeReturn = get_value(prices[startH[t]:endH[t]], shares, winners[t], losers[t], hedge, portfolio_value, forex, value)
        
        monthlyReturns.append(monthReturn)
        momReturns.append(np.log((momReturn+momWeight*value)/(momWeight*value)))
        hedgeReturns.append(np.log((hedgeReturn+(1-momWeight)*value)/((1-momWeight)*value)))
        
        value = portfolio_value.loc[endH[t]]["Port. Value (USD)"]
        positions = new_positions
    
    port_value_USD = list(portfolio_value["Port. Value (USD)"])
    port_value_GBP = portfolio_value["Port. Value (GBP)"]
    
    port_returns_USD = [np.log(port_value_USD[t]/port_value_USD[0]) for t in range(len(port_value_USD))]
    port_returns_GBP = [np.log(port_value_GBP[t]/port_value_GBP[0]) for t in range(len(port_value_GBP))]
    
    #portfolio_value.to_csv("Portfolio_Value.csv")
    #port_return.to_csv("Portfolio_Returns.csv")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    print("PLOT RESULTS")
    
    # Plot Monthly Returns, Momentum Returns, Hedge Returns
    strategy_returns = pd.DataFrame({'Month':startH[:(t+1)], 'Monthly': monthlyReturns, 'Momentum':momReturns, 'Hedge':hedgeReturns})
    plot_data.plot_same_axis(strategy_returns)
    
    # Plot Daily Returns in USD, GBP and FOREX - fix colours
    port_returns = pd.DataFrame({'Date':list(prices[startH[0]:endH.iloc[t]].index.values), 'Port. Return (USD)': port_returns_USD[1:], 'Port. Return (GBP)': port_returns_GBP[1:]})
    plot_data.plot_diff_axis(port_returns, forex[startH[0]:endH[t]])
    
    # Plot momentum weights versus portfolio standard deviation of that month
    within_monthSD = [statistics.stdev(port_returns.set_index('Date')['Port. Return (USD)'][startH[t]:endH[t]]) for t in range(len(winners))]
    vol_vs_weight = pd.DataFrame({'Month':startH[:(t+1)], "Month Volatility (%)":np.array(within_monthSD)*100, "Momentum Weight":np.array(historic_weights)*2})
    plot_data.plot_scatter(vol_vs_weight)
    
    # Plot Historic Returns Vs Portfolio Standard Deviation within month
    vol_vs_return = pd.DataFrame({'Month':startH[:(t+1)], "Month Volatility (%)":np.array(within_monthSD)*100, "Month Return":monthlyReturns})
    plot_data.plot_scatter(vol_vs_return)
    
    # Plot historic costs with historic costs as percentage of value
    historic_costs = pd.DataFrame({"Month":startH[:(t+1)], "Cost ($)":historic_costs})
    cost_percent = pd.DataFrame({"Month":startH[:(t+1)], "Percentage of Port. Value (%)":np.array([c/v for c,v in zip(historic_costs["Cost ($)"], port_value_USD)])*100})
    plot_data.plot_diff_axis(historic_costs, cost_percent)
    
    # Plot strategy returns versus benchmark: SPY
    strategy_versus_bench = pd.DataFrame({'Date':list(prices[startH[0]:endH.iloc[t]].index.values), 'Strategy':port_returns_USD[1:], 'Benchmark (SPY)':returns['SPY'][startH[0]:endH.iloc[t]].values.cumsum()})
    plot_data.plot_same_axis(strategy_versus_bench)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    print("RISK ANALYSIS")
    
    mean_monthreturn = np.mean(strategy_returns["Monthly"])
    std_monthreturn = np.std(strategy_returns["Monthly"])
    MDD = RiskMetrics.max_drawdown(np.array(port_returns_USD)+1)
    RiskMetrics.plotDrawdown(port_returns["Port. Return (USD)"])
    
    VAR_1_mon = RiskMetrics.valueAR(strategy_returns["Monthly"], 1)
    VAR_5_mon = RiskMetrics.valueAR(strategy_returns["Monthly"], 5)
    VAR_10_mon = RiskMetrics.valueAR(strategy_returns["Monthly"], 10)
    CVAR_1_mon = RiskMetrics.cVAR(strategy_returns["Monthly"], 1)
    CVAR_5_mon = RiskMetrics.cVAR(strategy_returns["Monthly"], 5)
    CVAR_10_mon = RiskMetrics.cVAR(strategy_returns["Monthly"], 10)
    
    returns = portfolio_value.reset_index()["Port. Value (USD)"].pct_change()[1:]
    mean_dailyreturn = np.mean(returns)
    std_dailyreturn = np.std(returns)
    
    VAR_1 = RiskMetrics.valueAR(returns, 1)
    VAR_5 = RiskMetrics.valueAR(returns, 5)
    VAR_10 = RiskMetrics.valueAR(returns, 10)
    CVAR_1 = RiskMetrics.cVAR(returns, 1)
    CVAR_5 = RiskMetrics.cVAR(returns, 5)
    CVAR_10 = RiskMetrics.cVAR(returns, 10)
    
    plt.hist(strategy_returns["Monthly"], bins=30)
    plt.xlabel("Monthly Returns")
    plt.ylabel("Frequency")
    plt.title("Monthly Returns Frequency")
    plt.grid(True)
    plt.show()
    
    # pip install tabulate
    print(tabulate([['Mean', "{:.3%}".format(mean_monthreturn)], ['Std Dev.', "{:.3%}".format(std_monthreturn)], ['Kurtosis', "{:.3}".format(st.kurtosis(strategy_returns["Monthly"]))], ['Skewness', "{:.3}".format(st.skew(strategy_returns["Monthly"]))]], headers=["Portfolio", ""]), "\n")
    
    print(tabulate([['90%', "{:.3%}".format(-VAR_10_mon), "{:.3%}".format(-CVAR_10_mon)], ['95%', "{:.3%}".format(-VAR_5_mon), "{:.3%}".format(-CVAR_5_mon)], ['99%', "{:.3%}".format(-VAR_1_mon), "{:.3%}".format(-CVAR_1_mon)]], headers=["Confidence Interval", "VAR", "Cond. VAR"]))
       
    plt.hist(returns, bins=100)
    x = np.linspace(mean_dailyreturn-3*std_dailyreturn, mean_dailyreturn+3*std_dailyreturn, 100)
    plt.plot(x, norm.pdf(x, mean_dailyreturn, std_dailyreturn), 'r')
    plt.xlabel("Daily Returns")
    plt.ylabel("Frequency")
    plt.title("Daily Returns Frequency")
    plt.grid(True)
    plt.show()
    
    print(tabulate([['Mean', "{:.3%}".format(mean_dailyreturn)], ['Std Dev.', "{:.3%}".format(std_dailyreturn)], ['Kurtosis', "{:.3}".format(st.kurtosis(returns))], ['Skewness', "{:.3}".format(st.skew(returns))], ['Max Drawdown', "{:.3%}".format(MDD)], ["Semi Std Dev.", "{:.3%}".format(RiskMetrics.semiv(returns))]], headers=["Portfolio", ""]), "\n")
    
    print(tabulate([['90%', "{:.3%}".format(-VAR_10), "{:.3%}".format(-CVAR_10)], ['95%', "{:.3%}".format(-VAR_5), "{:.3%}".format(-CVAR_5)], ['99%', "{:.3%}".format(-VAR_1), "{:.3%}".format(-CVAR_1)]], headers=["Confidence Interval", "VAR", "Cond. VAR"]))
    
        
    

