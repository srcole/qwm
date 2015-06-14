# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 10:54:11 2015

@author: Scott

Assumptions: if tied for distance, no one wins
"""

import numpy as np
import matplotlib.pyplot as plt
import pdb

def nWin(n1,n_other,N):
    # return no winnings if any in n_other equals n1. this is an invalid scenario
    if n1 in n_other:
        return 0
        
    nowin = []
    for no in range(len(n_other)):
        # Mark numbers that are closer to n_other than n_1
        nowin = np.hstack((nowin,numCloser(n_other[no],n1,N)))
    nowin = np.unique(nowin)
    #pdb.set_trace()
    return N - len(nowin)

def numCloser(n1,n2,N):
    x1 = np.abs(np.arange(N) - n1)
    x2 = np.abs(np.arange(N) - n2)
    All = np.arange(N)
    return All[x1<=x2]

N = 30
P = 3
W = np.zeros([N,N,N,P])
for n1 in range(N):
    for n2 in range(N):
        for n3 in range(N):
            W[n1,n2,n3,0] = nWin(n1,[n2,n3],N)
            W[n1,n2,n3,1] = nWin(n2,[n1,n3],N)
            W[n1,n2,n3,2] = nWin(n3,[n1,n2],N)

# Calculate the best choices for P2,3 for every possible choice by P1
p2bestN_1 = np.zeros(N)
p3bestN_1 = np.zeros(N)
p1bestW_1 = np.zeros(N)
p2bestW_1 = np.zeros(N)
p3bestW_1 = np.zeros(N)
choice_N1 = np.zeros(N)
for n1 in range(N):
    # Calculate the best possible P2W for every n2
    p2_bestres_eachn = np.zeros(N)
    for n2 in range(N):
        c_bestp3 = np.argmax(np.squeeze(W[n1,n2,:,2]))
        p2_bestres_eachn[n2] = W[n1,n2,c_bestp3,1]
                
    # Choose best P2N, followed by P3N
    p2bestN_1[n1] = np.argmax(p2_bestres_eachn)
    p3bestN_1[n1] = np.argmax(np.squeeze(W[n1,p2bestN_1[n1],:,2]))
    
    # Calculate winnings for all players
    p1bestW_1[n1] = W[n1,p2bestN_1[n1],p3bestN_1[n1],0]
    p2bestW_1[n1] = W[n1,p2bestN_1[n1],p3bestN_1[n1],1]
    p3bestW_1[n1] = W[n1,p2bestN_1[n1],p3bestN_1[n1],2]
    
    # Check to see if choices
    temp_p3 = sum(np.squeeze(W[n1,p2bestW_1[n1],:,2]) == p3bestW_1[n1])
    if temp_p3 != 1:
        choice_N1[n1] = 1


# Calculate the best option for player 1 and results
p1bestN = np.argmax(p1bestW_1)
p2bestN = p2bestN_1[p1bestN]
p3bestN = p3bestN_1[p1bestN]
p1bestW = W[p1bestN,p2bestN,p3bestN,0]
p2bestW = W[p1bestN,p2bestN,p3bestN,1]
p3bestW = W[p1bestN,p2bestN,p3bestN,2]


# Display optimal game
print 'P1 choice: ' , p1bestN , ' wins: ' , p1bestW
print 'P2 choice: ' , p2bestN , ' wins: ' , p2bestW
print 'P3 choice: ' , p3bestN , ' wins: ' , p3bestW

# What is the optimal choice for each person
# Player 1 wants to choose the number that returns the max
# for him when player 2 chooses the max for him based on that number
# SHOULD BE ABLE TO EXTEND THIS STRATEGY
        
def play23(n1):
    # Based on a choice by player 1, what do players 2 and 3 do
    p2bestN = p2bestN_1[p1bestN]
    p3bestN = p3bestN_1[p1bestN]
    p1bestW = W[p1bestN,p2bestN,p3bestN,0]
    p2bestW = W[p1bestN,p2bestN,p3bestN,1]
    p3bestW = W[p1bestN,p2bestN,p3bestN,2]
    
    # Display optimal game
    print 'P1 choice: ' , p1bestN , ' wins: ' , p1bestW
    print 'P2 choice: ' , p2bestN , ' wins: ' , p2bestW
    print 'P3 choice: ' , p3bestN , ' wins: ' , p3bestW