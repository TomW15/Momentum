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

import sys
    
def momentum_strategy(folder="ETF_Analysis"):
    # For a portfolio's returns, gives the index
    def indx(ret):
        ind = ret * 0
        ind += 100
        for i in range(1, len(ret)):
            ind[i] = ind[i-1] * (1+ret[i])
        return ind
    
    # Cumulative returns
    
    def cumRet(rets):
        cumR = rets * 0 
        for t in range(1, len(cumR)):
            cumR[t] = cumR[t-1] + rets[t]
        return cumR
    
    def plotCumRet(cumR):
        fig = plt.figure()
        ax = fig.add_axes([1,1,1,1])
        ax.plot(cumR)
        ax.set_xlabel('Year')
        ax.set_ylabel('% Return')
        ax.set_title('Cumulative Return')
        plt.show()
    
    def plotCumRets(rets):
        c = cumRet(rets)
        plotCumRet(c)
    
    # Risk metric functions
    
    def maxDrawdown(pri, window=252):
        Roll_Max = pri.rolling(window, min_periods=200).max()
        Daily_Drawdown = pri/Roll_Max - 1.0
        Daily_Drawdown *= -1
        Max_Daily_Drawdown = np.max(Daily_Drawdown)
        print("Max daily drawdown: {}%".format(round(Max_Daily_Drawdown, 2)))
        return Max_Daily_Drawdown
    
    def plotDrawdown(pri, window=252):
        Roll_Max = pri.rolling(window, min_periods=200).max()
        Daily_Drawdown = pri/Roll_Max - 1.0
        Daily_Drawdown *= -1
        fig = plt.figure()
        ax = fig.add_axes([1,1,1,1])
        ax.plot(Daily_Drawdown)
        ax.set_xlabel('Year')
        ax.set_ylabel('%')
        ax.set_title('Drawdown')
        plt.show()
    
    def valueAR(dailyRet, per): #Historical
        pci = np.percentile(dailyRet, per)
        print("VaR at {0}%: {1}%".format(per, round(-100*pci, 3)))
        return pci
    
    def cVAR(dailyRet, per):
        pci = np.percentile(dailyRet, per)
        sumBad = 0
        t = 0
        for i in range(1, len(dailyRet)):
            if dailyRet[i] <= pci:
                t += 1
                sumBad += dailyRet[i]
        if t > 0:
            condVaR = sumBad / t
        else:
            condVaR = 0
        print("CVaR at {0}%: {1}%".format(per, round(-100*condVaR, 3)))
        return condVaR
    
    def semiv(dayRet):
        m = np.mean(dayRet)
        low = []
        for i in range(1, len(dayRet)):
            if dayRet[i] <= m:
                low.append(dayRet[i])
        stand = np.std(low)
        print("SemiSD: {}".format(round(stand, 6)))
        return stand
    
    # Use pricing data
    def max_drawdown(X):
        mdd = 0
        peak = X[0]
        for i in range(1, len(X)):
            if X[i] > peak:
                peak = X[i]
            dd = (peak - X[i]) / peak
            if dd > mdd:
                mdd = dd
        return mdd
    
    # SD, SemiV, Drawdown, VaR, CVaR, Skewness, Kurtosis
    def riskMetrics(ret, name = "portfolio", varP = 5, cvarP = 5):
        print("Risk metrics for {}".format(name))
        pri = indx(ret)
        print("Average return: {}%".format(round(100*np.mean(ret), 6)))
        sd = np.std(ret)
        print("SD: {}".format(round(sd, 6)))
        semiv(ret)
        dd = max_drawdown(pri)
        print("Max DD: {}%".format(round(100*dd, 2)))
        valueAR(ret, varP)
        cVAR(ret, cvarP)
        sk = st.skew(ret)
        print("Skewness: {}".format(round(sk, 6)))
        kurt = st.kurtosis(ret)
        print("Kurtosis: {}".format(round(kurt, 6)))
        print("")
        
    def cVARNP(dailyRet, per):
        pci = np.percentile(dailyRet, per)
        sumBad = 0
        t = 0
        for i in range(1, len(dailyRet)):
            if dailyRet[i] <= pci:
                t += 1
                sumBad += dailyRet[i]
        if t > 0:
            condVaR = sumBad / t
        else:
            condVaR = 0
        print("CVaR at {0}%: {1}%".format(per, np.round(float(-100*condVaR), 3)))
        return condVaR
    
    def riskMetricsNP(ret, name = "portfolio", varP = 5, cvarP = 5):
        print("Risk metrics for {}".format(name))
        pri = indx(ret)
        print("Average return: {}%".format(round(100*np.mean(ret), 6)))
        sd = np.std(ret)
        print("SD: {}".format(np.round(sd, 6)))
        semiv(ret)
        dd = max_drawdown(pri)
        print("Max DD: {}%".format(np.round(float(100*dd), 2)))
        valueAR(ret, varP)
        cVARNP(ret, cvarP)
        sk = st.skew(ret)
        print("Skewness: {}".format(np.round(float(sk), 6)))
        kurt = st.kurtosis(ret)
        print("Kurtosis: {}".format(np.round(float(kurt), 6)))
        print("")
        
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
    #########################################################################################################
    #########################################################################################################
    #########################################################################################################
    #########################################################################################################
    #########################################################################################################
    #########################################################################################################
    #########################################################################################################
    #########################################################################################################
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
    targetSD = np.sqrt(12) / 100 # 0.0346
    
    monthlyReturn = np.zeros(len(winners))
    standardDev = np.zeros(len(winners))
    numWin = 4
    dailyReturns = []
    momWeight = np.zeros(len(winners))
    momSD = np.zeros(len(winners))
    g_win = np.zeros(len(winners))
    g_los = np.zeros(len(winners))
    hedgeWeight = np.zeros(len(winners))
    g_spy = np.zeros(len(winners))
    g_val = np.zeros(len(winners))
    mom_return = []
    
    for i in range(len(winners)):
        listWin = winners[i]
        listLoss = losers[i]
    
        retWin, retLoss = 0, 0
        for j in range(len(listWin)):
            r_w = getCSVRet(listWin[j], startH[i], endH[i])
            r_l = getCSVRet(listLoss[j], startH[i], endH[i])
    
            retWin = retWin + r_w/len(listWin)
            retLoss = retLoss + r_l/len(listLoss)
    
            g_win[i] = sum(retWin)
            g_los[i] = sum(retLoss)
    
        # Momentum strategy return
        moRet = retWin - retLoss
        mom_return.append(moRet)
        # Momentum scaling
        retWinScale = pd.Series()
        retLossScale = pd.Series()
    
        for j in range(len(listWin)): 
            pWin = getCSVPrice(listWin[j], startS[i], endS[i])
            pLoss = getCSVPrice(listLoss[j], startS[i], endS[i])
            
            if j == 0: 
                retWinScale = 0 * pd.Series(pWin)
                retLossScale = 0 * pd.Series(pWin)
                
            retWinScale = retWinScale + getCSVRet(listWin[j], startS[i], endS[i]) 
            retLossScale = retLossScale + getCSVRet(listLoss[j], startS[i], endS[i])
    
        scaleRet = (retWinScale - retLossScale) / len(listWin)
        
        totalVar = 0
        for j in range(len(scaleRet)):
            retj = float(scaleRet[j])
            totalVar += retj * retj
    
        monthlyVar = totalVar / 6 
        monthlySD = np.sqrt(monthlyVar)
        momSD[i] = monthlySD
        wMo = targetSD / monthlySD
    
        pSPY = getCSVPrice('SPY', startH[i], endH[i])
        retSPY = getCSVRet('SPY', startH[i], endH[i])
        g_spy[i] = sum(retSPY)
        
        pVal = getCSVPrice('VTV', startH[i], endH[i])
        retVal = getCSVRet('VTV', startH[i], endH[i])
        g_val[i] = sum(retVal)
        
        hedgeRet = retVal - retSPY
    
        momWeight[i] = wMo
        wMo *= .5
        # wHedge = .5
        wHedge = 1 - wMo
        hedgeWeight[i] = wHedge
#        cash = .5-wMo # Pointless
    
        fullPort = wMo * moRet + wHedge * hedgeRet
        dailyReturns.append(fullPort)
    
        exRet = forex['FX'][endH[i]]/forex['FX'][startH[i]]
        fullPort *= exRet
            
        monthRet = np.sum(fullPort)
        monthlyReturn[i] = monthRet
        standardDev[i] = np.std(fullPort)
        
    #################################################
    
    monthlyReturn.mean()*12
    standardDev.mean()*np.sqrt(252)
    
    ### METRICS ###
    #print(monthlyReturn)
    
    fig, ax = plt.subplots()
    ax.plot(100 * monthlyReturn)
    ax.set_xlabel('Month')
    ax.set_ylabel('Percent')
    ax.set_title('Monthly Returns')
    plt.show()
    
    riskMetricsNP(monthlyReturn, 'Whole Portfolio')
    #print(cash)
    
    fig2, ax2 = plt.subplots()
    ax2.plot(standardDev)
    ax2.set_xlabel('Month')
    ax2.set_ylabel('SD')
    ax2.set_title('Portfolio Standard Deviation')
    plt.show()
    
    plotCumRets(monthlyReturn)
    
    cumRet(monthlyReturn)
    
    ### Get Weights ###
    
    '''
    Make one month iteration and return weights vector 
    Return price vector also 
    
    Tom include 2 columns for scaling period and rows 1 and 3 added, and first 4 column titles 
    Efficiency for storing data to make backtesting quicker
    '''
    
    def getWeights(i): 
        # Volatility scaling
        # Aiming for 12% annual volatility, which is 3.46% monthly
        targetSD = .0346
    
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
        
        monthlyVar = totalVar / 6
        monthlySD = np.sqrt(monthlyVar)
        wMo = targetSD / monthlySD
    
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
        for k in range(numWin): 
            j_w = list(tickers).index(listWin[k])
            j_l = list(tickers).index(listLoss[k])
            
            weights[j_w] = 0.0625 * wMo
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
    totalShares = 0
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
            print("Price for {} is {}".format(i,p))
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
            if absPos[i] > 0: 
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
        
        return reFee 
    
    lastMonth = firstTime(getWeights(len(winners)-2)[0], getWeights(len(winners)-2)[1]) ######### Doesn't work .... two variables passed into firstTime but only requires one...
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
    numWin = len(listWin)
    listLoss = losers[i]
    
    #p = getCSVPrice(listWin[0], startH[i], endH[i])        ############## Unused?
    
    retWin, retLoss = 0, 0
    for j in range(numWin):
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
    cash = .5-wMo
    
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
    
    rebalance(lastWeights, thisWeights)#, prices) # Where does prices come from?
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
        for k in range(numWin): 
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
    
    m = np.array(momWeight)
    l = momSD
    m = pd.DataFrame(m).shift(1)
    #print(m[1:])
    print('Mean wMo: ')
    print(np.mean(m))
    plt.scatter(l, m)
    
    # Monthly Sharpe ratio 
    print(monthlyReturn/standardDev)
    print('\nMean Sharpe ratio: {}'.format(np.mean(monthlyReturn/standardDev)))
    print('\nSD: {}'.format(np.std(monthlyReturn/standardDev)))
    
    print('Momentum monthly return: ')
    print(monthlyReturn)
    print('\nMomentum SD: ')
    print(l)
    
    print(momWeight)
    print(np.mean(momWeight))
    
    sharpe = (monthlyReturn.mean()*12)/(standardDev.mean()*np.sqrt(252))
    print(sharpe)
    
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
    x['Risk_Metric'] = 'Risk metrics for Whole Portfolio, Average return: ' + str(round(monthlyReturn.mean()*100, 3)) + '%, SD: ' + str(round(monthlyReturn.std()*100, 3)) + '%, SemiSD: ' + str(round(semiv(monthlyReturn)*100, 2)) + '%, Max DD: ' + str(round(max_drawdown(monthlyReturn), 3)) + '%, VaR at 5%: ' + str(round(-np.percentile(monthlyReturn, 5)*100, 3)) + '%, CVaR at 5%: ' + str(round(-cVAR(monthlyReturn, 5)*100, 3)) + '%, Skewness: ' + str(round(st.skew(monthlyReturn), 3)) + ', Kurtosis: ' + str(round(st.kurtosis(monthlyReturn), 3))
    #x['Risk_Metrics'][1:] = ''
    x['Risk_Metric'][1:] = ''
    x.to_excel(folder+"/Momentum_with_VTV_SPY_Hedge.xlsx")
    y = pd.DataFrame(monthlyReturn, index=endH); y = y.rename(columns={0:"Strategy_Returns"})
    
    
    return mom_return

momentum_strategy()