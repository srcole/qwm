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

N = 25
P = 4
W = np.zeros([N,N,N,N,P])
for n1 in range(N):
    for n2 in range(N):
        for n3 in range(N):
            for n4 in range(N):
                W[n1,n2,n3,n4,0] = nWin(n1,[n2,n3,n4],N)
                W[n1,n2,n3,n4,1] = nWin(n2,[n1,n3,n4],N)
                W[n1,n2,n3,n4,2] = nWin(n3,[n1,n2,n4],N)
                W[n1,n2,n3,n4,3] = nWin(n4,[n1,n2,n3],N)

# Calculate the best choices for P2,3 for every possible choice by P1
p2bestN_1 = np.zeros(N)
p3bestN_1 = np.zeros([N,N])
p4bestN_1 = np.zeros([N,N])
p1bestW = np.zeros([N,N])
p2bestW = np.zeros([N,N])
p3bestW = np.zeros([N,N])
p4bestW = np.zeros([N,N])

p1_bestres = np.zeros(N)
for n1 in range(N):
    p2_bestres = np.zeros(N)
    for n2 in range(N):
        # Calculate the best possible P3W for every n1,n2 and n3 choice
        p3_bestres = np.zeros(N)
        for n3 in range(N):
            p4_bestres = np.argmax(np.squeeze(W[n1,n2,n3,:,3]))
            p3_bestres[n3] = W[n1,n2,n3,p4_bestres,2]
        
        # Choose best P2N, followed by P3N
        # Now know what p3 and p4 would choose for every p1 and p2
        p3bestN_1[n1,n2] = np.argmax(p3_bestres)
        p4bestN_1[n1,n2] = np.argmax(np.squeeze(W[n1,n2,p3bestN_1[n1,n2],:,3]))
        
        # Calculate the optimal n2
        p2_bestres[n2] = W[n1,n2,p3bestN_1[n1,n2],p4bestN_1[n1,n2],1]
    
    p2bestN_1[n1] = np.argmax(p2_bestres)
    p1_bestres[n1] = W[n1,p2bestN_1[n1],p3bestN_1[n1,p2bestN_1[n1]],p4bestN_1[n1,p2bestN_1[n1]],0]

# Calculate the best option for player 1 and results
p1bestN = np.argmax(p1_bestres)
p2bestN = p2bestN_1[p1bestN]
p3bestN = p3bestN_1[p1bestN,p2bestN]
p4bestN = p4bestN_1[p1bestN,p2bestN]
p1bestW = W[p1bestN,p2bestN,p3bestN,p4bestN,0]
p2bestW = W[p1bestN,p2bestN,p3bestN,p4bestN,1]
p3bestW = W[p1bestN,p2bestN,p3bestN,p4bestN,2]
p4bestW = W[p1bestN,p2bestN,p3bestN,p4bestN,3]

# Display optimal game
print 'P1 choice: ' , p1bestN , ' wins: ' , p1bestW
print 'P2 choice: ' , p2bestN , ' wins: ' , p2bestW
print 'P3 choice: ' , p3bestN , ' wins: ' , p3bestW
print 'P4 choice: ' , p4bestN , ' wins: ' , p4bestW