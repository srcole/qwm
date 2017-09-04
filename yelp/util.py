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
    df_cities.to_csv('/gh/data2/yelp/city_pop.csv')
    return df_cities
