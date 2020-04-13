# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 18:09:00 2020

@author: tomw1
"""

import matplotlib.pyplot as plt
from matplotlib import interactive
interactive('True')
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import pickle
import re
import scipy.stats as st

import RiskMetrics

import sys
        
def momentum_strategy(num, targetSD = np.sqrt(12) / 100, folder="ETF_Analysis"):
    
    def getCSVPrice(t, start, end): 
        prices = dfP.loc[start : end, t]
        return prices
    
    def getCSVRet(t, start, end): 
        rets = dfRet.loc[start:end, t]
        return rets 
    
    def get_list(my_list, pattern = "'(.*?)'"):
        return re.findall(pattern, my_list)
        
    #########################################################################################################
    #########################################################################################################
    #########################################################################################################
    
    def get_details(cur1="GBP", cur2="USD"):
        
        with open('universe_tickers.pickle', 'rb') as f:
            tickers = pickle.load(f)
            
        dfList = pd.read_csv(folder+'/WML_Old.csv')
        
        dfP = pd.read_csv(folder+'/All_data.csv')
        dfP = dfP.set_index('Date')
        dfP = pd.DataFrame.fillna(dfP, 0)
        
        forex = pd.read_csv('forex_{}_{}.csv'.format(cur1, cur2))
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
    
    print("Getting analysis...")
    tickers, dfP, dfRet, winners, losers, startF, endF, startH, endH, startS, endS, forex = get_details()
    print("Got analysis...")
    
    #    cumWin = []
    #    cumLoss = []
    
    # Volatility scaling
    # Aiming for 12% annual volatility, which is 3.46% monthly
    #    targetSD = np.sqrt(12) / 100 # 0.0346 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    
    monthlyReturn = np.zeros(len(winners))
    
    standardDev, momSD = np.zeros(len(winners)), np.zeros(len(winners))
    dailyReturns, mom_return = [], []
    
    g_win, g_los, g_spy, g_val = np.zeros(len(winners)), np.zeros(len(winners)), np.zeros(len(winners)), np.zeros(len(winners))
    
    hedgeWeight, momWeight = np.zeros(len(winners)), np.zeros(len(winners))
    
    retWinScale, retLossScale = pd.Series(), pd.Series()
    
    
    for t in range(len(winners)):
        listWin, listLoss = winners[t], losers[t]
        retWin, retLoss = 0, 0
        
        for w, l in zip(listWin, listLoss):           
            r_w = getCSVRet(w, startH[t], endH[t])
            r_l = getCSVRet(l, startH[t], endH[t])
            
            pWin = getCSVPrice(w, startS[t], endS[t])
            pLoss = getCSVPrice(l, startS[t], endS[t])
            
            if w == listWin[0]: 
                retWinScale = 0 * pd.Series(pWin)
                retLossScale = 0 * pd.Series(pWin)
            
            retWin += r_w/num
            retLoss += r_l/num
            
            g_win[t] = sum(retWin)
            g_los[t] = sum(retLoss)
            
            retWinScale += getCSVRet(w, startS[t], endS[t]) 
            retLossScale += getCSVRet(l, startS[t], endS[t])
        
        scaleRet = (retWinScale - retLossScale)/num
        moRet = retWin - retLoss
        mom_return.append(moRet)
        
        totalVar = 0
        for j in range(len(scaleRet)):
            retj = float(scaleRet[j])
            totalVar += retj * retj
        
        monthlyVar = totalVar / 6 
        monthlySD = np.sqrt(monthlyVar)
        momSD[t] = monthlySD
        wMo = targetSD / monthlySD
        
        pSPY = getCSVPrice('SPY', startH[t], endH[t])
        retSPY = getCSVRet('SPY', startH[t], endH[t])
        g_spy[t] = sum(retSPY)
        
        pVal = getCSVPrice('VTV', startH[t], endH[t])
        retVal = getCSVRet('VTV', startH[t], endH[t])
        g_val[t] = sum(retVal)
        
        hedgeRet = retVal - retSPY
    
        momWeight[t] = wMo
        wMo *= .5
        # wHedge = .5
        wHedge = 1 - wMo
        hedgeWeight[t] = wHedge
        cash = .5-wMo
    
        fullPort = wMo * moRet + wHedge * hedgeRet
        dailyReturns.append(fullPort)
    
        exRet = forex['FX'][endH[t]]/forex['FX'][startH[t]]
        fullPort *= exRet
            
        monthRet = np.sum(fullPort)
        monthlyReturn[t] = monthRet
        standardDev[t] = np.std(fullPort)
    
    print("Average Annual Return: ", monthlyReturn.mean()*12)
    print("Average Annual Standard Deviation: ", standardDev.mean()*np.sqrt(252))
            
    
    #    for i in range(len(winners)):
    #        listWin = winners[i]
    #        listLoss = losers[i]
    #    
    #        retWin, retLoss = 0, 0
    #        for j in range(len(listWin)):
    #            r_w = getCSVRet(listWin[j], startH[i], endH[i])
    #            r_l = getCSVRet(listLoss[j], startH[i], endH[i])
    #    
    #            retWin = retWin + r_w/len(listWin)
    #            retLoss = retLoss + r_l/len(listLoss)
    #    
    #            g_win[i] = sum(retWin)
    #            g_los[i] = sum(retLoss)
    #    
    #        # Momentum strategy return
    #        moRet = retWin - retLoss
    #        mom_return.append(moRet)
    #        # Momentum scaling
    #        retWinScale = pd.Series()
    #        retLossScale = pd.Series()
    #    
    #        for j in range(len(listWin)): 
    #            pWin = getCSVPrice(listWin[j], startS[i], endS[i])
    #            pLoss = getCSVPrice(listLoss[j], startS[i], endS[i])
    #            
    #            if j == 0: 
    #                retWinScale = 0 * pd.Series(pWin)
    #                retLossScale = 0 * pd.Series(pWin)
    #                
    #            retWinScale = retWinScale + getCSVRet(listWin[j], startS[i], endS[i]) 
    #            retLossScale = retLossScale + getCSVRet(listLoss[j], startS[i], endS[i])
    #    
    #        scaleRet = (retWinScale - retLossScale) / len(listWin)
    #        
    #        totalVar = 0
    #        for j in range(len(scaleRet)):
    #            retj = float(scaleRet[j])
    #            totalVar += retj * retj
    #    
    #        monthlyVar = totalVar / 6 
    #        monthlySD = np.sqrt(monthlyVar)
    #        momSD[i] = monthlySD
    #        wMo = targetSD / monthlySD
    #    
    #        pSPY = getCSVPrice('SPY', startH[i], endH[i])
    #        retSPY = getCSVRet('SPY', startH[i], endH[i])
    #        g_spy[i] = sum(retSPY)
    #        
    #        pVal = getCSVPrice('VTV', startH[i], endH[i])
    #        retVal = getCSVRet('VTV', startH[i], endH[i])
    #        g_val[i] = sum(retVal)
    #        
    #        hedgeRet = retVal - retSPY
    #    
    #        momWeight[i] = wMo
    #        wMo *= .5
    #        # wHedge = .5
    #        wHedge = 1 - wMo
    #        hedgeWeight[i] = wHedge
    #        cash = .5-wMo
    #    
    #        fullPort = wMo * moRet + wHedge * hedgeRet
    #        dailyReturns.append(fullPort)
    #    
    #        exRet = forex['FX'][endH[i]]/forex['FX'][startH[i]]
    #        fullPort *= exRet
    #            
    #        monthRet = np.sum(fullPort)
    #        monthlyReturn[i] = monthRet
    #        standardDev[i] = np.std(fullPort)
    #        
    #    #################################################
    #    
    #    monthlyReturn.mean()*12
    #    standardDev.mean()*np.sqrt(252)
    
    ### METRICS ###
    #print(monthlyReturn)
    
    #    # PLOTTING - FIX X-AXIS LABELS
    #    fig, ax = plt.subplots()
    #    ax.plot(100 * monthlyReturn)
    #    ax.set_xlabel('Month')
    #    ax.set_ylabel('Percent')
    #    ax.set_title('Monthly Returns')
    #    plt.show()
    #
    #    fig2, ax2 = plt.subplots()
    #    ax2.plot(standardDev)
    #    ax2.set_xlabel('Month')
    #    ax2.set_ylabel('SD')
    #    ax2.set_title('Portfolio Standard Deviation')
    #    plt.show()
    #    
    #    RiskMetrics.plotCumRets(monthlyReturn)
    #    
    #    # METRICS
    #    RiskMetrics.riskMetricsNP(monthlyReturn, 'Whole Portfolio')
    #    #print(cash)
    
    
    
    # PRINTS CUMULATIVE RETURN BUT NOT COMPOUNDING
    #    RiskMetrics.cumRet(monthlyReturn)
    
    ### Get Weights ###
    '''
    Make one month iteration and return weights vector 
    Return price vector also 
    
    Tom include 2 columns for scaling period and rows 1 and 3 added, and first 4 column titles 
    Efficiency for storing data to make backtesting quicker
    '''
    
    def getWeights(i, targetSD = np.sqrt(12)/100):         
    
        listWin = winners[i]
        listLoss = losers[i]
    
        retWin = 0
        retLoss = 0
        prices = 10 * np.ones(len(tickers))
        
        for j in range(len(listWin)):
            p_w = getCSVPrice(listWin[j], startH[i], endH[i])
            p_l = getCSVPrice(listLoss[j], startH[i], endH[i])
            
            r_w = getCSVRet(listWin[j], startH[i], endH[i])
            r_l = getCSVRet(listLoss[j], startH[i], endH[i])
            
            retWin = retWin + r_w/len(listWin)
            retLoss = retLoss + r_l/len(listLoss)
            
            k_w = list(tickers).index(listWin[j])
            k_l = list(tickers).index(listLoss[j])
            
            prices[k_w] = p_w[len(p_w)-1]
            prices[k_l] = p_l[len(p_l)-1]
            # * (1+r[i-1])/(1+"retWinners in each list"[i-1])
    
        # Momentum scaling
        retWinScale = getCSVRet(listWin[0], startS[i], endS[i])
        retLossScale = getCSVRet(listLoss[0], startS[i], endS[i])
    
        scaleRet = retWinScale - retLossScale ########################### ? Only uses first ETF?
        
        totalVar = 0
        for j in range(len(scaleRet)):
            retj = float(scaleRet[j])
            totalVar += retj * retj
        
        print("Total Variance: ", totalVar)
        monthlyVar = totalVar / 6
        print("Monthly Variance: ", monthlyVar)
        monthlySD = np.sqrt(monthlyVar)
        wMo = targetSD / monthlySD
        print("Momentum Weight", wMo)
    
    
        pSPY = getCSVPrice('SPY', startH[i], endH[i])
        pSPY = pSPY[len(pSPY)-1]
        
        pVal = getCSVPrice('VTV', startH[i], endH[i])
        pVal = pVal[len(pVal)-1]
        
        wMo *= .5
        # wHedge = .5
        wHedge = 1 - wMo
        cash = .5-wMo
        
        # Weights vector 
        weights = np.zeros(len(tickers))
        for k in range(num): 
            j_w = list(tickers).index(listWin[k])
            j_l = list(tickers).index(listLoss[k])
            
            weights[j_w] = 0.0625 * wMo    # wMo has already been halved but we are multiplying my 0.0625 = 0.5/8 ?
            weights[j_l] = -0.0625 * wMo
            
        # Hedge weights 
        prices[len(prices)-2] = pVal
        prices[len(prices)-1] = pSPY
        weights[len(weights)-2] = wHedge / 2
        weights[len(weights)-1] = wHedge / 2
        
        return weights, prices
    
    ### Fees ###
        
    # Making the portfolio in the first month
    '''
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
    
    '''
    
    #Â Assumed all trades are either quote or order, can make a vector otherwise
    #Â Is the short classed as a sale, hence giving transaction costs?
    #Â Do we only buy and sell ETFs in whole numbers?
    #Â Requires positions as a vector of weights, prices and the stocks in the same order
    #    totalShares = 0
    def firstTime(positions, prices=1, quoteDriven=True, liquidity=10000, rebalance=False):
        #Â This may not like the short
        absPos = np.zeros(len(positions))
        for i in range(len(absPos)):
            absPos[i] = positions[i]
            if positions[i] < 0:
                absPos[i] = positions[i] * -1
            
        if rebalance == False: 
            if sum(absPos) != 0 and sum(absPos) != 1:
                sumPos = sum(absPos)
                for i in range(len(positions)):
                     positions[i] /= sumPos
                print('Reweighted: {}'.format(positions))
    
        if type(prices) == int and prices == 1:
            prices = 10 * np.ones(len(positions))
        else:
            print('Prices: {}'.format(prices))
    
        numShares = 0
        p = 1
        val = 0
        volume = np.zeros(len(positions))
        trans = np.zeros(len(positions))
        passThru = np.zeros(len(positions))
        clearing = np.zeros(len(positions))
        exchange = np.zeros(len(positions))
        totalShares = 0
    
        for i in range(len(positions)):
            w = absPos[i]
            p = prices[i]
            val = liquidity * w
            numShares = val / p
            totalShares += numShares
            volume[i] = 0.0035 * numShares
            if volume[i] < 0.35: 
                volume[i] = 0.35 
            if val / 100 < 0.35: 
                volume[i] = val / 100 
                
            if positions[i] < 0:
                trans[i] = 0.0000207 * val
            else:
                trans[i] = 0
            
            passThru[i] = 0.0000006125 * numShares # 0.0035 * 0.000175
            clearing[i] = 0.002 * numShares
            
            if absPos[i] > 0: # But its always non-negative so I guess just charging when position taken
                if quoteDriven:
                    exchange[i] = 0.003
                else:
                    exchange[i] = -0.002
        
        totalVolume = round(sum(volume), 10)
        totalTrans = round(sum(trans), 10)
        totalPass = round(sum(passThru), 10)
        totalClearing = round(sum(clearing), 10)
        totalExchange = round(sum(exchange), 10)
        fees = [totalVolume, totalTrans, totalPass, totalClearing, totalExchange]
        totalFee = round(sum(fees),10)
        print(fees)
        print('\nTotal fee: $ {}'.format(totalFee))
        print('Fee percentage: {} %\n'.format(totalFee/liquidity))
    
        return totalFee
    
    ### Rebalance ###
    
    # Rebalacing the portfolio
    # Needs to have the last month's positions
    def rebalance(lastPositions, positions, prices=1, quoteDriven=True, liquidity=10000):
        if type(prices) == int and prices == 1: 
            prices = 10 * np.ones(len(positions))
        
        changePositions = positions - lastPositions
        
        reFee = firstTime(changePositions, prices, rebalance=True)
        print(reFee)
        
        
        return reFee 
    
    #    lastMonth = firstTime(getWeights(len(winners)-2)[0], getWeights(len(winners)-2)[1]) ######### Doesn't work .... two variables passed into firstTime but only requires one...
    lastWeights = getWeights(len(winners)-2)[0]
    thisWeights = getWeights(len(winners)-1)[0]
    
    #print('Last month: ')
    #print(lastMonth)
    #print('\nThis weights: ')
    #print(thisWeights)
    #print('\nLast weights: ')
    #print(lastWeights)
    
    ### Exchange Rate ###
    
    i = len(winners)-1
    listWin = winners[i]
    num = len(listWin)
    listLoss = losers[i]
    
    #p = getCSVPrice(listWin[0], startH[i], endH[i])        ############## Unused?
    
    retWin, retLoss = 0, 0
    for j in range(num):
    #    p = getCSVPrice(listWin[j], startH[i], endH[i])    ############## Unused?
    #    p_l = getCSVPrice(listLoss[j], startH[i], endH[i])  ############## Unused?
    
        r_w = getCSVRet(listWin[j], startH[i], endH[i])
        r_l = getCSVRet(listLoss[j], startH[i], endH[i])
        
        retWin += r_w/len(listWin)                  ############## Repeated code?
        retLoss += r_l/len(listLoss)
    
        # * (1+r[i-1])/(1+"retWinners in each list"[i-1])
    
    # Momentum strategy return
    moRet = retWin - retLoss
    
    # Momentum scaling
    pWin = getCSVPrice(listWin[0], startS[i], endS[i])
    pLoss = getCSVPrice(listLoss[0], startS[i], endS[i])
    
    retWinScale = getCSVRet(listWin[0], startS[i], endS[i])
    retLossScale = getCSVRet(listLoss[0], startS[i], endS[i])
    
    scaleRet = retWinScale - retLossScale
     # Only Uses first ETF?
    totalVar = 0
    for j in range(len(scaleRet)):
        retj = float(scaleRet[j])
        totalVar += retj * retj
    monthlyVar = totalVar / 6
    monthlySD = np.sqrt(monthlyVar)
    wMo = targetSD / monthlySD
    
    pSPY = getCSVPrice('SPY', startH[i], endH[i])
    retSPY = getCSVRet('SPY', startH[i], endH[i])
    pVal = getCSVPrice('VTV', startH[i], endH[i])
    retVal = getCSVRet('VTV', startH[i], endH[i])
    
    hedgeRet = retVal - retSPY
    
    wMo *= .5
    # Alternatively wHedge = .5
    wHedge = 1 - wMo
    cash = .5-wMo # Da fuck
    
    fullPort = wMo * moRet + wHedge * hedgeRet
    #    forex = pd.read_csv("forex_GBP_USD.csv").set_index('Date')                 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    exRet = forex['FX'][endH[i]]/forex['FX'][startH[i]]
    monthRet = np.sum(fullPort)
    afterExRet = monthRet * exRet
    #print(afterExRet)
    
    #################################################
    
    #print(monthRet)
    # Before fees and exchange rate 
    
    feee = 0.00037558115138 # %
    #print(feee)
    # Exchange rate return 
    #print(exRet)
    # Portfolio return after exchange rate 
    # print(sum(fullPort))
    
    # Return after exchange rate and fees 
    print('True return: {}\n'.format((1 + monthRet - feee) * exRet - 1))
    # Can only do without fees for full period 
    # (1 + monthRet) * exRet - 1 
    
    # Comment the below after first run 
    listExRets = np.zeros(len(winners))
    for i in range(len(winners)): 
        exRet = forex['FX'][endH[i]]/forex['FX'][startH[i]]
        listExRets[i] = exRet
    
    listExRets = np.array(listExRets)
    #print(listExRets)
    
    print('Change weightings: ')
    changeWeights = thisWeights - lastWeights
    
    reFee=rebalance(lastWeights, thisWeights)#, prices) # Where does prices come from?
    print("Fee: ",reFee)
    # $ 3.76 to rebalance in the last month 
    
    print(sum(abs(changeWeights)))
    
    for i in range(len(winners)-2, len(winners)): 
    #    winners = dfList['Winners']
    #    losers = dfList['Losers']
    #    startH = dfList['StartH']
    #    endH = dfList['EndH']
    
        # Volatility scaling
        # Aiming for 12% annual volatility, which is 3.46% monthly
        targetSD = .0346
    
        listWin = winners[i]
        listLoss = losers[i]
    
        p = getCSVPrice(listWin[0], startH[i], endH[i]) # ?
        p_l = getCSVPrice(listLoss[0], startH[i], endH[i]) # ?
    
        retWin = 0
        retLoss = 0
        
        prices = np.ones(len(tickers))
        for j in range(len(listWin)): # Could be changed to j in listWin
            p_w = getCSVPrice(listWin[j], startH[i], endH[i])
            p_l = getCSVPrice(listLoss[j], startH[i], endH[i])
    
            r_w = getCSVRet(listWin[j], startH[i], endH[i])
            r_l = getCSVRet(listLoss[j], startH[i], endH[i])
    
            retWin +=  r_w/len(listWin)
            retLoss +=  r_l/len(listLoss)
    
            k_w = tickers.index(listWin[j])
            k_l = tickers.index(listLoss[j])
    
            prices[k_w] = p_w[len(p_w)-1]
            prices[k_l] = p_l[len(p_l)-1]
    
            # * (1+r[i-1])/(1+"retWinners in each list"[i-1])
    
        # Momentum scaling
        pWin = getCSVPrice(listWin[0], startS[i], endS[i])
        retWinScale = getCSVRet(listWin[0], startS[i], endS[i])
        pLoss = getCSVPrice(listLoss[0], startS[i], endS[i])
        retLossScale = getCSVRet(listLoss[0], startS[i], endS[i])
        scaleRet = retWinScale - retLossScale
        
        totalVar = 0
        for j in range(len(scaleRet)):
            retj = float(scaleRet[j])
            totalVar += retj * retj
            
        monthlyVar = totalVar / 6
        monthlySD = np.sqrt(monthlyVar)
        wMo = targetSD / monthlySD
    
        pSPY = getCSVPrice('SPY', startH[i], endH[i])
        pSPY = pSPY[len(pSPY)-1]
        pVal = getCSVPrice('VTV', startH[i], endH[i])
        pVal = pVal[len(pVal)-1]
    
        wMo *= .5
        # Alternatively wHedge = .5
        wHedge = 1 - wMo
        cash = .5-wMo
    
        # Weights vector 
        weights = np.zeros(len(tickers))
        for k in range(num): 
            j = tickers.index(listWin[k])
            weights[j] = 0.0625 * wMo
            l = tickers.index(listLoss[k])
            weights[l] = -0.0625 * wMo
    
        # Hedge weights 
        prices[len(prices)-2] = pVal
        prices[len(prices)-1] = pSPY
        weights[len(weights)-2] = 1/4
        weights[len(weights)-1] = -1/4
        
        if i == len(winners)-2: 
            lastWeights = weights 
        if i == len(winners)-1: 
            thisWeights = weights
            
    #print(lastWeights)
    #print(thisWeights)
    
    ### wMo ###
    
    # PLOTTING
    
    months = list(pd.read_csv("ETF_Analysis/months.csv")["StartF"])
    
    fig, ax = plt.subplots()
    ax.plot(months, 100 * monthlyReturn)
    ax.set_xlabel('Month')
    ax.set_ylabel('Percent')
    ax.set_title('Monthly Returns')
    plt.xticks(np.arange(0, len(months), step=15))
    plt.xticks(rotation=30)
    plt.show()
    
    fig2, ax2 = plt.subplots()
    ax2.plot(months, standardDev)
    ax2.set_xlabel('Month')
    ax2.set_ylabel('SD')
    ax2.set_title('Portfolio Standard Deviation')
    plt.xticks(np.arange(0, len(months), step=15))
    plt.xticks(rotation=30)
    plt.show()
    
    RiskMetrics.plotCumRets(monthlyReturn)
    
    # METRICS
    RiskMetrics.riskMetricsNP(monthlyReturn, 'Whole Portfolio')
    #print(cash)
    
    m = np.array(momWeight)
    l = momSD
    m = pd.DataFrame(m).shift(1)
    #print(m[1:])
    #    print('Mean wMo: ')
    fig3, ax3 = plt.subplots()
    ax3.scatter(l, m)
    ax3.set_xlabel("Momentum Volatility")
    ax3.set_ylabel("Momentum Momentum")
    
    # Monthly Sharpe ratio 
    #    print(monthlyReturn/standardDev)
    #    print('\nMean Sharpe ratio: {}'.format(np.mean(monthlyReturn/standardDev)))
    #    print('\nSD: {}'.format(np.std(monthlyReturn/standardDev)))
    
    #    print('Momentum monthly return: ')
    #    print(monthlyReturn)
    #    print('\nMomentum SD: ')
    #    print(l)
    #    
    #    print(momWeight)
    
    #    sharpe = (monthlyReturn.mean()*12)/(standardDev.mean()*np.sqrt(252))
    sharpe = (monthlyReturn.mean())/(standardDev.mean())
    print("Sharpe Ratio: ", sharpe)
    
    np.round(monthlyReturn, 10) 
    # Equivalent to np.round((g_win*momWeight*0.5)-(g_los*momWeight*0.5)+(g_val*hedgeWeight - g_gro*hedgeWeight), 10)
    
    dfList = pd.read_csv(folder+'/WML_Old.csv')
    
    frameWinLos = dfList; frameWinLos['Hedge'] = hedgeWeight
    frameWinLos = pd.DataFrame.set_index(frameWinLos, frameWinLos['EndH'])
    x = pd.DataFrame(momWeight, index=endH); x = x.rename(columns={0:"Momentum_Weights"})
    x['Winners_Returns'] = g_win; x['Losers_Returns'] = g_los 
    x['Hedge_Weight'] = frameWinLos['Hedge']
    x['VTV_Return'] = g_val; x['SPY_Return'] = g_spy 
    x['Winners'] = frameWinLos['Winners']; x['Losers'] = frameWinLos['Losers']
    x = pd.DataFrame.sort_index(x, ascending=True)
    #x['Risk_Metrics'] = 'Risk metrics for Whole Portfolio, Average return: 0.414307%, SD: 0.01645, SemiSD: 0.00956, Max DD: 7.71%, VaR at 5%: 2.314%, CVaR at 5%: 2.695%, Skewness: 0.04543, Kurtosis: -0.543714'
    #x['Risk_Metric'] = 'Risk metrics for Whole Portfolio, Average return: ' & round(monthlyReturn.mean()*100, 5) &'%, SD: ' & round(monthlyReturn.std()*100, 5) &', SemiSD: ' & 0.00956 & ', Max DD: ' & round(max_drawdown(monthlyReturn), 2) & '%, VaR at 5%: ' & round(-np.percentile(monthlyReturn, 5)*100, 2) &'%, CVaR at 5%: ' & round(-cVAR(monthlyReturn, 5)*100, 2) &'%, Skewness: ' & round(st.skew(monthlyReturn), 4) & ', Kurtosis: ' & round(st.kurtosis(monthlyReturn), 4)
    x['Risk_Metric'] = 'Risk metrics for Whole Portfolio, Average return: ' + str(round(monthlyReturn.mean()*100, 3)) + '%, SD: ' + str(round(monthlyReturn.std()*100, 3)) + '%, SemiSD: ' + str(round(RiskMetrics.semiv(monthlyReturn)*100, 2)) + '%, Max DD: ' + str(round(RiskMetrics.max_drawdown(monthlyReturn), 3)) + '%, VaR at 5%: ' + str(round(-np.percentile(monthlyReturn, 5)*100, 3)) + '%, CVaR at 5%: ' + str(round(-RiskMetrics.cVAR(monthlyReturn, 5)*100, 3)) + '%, Skewness: ' + str(round(st.skew(monthlyReturn), 3)) + ', Kurtosis: ' + str(round(st.kurtosis(monthlyReturn), 3))
    #x['Risk_Metrics'][1:] = ''
    x['Risk_Metric'][1:] = ''
    x.to_excel(folder+"/Momentum_with_VTV_SPY_Hedge.xlsx")
    y = pd.DataFrame(monthlyReturn, index=endH); y = y.rename(columns={0:"Strategy_Returns"})
    
        
    return mom_return
