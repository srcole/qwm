# -*- coding: utf-8 -*-
"""
This script contains functions for loading and analysis of burrito data
"""

import numpy as np
import scipy as sp
import pandas as pd

def load_burritos(filename='burrito_current.csv',
                  delete_unreliable = True, delete_nonSD = True, use_Google_Sheets=True):
    # Load all data
    if use_Google_Sheets:
        from StringIO import StringIO  # got moved to io in python3.
        import requests
        r = requests.get('https://docs.google.com/spreadsheet/ccc?key=18HkrklYz1bKpDLeL-kaMrGjAhUM6LeJMIACwEljCgaw&output=csv')
        df = pd.read_csv(StringIO(r.content))
    else:
        df = pd.read_csv(filename)
    df.Location = df.Location.str.lower()
    df.Location = df.Location.str.strip()
    df.Reviewer = df.Reviewer.str.strip()
    
    # Delete unreliable ratings
    if delete_unreliable:
        
        # Binarize unreliable
        df.Unreliable = df.Unreliable.map({'x':1,'X':1,1:1})
        df.Unreliable = df.Unreliable.fillna(0)
            
        # Select only reliable ratings from dataframe
        import pandasql
        q = """
        SELECT
        *
        FROM
        df
        WHERE
        unreliable == 0
        """
        df = pandasql.sqldf(q.lower(), locals())

    # Delete non SD ratings
    if delete_nonSD:

        # Binarize not San Diego
        df.NonSD = df.NonSD.map({'x':1,'X':1,1:1})
        df.NonSD = df.NonSD.fillna(0)
            
        # Select only reliable ratings from dataframe
        import pandasql
        q = """
        SELECT
        *
        FROM
        df
        WHERE
        NonSD == 0
        """
        df = pandasql.sqldf(q.lower(), locals())

    # Get restaurant info
    i_address = []
    for n in range(df.shape[0]):
        if df.loc[n].Neighborhood is not None:
            i_address.append(n)
    dfRestaurants = df.loc[i_address][['Location','Neighborhood','Address','URL','Yelp','Google','Chips']]

    # Binarize chips
    dfRestaurants.Chips = dfRestaurants.Chips.map({'x':True,'X':True,1:True})
    dfRestaurants.Chips = dfRestaurants.Chips.fillna(False)

    # Get ingredient info
    dfIngredients = df[df.keys()[np.where(df.keys()=='Beef')[0][0]:]]
    df = df[df.keys()[:np.where(df.keys()=='Beef')[0][0]]]
    df = df.drop(['Neighborhood','Address','URL','Yelp','Google','Chips','Unreliable','NonSD'],axis=1)

    return df, dfRestaurants, dfIngredients