"""
util.py
Helper functions for interacting with the Yelp API.
"""

import numpy as np

import pandas as pd
import json
import pprint
import requests
import sys
import urllib
import glob
import os

from urllib.error import HTTPError
from urllib.parse import quote
from urllib.parse import urlencode

# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
TOKEN_PATH = '/oauth2/token'
GRANT_TYPE = 'client_credentials'

# OAuth credential placeholders that must be filled in by users.
# You can find them on
# https://www.yelp.com/developers/v3/manage_app
with open('/gh/data2/id/yelp_clientid.txt', 'r') as f:
    CLIENT_ID = f.read()
with open('/gh/data2/id/yelp_clientsecret.txt', 'r') as f:
    CLIENT_SECRET = f.read()


def obtain_bearer_token(host, path):
    """Given a bearer token, send a GET request to the API.

    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.

    Returns:
        str: OAuth bearer token, obtained using client_id and client_secret.

    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    assert CLIENT_ID, "Please supply your client_id."
    assert CLIENT_SECRET, "Please supply your client_secret."
    data = urlencode({
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': GRANT_TYPE,
    })
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
    }
    response = requests.request('POST', url, data=data, headers=headers)
    bearer_token = response.json()['access_token']
    return bearer_token


def request(host, path, bearer_token, url_params=None, verbose=True):
    """Given a bearer token, send a GET request to the API.

    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        bearer_token (str): OAuth bearer token, obtained using client_id and client_secret.
        url_params (dict): An optional set of query parameters in the request.

    Returns:
        dict: The JSON response from the request.

    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % bearer_token,
    }

    if verbose:
        print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()


def search(bearer_token, search_params, verbose=True):
    """Query the Search API by a search term and location.

    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.

    Returns:
        dict: The JSON response from the request.
    """
    url_params = {}
    for k in search_params.keys():
        val = search_params[k]
        if type(val) is str:
            url_params[k] = val.replace(' ', '+')
        else:
            url_params[k] = val

    return request(API_HOST, SEARCH_PATH, bearer_token, url_params=url_params, verbose=verbose)


def get_business(bearer_token, business_id):
    """Query the Business API by a business ID.

    Args:
        business_id (str): The ID of the business to query.

    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, bearer_token)


def query_api(search_params, verbose=False):
    """Queries the API by the input values from the user.

    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """

    bearer_token = obtain_bearer_token(API_HOST, TOKEN_PATH)

    response = search(bearer_token, search_params, verbose=verbose)

    total = response['total']
    latitude = response['region']['center']['latitude']
    longitude = response['region']['center']['longitude']
    businesses = response['businesses']

    if not businesses:
        print(u'No businesses for {0} in {1} found.'.format(search_params['term'], search_params['location']))
        return None, None, None, None

    return total, latitude, longitude, businesses


def process_city_population_data():
    """This processing only needs to be done once and resaved (to city_pop2.csv)"""
    # Load raw cities
    df_cities = pd.read_csv('/gh/data2/yelp/city_pop_old.csv')

    # Extract state
    df_cities['state'] = [c.split(',')[1][1:] for c in df_cities['GC_RANK.display-label.1']]

    # Extract just city
    city_temp = [c.split(',')[0][:] for c in df_cities['GC_RANK.display-label.1']]

    # Remove unnecessary words from city name
    remove_terms_post = ['city', 'town', 'village',
                         'metro', 'urban', 'CDP',
                         'municip', 'consolidate', 'unified']
    for k in remove_terms_post:
        city_temp = [c.split(' '+k)[0] for c in city_temp]

    remove_terms_pre = ['Urban']
    for k in remove_terms_pre:
        city_temp = [c.split(k+' ')[-1] for c in city_temp]

    # Replace any slashes with dashes
    N_cities = len(city_temp)
    for i in range(N_cities):
        if '/' in city_temp[i]:
            city_temp[i] = city_temp[i].replace('/', '-')
    df_cities['city'] = city_temp

    # Get just city, state, and pop
    df_cities.rename(columns={'respop72016': 'population'}, inplace=True)
    df_cities = df_cities[['city', 'state', 'population']]
    df_cities.to_csv('/gh/data2/yelp/city_pop_old2.csv')
    return df_cities


def process_scraped_data():
    """
    Transform data from original scraped format to 2 refined dataframes
    that contain data for all restaurants
    """
    # Load cities info
    df_cities = pd.read_csv('/gh/data2/yelp/city_pop.csv', index_col=0)

    # Determine paths to all dataframes
    dfs_places = []
    df_path_base = '/gh/data2/yelp/food_by_city/places/'
    for i, row in df_cities.iterrows():
        city = row['city']
        state = row['state']
        json_path = df_path_base + city + '_' + state + '.json'
        if os.path.isfile(json_path):
            df_temp = pd.read_json(json_path)
            df_temp['city'] = city
            df_temp['state'] = state
            dfs_places.append(df_temp)
        else:
            print('No data for', city, state)

    # Concatenate dataframes for each city
    df_places = pd.concat(dfs_places)
    df_places.reset_index(inplace=True)

    # Create custom columns
    df_places['all_aliases'] = [[a['alias'] for a in df_places['categories'][i]] for i in df_places.index]
    df_places['latitude'] = [df_places.loc[i]['coordinates']['latitude'] for i in df_places.index]
    df_places['longitude'] = [df_places.loc[i]['coordinates']['longitude'] for i in df_places.index]
    df_places['cost'] = [len(str(x)) for x in df_places['price'].values]
    df_places['has_delivery'] = ['delivery' in x for x in df_places['transactions'].values]
    df_places['has_pickup'] = ['pickup' in x for x in df_places['transactions'].values]

    # Determine which columns to keep
    cols_keep = ['id', 'name', 'city', 'state', 'rating', 'review_count', 'cost', 'all_aliases',
                 'latitude', 'longitude', 'has_delivery', 'has_pickup', 'url']
    df_places = df_places[cols_keep]

    # Determine all categories and their indices
    all_categories = np.unique(np.hstack(df_places['all_aliases'].values))
    k, v = np.unique(all_categories, return_inverse=True)
    idx_by_category = dict(zip(k, v))

    # Make a dataframe indicating if each restaurant is each category
    N_categories = len(all_categories)
    matrix_categories = np.zeros((len(df_places), N_categories), dtype=int)
    for i, row in df_places.iterrows():
        # Determine number of aliases
        N_aliases = len(row['all_aliases'])
        for j in range(N_aliases):
            # Mark alias as present
            alias_name = row['all_aliases'][j]
            matrix_categories[i, idx_by_category[alias_name]] = 1
    df_places_categories = pd.DataFrame(matrix_categories, columns=all_categories)

    # Save dataframes
    df_places.drop('all_aliases', axis=1).to_csv('/gh/data2/yelp/food_by_city/df_restaurants.csv')
    df_places_categories.to_csv('/gh/data2/yelp/food_by_city/df_categories.csv')
    return df_places, df_places_categories


def expand_df_cities():
    """
    Append to city dataframe some of the info scraped from yelp.
    """
    # Load cities info
    df_cities = pd.read_csv('/gh/data2/yelp/city_pop_old2.csv', index_col=0)
    df_restaurants = pd.read_csv('/gh/data2/yelp/food_by_city/df_restaurants.csv', index_col=0)

    # Total number of restaurants
    N_cities = len(df_cities)
    total_food = np.zeros(N_cities, dtype=int)
    for i, row in df_cities.iterrows():
        # Load numpy array of total places
        total_temp = np.load('/gh/data2/yelp/food_by_city/totals/' + row['city'] + '_' + row['state'] + '.npy')
        total_food[i] = int(np.median(total_temp))
    df_cities['total_food'] = total_food

    # Latitude
    lats = np.zeros(N_cities)
    for i, row in df_cities.iterrows():
        # Try to load text
        try:
            with open('/gh/data2/yelp/food_by_city/lats/' + row['city'] + '_' + row['state'] + '.txt', 'r') as f:
                lats[i] = float(f.read())
        except FileNotFoundError:
            lats_temp = np.load('/gh/data2/yelp/food_by_city/lats/' + row['city'] + '_' + row['state'] + '.npy')
            lats[i] = np.median(lats_temp)
    df_cities['latitude'] = lats

    # Longitude
    longs = np.zeros(N_cities)
    for i, row in df_cities.iterrows():
        # Try to load text
        try:
            with open('/gh/data2/yelp/food_by_city/longs/' + row['city'] + '_' + row['state'] + '.txt', 'r') as f:
                longs[i] = float(f.read())
        except FileNotFoundError:
            longs_temp = np.load('/gh/data2/yelp/food_by_city/longs/' + row['city'] + '_' + row['state'] + '.npy')
            longs[i] = np.median(longs_temp)
    df_cities['longitude'] = longs

    # Count number of restaurants scraped for each city
    total_scraped = np.zeros(N_cities, dtype=int)
    for i, row in df_cities.iterrows():
        # Load numpy array of total places
        total_scraped[i] = sum((df_restaurants['city'] == row['city']) & (df_restaurants['state'] == row['state']))
    df_cities['total_scraped'] = total_scraped

    df_cities.to_csv('/gh/data2/yelp/city_pop.csv')
