# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 16:17:34 2020

@author: tomw1
"""

import numpy as np
import pandas as pd
import pickle

def cluster(startC, endC, log_ret, cluster_on, folder='ETF_Data'):
    
################################################################################
################################################################################

    def create_correlation_list(correlation):
    
        n_comp = len(correlation.columns)
        comp_names = list(correlation.columns)
        correl_mat = correlation.values
        L = [] 
        for i in range(n_comp):
            for j in range(i+1,n_comp):
                L.append((correl_mat[i,j],comp_names[i],comp_names[j]))
        return L
    
################################################################################
################################################################################
    
    def find_bottom(start_node, next_nodes):
        node = start_node
        while next_nodes[node] != node:
            node = next_nodes[node]
        return node
    
    def cluster_correlations(edges, tickers):
        
        ########################################################################
        ########################################################################
        
        def merge_sets(node1, node2, next_nodes, set_starters):
            bottom1 = find_bottom(node1, next_nodes)
            bottom2 = find_bottom(node2, next_nodes)
            next_nodes[bottom1] = bottom2
            if bottom2 in set_starters:
                set_starters.remove(bottom2)
            return next_nodes, set_starters
      
        ########################################################################
        ########################################################################         
        
        abs_edge=[]
        for e in edges:
            abs_edge.append((abs(e[0]), e[1], e[2]))
        sorted_edges = sorted(abs_edge, reverse=True)
        next_nodes = {node: node for node in tickers}
        set_starters = {node for node in tickers}
        count=0
        
        while sorted_edges[count][0]>cluster_on:
    
            comp1=sorted_edges[count][1]
            comp2=sorted_edges[count][2]
                       
            bottom1 = find_bottom(comp1, next_nodes)
            bottom2 = find_bottom(comp2, next_nodes)
            
            if bottom1 != bottom2:
                next_nodes, set_starters = merge_sets(comp1, comp2, next_nodes, set_starters) 
            count+=1
        return set_starters, next_nodes
    
    def construct_sets(set_starters, next_nodes):
    
        all_sets = dict()
        
        for s in set_starters:
            cur_set = set()
            cur_set.add(s)
            p = s
            while next_nodes[p] != p:
                p = next_nodes[p]
                cur_set.add(p)  
            if p not in all_sets:
                all_sets[p] = cur_set
            else: 
                for item in cur_set:
                    all_sets[p].add(item)
        return all_sets
        
    ###########################################################################
    ###########################################################################
        
#    def find_least(all_clusters, next_nodes, tickers, correlation):
#        bottom=[]
#        for i in tickers:
#            if find_bottom(i, next_nodes)==i:
#                bottom.append(i)
#        
#    #    min_corr = dict()
#        most_data = dict()
#        comp = dict()
#        
#        #######################################################################
#        # Shortest Path Algorithm
#        
#        for i in bottom:
#            
#    #        min_corr[i] = len(tickers)
#            most_data[i] = len(tickers)
#            
#            for element in all_clusters[i]:
#                s = pd.read_csv(folder+'/{}.csv'.format(element))[element].shape[0]
##                    s = read_data(element).shape[0]
#                
#                if most_data[i] == len(tickers):
#                    most_data[i] = s
#                    comp[i] = element
#                elif s > most_data[i]:
#                    most_data[i] = s
#                    comp[i] = element
#                
#    #            c = correlation[element].abs().sum()
#    #            
#    #            if c < min_corr[i]:
#    #                comp[i]=element
#    #                min_corr[i]=c ### CAN BE IMPROVED
#    
#        #######################################################################
#                
#        
#        with open('universe_tickers.pickle', 'wb') as f:
#                pickle.dump(list(comp.values()),f)
#        
#        return list(comp.values())
    
    ###########################################################################
    ###########################################################################
    
    def captain_america(matrix):
        """
            Brings everyone together!
        """
        return np.sum(np.sum(np.abs(matrix)))

    def bruce_banner(nodes):
        """
            Does the calculcations!
        """
        matrix = correlation[nodes].loc[nodes]
        value = captain_america(matrix)
        return value

    def stan_lee(all_clusters, target, optimal, value, changes, opt):
        """
            Keeps returning!
        """
        target_set = all_clusters[target]
        
#        print("Target {}".format(target))
#        print("Target Set: {}".format(target_set))
        
        position = list(optimal).index(target)+1
        
        global new_op
        
        new_op = optimal
        new_key = target
        
        for i in target_set:
            if i not in new_op:
                compete = new_op^{target,i} # Symmetric Differencing
                comp_value = bruce_banner(compete)
                if value > comp_value:
#                    print("New optimal value: {} from set: {}".format(comp_value, compete))
                    new_op = compete
                    value = comp_value
                    new_key = i
#                else:
#                    print("Stick with {}".format(new_op))
    
        if new_key == target:
            pass
        else:
            changes += 1
            all_clusters[new_key] = all_clusters[target]
            del all_clusters[target]
        if opt==False:
            if position == len(optimal):
                opt=True
                stan_lee(all_clusters, list(new_op)[0], new_op, value, 0, opt)
            else:
                stan_lee(all_clusters, list(new_op)[position], new_op, value, changes, opt)
        else:
            if position == len(optimal) and changes==0:
                print("Minimum found...")
                print(new_op)
            elif position == len(optimal) and changes!=0:
                stan_lee(all_clusters, list(new_op)[0], new_op, value, 0, opt)
            else:
                stan_lee(all_clusters, list(new_op)[position], new_op, value, changes, opt)
        
    def ironman(all_clusters, correlation):
        """
            All starts with Ironman!  
            
            Steps:
                - Pick an arbitrary node in each cluster
                - Form the correlation matrix
                - Calculate value of said matrix
                - Recursion (Stan Lee):
                    - Goes through the clusters
                    - In a cluster, checks if a new optimal node can be chosen
                    - Repeat
        """
        arb_nodes = set(all_clusters.keys())
        value = bruce_banner(arb_nodes)
        stan_lee(all_clusters, list(arb_nodes)[0], arb_nodes, value, 0, opt=False)
    
    ###########################################################################
    ###########################################################################

    
    tickers = list(log_ret.columns)[:-2]
    
    print('Clustering data...')
    correlation = log_ret.loc[startC:endC, tickers].corr()
    edges = create_correlation_list(correlation)
    set_starters, next_nodes = cluster_correlations(edges, tickers)
    all_clusters = construct_sets(set_starters,next_nodes)
    print('Clustered data!')
    
    print('Perform Optimisation...')
    ironman(all_clusters, correlation)
    
    print('Getting universe...')
#    tickers = find_least(all_clusters, next_nodes, tickers, correlation)
    print('Got universe!')
        
    return list(new_op)  
    
    
    