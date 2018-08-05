"""
format_population_data.py
This script processes population data into a dataframe ready for analysis.
Data was acquired from the NIH at https://seer.cancer.gov/popdata/download.html
The "All States Combined (adjusted)" file was downloaded, and resaved with only
the 2015 data.
The meaning of the numbers in the plain text file is described here:
https://seer.cancer.gov/popdata/popdic.html
Script takes about 5 seconds to run.
"""

import numpy as np
import pandas as pd

# Load data 
filename = '/gh/data/classy/us.2015.singleages.adjusted.txt'
with open(filename, 'r') as f:
    data = f.readlines()
    
# For each line, determine the state
data_dict = {}
data_dict['state'] = [x[4:6] for x in data]

# For each line, determine the age
data_dict['age'] = [int(x[16:18]) for x in data]

# For each line, determine the gender
data_dict['gender'] = [int(x[15]) for x in data]

# For each line, determine the population
data_dict['population'] = [int(x[18:]) for x in data]

# Create dataframe of population by state, gender, and age
df = pd.DataFrame.from_dict(data_dict)
df = df.groupby(['state', 'gender', 'age']).sum()
df = df.reset_index()

# Remove population below age 18
df = df.loc[df['age']>=18]
df = df.reset_index(drop=True)

# Compute population fraction for each group
df['population_fraction'] = df['population'] / df['population'].sum()

# Compute cumulative population along the dataframe, which will help in simulating random populations
cumulative_fraction = [0]*len(df)
for i in range(len(df)):
    cumulative_fraction[i] = df['population_fraction'].loc[:i].sum()
df['cumulative_fraction'] = cumulative_fraction

# Change state to full name
from us_state_abbrev import us_state_abbrev
us_state_abbrev = dict(zip(us_state_abbrev.values(),us_state_abbrev.keys()))
states = [0]*len(df)
for i, row in df.iterrows():
    states[i] = us_state_abbrev[row['state']]
df['state'] = states

# Replace '1' with 'M' and '2' with 'F'
df['gender'] = ['M' if g == 1 else 'F' for g in df['gender'].values]

# Resave as csv
df.to_csv('./population_data.csv')