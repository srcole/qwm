# -*- coding: utf-8 -*-
"""
Automated rebooking for United

Created on Thu Aug 06 17:10:03 2015

@author: Scott
"""

'''
Algorithm:



Optional improvements:
1. Only look at certain airlines using the first code in the data as well
as the airlines database found here: 
https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat

2. 

'''
#%% Imports
import numpy as np

np.random.seed(0)

#%% Parameters

# Maximum number of layovers
nLay = 3

# Airport start and end
port1 = 'AMS'
port2 = 'SAN'

# Maximum number of results
nRes = 10

# Maximum length of time until arrival

#%% Import data
# Obtained from: http://openflights.org/data.html
# Timetable of data is in development by openflights.org but for now randomly assign times
arr = np.loadtxt('C:/gh/qwm/flights/routes.dat',delimiter=',')

#%%
f = open('C:/gh/qwm/flights/routes.dat')
lines = f.readlines()