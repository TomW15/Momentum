# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 21:07:02 2020

@author: tomw1
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statistics
import sys

from tabulate import tabulate
from scipy.stats import norm
import scipy.stats as st

# Import necessary .py files
import plot_data
import RiskMetrics
import strategy_implementation_functions

def strategy():
    
    # Gather all information from previous processing
    tickers, prices, returns, winners, losers, startF, endF, startH, endH, startS, endS, forex = strategy_implementation_functions.get_details()
#    tickers, prices, returns, winners, losers, startF, endF, startH, endH, startS, endS, forex = get_details()
    hedge = list(set(prices.keys())-set(tickers))
    
    # Initialize a dictionary containing all positions in the ETFs and hedge (default is zero)
    positions = {ticker:0 for ticker in (tickers+hedge)}
    # Similar dictionary for shares
    shares = positions
    # Set initial value of portfolio to 10000
    value = 10000
    # Initialize a portfolio dataframe containing value of portfolio is dollars and pounds
    portfolio_value = pd.DataFrame([("Initial Investment", value, value/forex['FX'][startH[0]])], columns = ["Date", "Port. Value (USD)", "Port. Value (GBP)"]).set_index("Date")
    
    # Initialize empty lists to collect information from strategy run through
    historic_costs = []
    historic_weights = []
    monthlyReturns = []
    momReturns = []
    hedgeReturns = []
    vol_scalingSD = []
    
    # Loop through all time periods
    for t in range(len(winners)):
        # Run scaling variance function to get the momentum weight and scaling standard deviation and add these values
        # to two separate lists
        momWeight, scalingSD = strategy_implementation_functions.scaling_variance(returns, winners[t], losers[t], startS[t], endS[t])
#        momWeight, scalingSD = scaling_variance(returns, winners[t], losers[t], startS[t], endS[t])
        historic_weights.append(momWeight)
        vol_scalingSD.append(scalingSD)
    
        # Run new_portfolio function to get the new positions in each of the winners and losers for the 
        # current time period and find the difference between this new portfolio and the last portfolio
        # to cost the change
        new_positions = strategy_implementation_functions.New_Portfolio(tickers, hedge, winners[t], losers[t], momWeight)
#        new_positions = New_Portfolio(tickers, hedge, winners[t], losers[t], momWeight)
        position_changes = {ticker:(new_positions[ticker]-positions[ticker]) for ticker in (tickers+hedge)}
        
        # Run the costChanges function to find the cost of the change to the portfolio calculated above and add to list
        # - Future advancements to function should discretize changes 
        cost = strategy_implementation_functions.costChanges(new_positions, position_changes, value, prices, startH[t])
#        cost = costChanges(new_positions, position_changes, value, prices, startH[t])
        historic_costs.append(cost)
        
        # Subtract cost from value of portfolio
        value -= cost
        
        # Using remaining cash to invest, calculate the shares in each ticker by running invest function
        shares = strategy_implementation_functions.invest(prices, tickers, hedge, winners[t], losers[t], value, momWeight, startH[t])
#        shares = invest(prices, tickers, hedge, winners[t], losers[t], value, momWeight, startH[t])
        
        # Run the get_value function to fast forward through holding periods and add returns to lists
        portfolio_value, monthReturn, momReturn, hedgeReturn = strategy_implementation_functions.get_value(prices[startH[t]:endH[t]], shares, winners[t], losers[t], hedge, portfolio_value, forex, value)
#        portfolio_value, monthReturn, momReturn, hedgeReturn = get_value(prices[startH[t]:endH[t]], shares, winners[t], losers[t], hedge, portfolio_value, forex, value)
        monthlyReturns.append(monthReturn)
        momReturns.append(np.log((momReturn+momWeight*value)/(momWeight*value)))
        hedgeReturns.append(np.log((hedgeReturn+(1-momWeight)*value)/((1-momWeight)*value)))
        
        # Get the new value of the portfolio at the end of the holding period and set the current positions
        # to the new positions set this period
        value = portfolio_value.loc[endH[t]]["Port. Value (USD)"]
        positions = new_positions
    # Get the portfolio values in USD and GBP in two separate lists
    port_value_USD = list(portfolio_value["Port. Value (USD)"])
    port_value_GBP = portfolio_value["Port. Value (GBP)"]
    # Get the returns from the value of the portfolio using initial 10000 portfolio value
    port_returns_USD = [np.log(port_value_USD[t]/port_value_USD[0]) for t in range(len(port_value_USD))]
    port_returns_GBP = [np.log(port_value_GBP[t]/port_value_GBP[0]) for t in range(len(port_value_GBP))]
    
    
    # Start plotting results:
    
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
        
    
    # Calculate and plot risk analysis:
    
    # Calculate the mean monthly return and standard deviation of monthly returns
    mean_monthreturn = np.mean(strategy_returns["Monthly"])
    std_monthreturn = np.std(strategy_returns["Monthly"])
    # Using the above, one can calculate the Sharpe ratio
    sharpe_ratio = mean_monthreturn/std_monthreturn
    # Calculate the max drawdown and plot the drawdown
    MDD = RiskMetrics.max_drawdown(np.array(port_returns_USD)+1)
    RiskMetrics.plotDrawdown(port_returns["Port. Return (USD)"])
    
    # Calculate the 99, 95 and 90% value at risk followed by the conditional 
    # value at risk for same confidence intervals for monthly returns
    VAR_1_mon = RiskMetrics.valueAR(strategy_returns["Monthly"], 1)
    VAR_5_mon = RiskMetrics.valueAR(strategy_returns["Monthly"], 5)
    VAR_10_mon = RiskMetrics.valueAR(strategy_returns["Monthly"], 10)
    CVAR_1_mon = RiskMetrics.cVAR(strategy_returns["Monthly"], 1)
    CVAR_5_mon = RiskMetrics.cVAR(strategy_returns["Monthly"], 5)
    CVAR_10_mon = RiskMetrics.cVAR(strategy_returns["Monthly"], 10)
    
    # Plot the monthly returns
    plt.hist(strategy_returns["Monthly"], bins=30)
    plt.xlabel("Monthly Returns")
    plt.ylabel("Frequency")
    plt.title("Monthly Returns Frequency")
    plt.grid(True)
    plt.show()
    
    # Create a table containing all risk metrics used  - use pip install tabulate if error
    print(tabulate([['Mean', "{:.3%}".format(mean_monthreturn)], ['Std Dev.', "{:.3%}".format(std_monthreturn)], ['Sharpe Ratio', "{:.3}".format(sharpe_ratio)], ['Kurtosis', "{:.3}".format(st.kurtosis(strategy_returns["Monthly"]))], ['Skewness', "{:.3}".format(st.skew(strategy_returns["Monthly"]))]], headers=["Portfolio", ""]), "\n")
    print(tabulate([['90%', "{:.3%}".format(-VAR_10_mon), "{:.3%}".format(-CVAR_10_mon)], ['95%', "{:.3%}".format(-VAR_5_mon), "{:.3%}".format(-CVAR_5_mon)], ['99%', "{:.3%}".format(-VAR_1_mon), "{:.3%}".format(-CVAR_1_mon)]], headers=["Confidence Interval", "VAR", "Cond. VAR"]))

    # Get daily returns using daily portfolio value
    returns = portfolio_value.reset_index()["Port. Value (USD)"].pct_change()[1:]
    # Calculate the mean daily return and standard deviation of daily returns
    mean_dailyreturn = np.mean(returns)
    std_dailyreturn = np.std(returns)
    
    # Calculate the 99, 95 and 90% value at risk followed by the conditional 
    # value at risk for same confidence intervals for daily returns
    VAR_1 = RiskMetrics.valueAR(returns, 1)
    VAR_5 = RiskMetrics.valueAR(returns, 5)
    VAR_10 = RiskMetrics.valueAR(returns, 10)
    CVAR_1 = RiskMetrics.cVAR(returns, 1)
    CVAR_5 = RiskMetrics.cVAR(returns, 5)
    CVAR_10 = RiskMetrics.cVAR(returns, 10)
    
    # Plot the daily returns
    plt.hist(returns, bins=100)
    x = np.linspace(mean_dailyreturn-7*std_dailyreturn, mean_dailyreturn+7*std_dailyreturn, 100)
    plt.plot(x, norm.pdf(x, mean_dailyreturn, std_dailyreturn), 'r')
    plt.xlabel("Daily Returns")
    plt.ylabel("Frequency")
    plt.title("Daily Returns Frequency")
    plt.grid(True)
    plt.show()
    
    # Create a table containing all risk metrics used  - use pip install tabulate if error
    print(tabulate([['Mean', "{:.3%}".format(mean_dailyreturn)], ['Std Dev.', "{:.3%}".format(std_dailyreturn)], ['Kurtosis', "{:.3}".format(st.kurtosis(returns))], ['Skewness', "{:.3}".format(st.skew(returns))], ['Max Drawdown', "{:.3%}".format(MDD)], ["Semi Std Dev.", "{:.3%}".format(RiskMetrics.semiv(returns))]], headers=["Portfolio", ""]), "\n")
    print(tabulate([['90%', "{:.3%}".format(-VAR_10), "{:.3%}".format(-CVAR_10)], ['95%', "{:.3%}".format(-VAR_5), "{:.3%}".format(-CVAR_5)], ['99%', "{:.3%}".format(-VAR_1), "{:.3%}".format(-CVAR_1)]], headers=["Confidence Interval", "VAR", "Cond. VAR"]))
    
        
    

