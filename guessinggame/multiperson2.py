# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 10:54:11 2015

@author: Scott

Assumptions: if tied for distance, no one wins
"""

import numpy as np
import numpy.matlib
import matplotlib.pyplot as plt
from matplotlib import cm

N = 10

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

P = 2
W = np.zeros([N,N,2])
for n1 in range(N):
    for n2 in range(N):
        W[n1,n2,0] = nWin(n1,[n2],N)
        W[n1,n2,1] = nWin(n2,[n1],N)

# Choose the best number for player 1
# Search through all numbers and find the max for player 2
# When I choose that number
# Choose the one that minimizes his max, which is maximizing my max
p1_bestres_eachn = np.zeros(N)
for n in range(N):
    p1_bestres_eachn[n] = N - np.max(np.squeeze(W[n,:,1]))
p1_best = np.argmax(p1_bestres_eachn)

# Best choice for player 2
p2_best = np.argmax(np.squeeze(W[p1_best,:,1]))
p2_bestW = W[p1_best,p2_best,1]
p1_bestW = W[p1_best,p2_best,0]

# Display optimal game
print '# players: ' , P
print 'P1 choice: ' , p1_best , ' wins: ' , p1_bestW
print 'P2 choice: ' , p2_best , ' wins: ' , p2_bestW

# Visualize result in bar chart and color plot
def closest(nps,N):
    P = len(nps)
    closescore = np.zeros([P,N])
    for p in range(P):
        closescore[p,:] = np.abs(np.arange(N) - nps[p])
    
    closests = np.argmin(closescore,axis=0)
    for n in range(N):
        temp1 = np.min(closescore[:,n])
        if sum(closescore[:,n] == temp1) != 1:
            closests[n] = -1
    
    return closests
#%%
# Should add option to turn off vertical line
ns = np.arange(N)
closests = closest([p1_best,p2_best],N)
closests = np.matlib.repmat(closests,2,1)
y = np.arange(2)

plt.figure()
plt.pcolor(ns, y, closests)
plt.colors()
for n in range(N):
    plt.plot([n,n],[0,1],'k-')
plt.colorbar()    