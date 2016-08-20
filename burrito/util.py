# -*- coding: utf-8 -*-
"""
This script contains functions for loading and analysis of burrito data
"""

import numpy as np
import scipy as sp
import pandas as pd

def load_burritos(filename='burrito_current.csv',
                  delete_unreliable = True):
    # Load all data
    df = pd.read_csv(filename)
    df.Location = df.Location.str.lower()
    
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

    return df