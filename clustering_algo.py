# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 16:17:34 2020

@author: tomw1
"""

import numpy as np

def cluster(startC, endC, log_ret, cluster_on, folder='ETF_Data'):
    
################################################################################
################################################################################

    def create_correlation_list(correlation):
        """
            Input: correlation - correlation matrix of wider universe of tickers we are interested in reducing
            Function: Purpose is to create a list of all correlations with each input including the 
            correlation value, and the ETFs this is between
        """
        # Finds the number of ETFs in correlation matrix
        n_comp = len(correlation.columns)
        # Gets list of ETFs from correlation matrix
        comp_names = list(correlation.columns)
        # Gets the untitled correlation matrix 
        correl_mat = correlation.values
        # Initializes an empty list to put all correlation edges
        L = [] 
        # Goes through all possible edges of correlation network
        for i in range(n_comp):
            for j in range(i+1,n_comp):
                L.append((correl_mat[i,j],comp_names[i],comp_names[j]))
        return L
    
################################################################################
################################################################################
    
    def find_bottom(start_node, next_nodes):
        """
            Inputs: start_node - a node we want to find the bottom of
                    next_nodes - a direction list of network of nodes which are connected
            Function: Purpose is to find the source node of a start_node in order to find if two nodes are in the same cluster
        """
        node = start_node
        while next_nodes[node] != node:
            node = next_nodes[node]
        return node
    
    def cluster_correlations(edges, tickers):
                
        def merge_sets(node1, node2, next_nodes, set_starters):
            """
                Inputs: node1, node2 - two ETFs in different clusters to merge clusters
                        next_nodes - a direction list of network of nodes which are connected
                        set_starters - set of bottom nodes
                Function: Purpose is to merge clusters when two ETFs are sufficiently highly correlated
            """
            bottom1 = find_bottom(node1, next_nodes)
            bottom2 = find_bottom(node2, next_nodes)
            next_nodes[bottom1] = bottom2
            if bottom2 in set_starters:
                set_starters.remove(bottom2)
            return next_nodes, set_starters
      
        ########################################################################
        ########################################################################         
        
        # Initialize list of absolute edges
        abs_edge=[]
        # Loop through all edges created
        for e in edges:
            abs_edge.append((abs(e[0]), e[1], e[2]))
        # Sort in decreasing order the abs_edge values (i.e. order absolute value of correlation)
        sorted_edges = sorted(abs_edge, reverse=True)
        # Initialize dictionary of next_nodes and set of set_starters which starts with each ETF pointing to itself and the set of bottom nodes is all the ETFs
        next_nodes = {node: node for node in tickers}
        set_starters = {node for node in tickers}
        i=0
        # Loop through all sorted edge values until below a specified cluster_on threshold defined by user
        while sorted_edges[i][0]>cluster_on:
            # Find the ETF names of the i-th value in the sorted_edge list
            comp1=sorted_edges[i][1]
            comp2=sorted_edges[i][2]
            # Get the bottom nodes for both ETFs above
            bottom1 = find_bottom(comp1, next_nodes)
            bottom2 = find_bottom(comp2, next_nodes)
            
            # If not already in the same cluster then merge the nodes
            if bottom1 != bottom2:
                next_nodes, set_starters = merge_sets(comp1, comp2, next_nodes, set_starters) 
            i+=1
        return set_starters, next_nodes
    
    def construct_sets(set_starters, next_nodes):
        """
            Inputs: set_starters - a node we want to find the bottom of
                    next_nodes - a direction list of network of nodes which are connected
            Function: Purpose is to create a dictionary of all clusters
        """
        # Initialize an empty dictionary called 'all_sets'
        all_sets = dict()
        # Loop through all bottom nodes
        for s in set_starters:
            # Initialize an empty set
            cur_set = set()
            # Add bottom node to set
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
    
    def captain_america(matrix):
        """
            Brings everyone together!
        """
        # Sums all elements of correlation matrix
        return np.sum(np.sum(np.abs(matrix)))

    def bruce_banner(nodes):
        """
            Does the calculcations!
        """
        # Function sets up calculations
        matrix = correlation[nodes].loc[nodes]
        value = captain_america(matrix)
        return value

    def stan_lee(all_clusters, target, optimal, value, changes, opt):
        """
            Keeps returning!
        """
        # Gets the cluster of the target node
        target_set = all_clusters[target]
        # Gets position of target in optimal set       
        position = list(optimal).index(target)+1
        # Sets new optimal to be a global variable
        global new_op
        # Sets the new optimal to be the current optimal and the new key to be the current target
        new_op = optimal
        new_key = target
        
        # Loop through the target set to find optimal ETF in set
        for i in target_set:
            # If current i is not in the optimal set, check if current i is a better choice
            if i not in new_op:
                # Replaces the target with i in the new_op set (Symmetric Differencing)
                compete = new_op^{target,i}
                # Performs calculation to find if i is a better choice
                comp_value = bruce_banner(compete)
                if comp_value < value:
                    # Replace current optimal with new found optimal and update optimal value and target
                    new_op = compete
                    value = comp_value
                    new_key = i
        # Check if the optimal is unchanged when looping through target set
        if new_key == target:
            pass
        else:
            changes += 1
            # Create new entry in all_clusters, letting the new_key be the key for the set and delete the original entry and target
            all_clusters[new_key] = all_clusters[target]
            del all_clusters[target]
        # Check if optimal found already
        if opt==False:
            # If not and on last element of set, set optimal to true and re-run function from start, else continue searching
            if position == len(optimal):
                opt=True
                stan_lee(all_clusters, list(new_op)[0], new_op, value, 0, opt)
            else:
                stan_lee(all_clusters, list(new_op)[position], new_op, value, changes, opt)
        else:
            # If so and no changes were made in previous loop then optimal has been found
            if position == len(optimal) and changes==0:
                print("Minimum found...")
                print(new_op)
            # If so and changes were made then repeat search
            elif position == len(optimal) and changes!=0:
                stan_lee(all_clusters, list(new_op)[0], new_op, value, 0, opt)
            # Continue searching for optimal
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

    # Get all ETFs outside hedge
    tickers = list(log_ret.columns)[:-2]
    
    print('Clustering data...')
    correlation = log_ret.loc[startC:endC, tickers].corr()
    edges = create_correlation_list(correlation)
    set_starters, next_nodes = cluster_correlations(edges, tickers)
    all_clusters = construct_sets(set_starters,next_nodes)
    print('Clustered data!')
    
    print('Perform Optimisation...')
    ironman(all_clusters, correlation)
      
    # Return the optimal found      
    return list(new_op)  
    
    
    