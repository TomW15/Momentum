# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 20:59:42 2020

@author: tomw1
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random

def plot_single_data(df):
    x_axis = df.columns[0]
    y_axis = df.columns[1]
    
    df = df.set_index(x_axis)
    
    r = random.random()
    b = random.random()
    g = random.random()
    color = (r, g, b)
    
    fig, ax1 = plt.subplots()
    ax1.plot(df[y_axis], c=color, label=y_axis)
    ax1.set_xlabel(x_axis)
    ax1.set_ylabel(y_axis)
    x=len(df)/10
    plt.xticks(np.arange(0, len(df), step=x))
    plt.xticks(rotation=30)
    ax1.legend()
    plt.show()
    
def plot_diff_axis(df1, df2, title=""):
    x_axis = df1.columns[0]
    
    if type(df1.index) == pd.core.indexes.range.RangeIndex:
        df1 = df1.set_index(x_axis)
    if type(df2.index) == pd.core.indexes.range.RangeIndex:
        df2 = df2.set_index(x_axis)
        
    y1_axis = df1.columns[0]    
    y2_axis = df2.columns[0]
    
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    
    for i in df1.columns:
        r = random.random()
        b = random.random()
        g = random.random()
        color = (r, g, b)
        ax1.plot(df1[i], c=color, label=i)
        title += (i + " and ")
        
    for j in df2.columns:  
        r = random.random()
        b = random.random()
        g = random.random()
        color = (r, g, b)
        ax2.plot(df2[j], c=color, label=j)
        title += j
        
    ax1.set_xlabel(x_axis)
    ax1.set_ylabel(y1_axis)
    ax2.set_ylabel(y2_axis)
    
    x = len(df1)/5
    
    plt.xticks(np.arange(0, len(df1), step=x))
    plt.xticks(rotation=30)
    plt.title(title)
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")
    plt.show()
    
def plot_same_axis(df, title=""):
    x_axis = df.columns[0]
    
    if type(df.index) == pd.core.indexes.range.RangeIndex:
        df = df.set_index(x_axis) 
    
    n = len(df.columns) - 1

    fig, ax1 = plt.subplots()
    
    for i, j in enumerate(df.columns):
        r = random.random()
        b = random.random()
        g = random.random()
        color = (r, g, b)
        ax1.plot(df[j], c=color, label=j)
        if i == n:
            title += (" and " + j)
        elif i == (n-1):
            title += (j)
        else: 
            title += (j + ", ")

    ax1.set_xlabel(x_axis)
    
    x = len(df)/5
    
    plt.xticks(np.arange(0, len(df), step=x))
    plt.xticks(rotation=30)
    plt.title(title)
    ax1.legend()
    plt.show()
    
def plot_scatter(df):
    x_axis = df.columns[0]
    df = df.set_index(x_axis)
  
    fig, ax1 = plt.subplots()
    
    ax1.scatter(df[df.columns[0]], df[df.columns[1]])
    
    ax1.set_xlabel(df.columns[0])
    ax1.set_ylabel(df.columns[1])
    
    plt.title(df.columns[0] + " vs " + df.columns[1])


   
    
    
