import requests
import pandas as pd
from urllib.parse import urlencode
from requests.exceptions import HTTPError, RequestException
import warnings

class RawQuery:
    def __init__(self, base_url, full_query, headers):
        self.base_url = base_url.rstrip('/')
        self.full_query = full_query.strip('/')
        self.headers = headers

    def fetch(self):
        full_url = f"{self.base_url}/{self.full_query}"
        response = requests.get(full_url, headers=self.headers)
        response.raise_for_status()
        return pd.DataFrame(response.json())

class Query:
    def __init__(self, base_url, endpoint, headers=None):
        self.base_url = base_url.rstrip('/')
        self.endpoint = endpoint.strip('/')
        self.headers = headers or {}
        self._params = {}
        self._filters = []
        self._orders = []

    def select(self, *columns):
        cols = [c for c in columns]
        existing = self._params.get('select','').split(',')
        combined = [c for c in existing + cols if c]
        self._params['select'] = ','.join(combined)
        return self

    def filters(self, *filter_strings):
        self._filters.extend(filter_strings)
        return self

    def order(self, *column, desc=False):
        direction = 'desc' if desc else 'asc'
        for col in column:
            for c in col.split(','):
                c = c.strip()
                if c:
                    self._orders.append(f"{c}.{direction}")
        return self

    def limit(self, n):
        self._params['limit'] = str(n)
        return self
    
    def compose_url(self):
        # Compose full URL
        full_url = f'{self.endpoint}'
        # Add ordering to params if exists
        if self._orders:
            self._params['order'] = ','.join(self._orders)

        query_str = urlencode(self._params, safe=',()')
        filter_str = '&'.join(self._filters)

        if query_str or filter_str:
            full_url += '?' + '&'.join(filter(None, [query_str, filter_str]))
        return full_url
    
    def fetch(self, diagnostic=False):
        full_url = f'{self.base_url}/{self.compose_url()}'
        print(full_url)
        try:
            response = requests.get(full_url, headers=self.headers)
            response.raise_for_status()
        
        except:
            #full (slow) diagnostic mode
            if diagnostic:
                try:
                    connection_test = requests.head(f'{self.base_url}/', headers=self.headers)
                    connection_test.raise_for_status()
                except:
                    raise ValueError(f"Connection to server failed, server returned {connection_test.status_code}. Check Clubcode, API/Access token and network connection") from None
                try:
                    check_endpoint = requests.get(f'{self.base_url}/{self.endpoint}?select=*&limit=1', headers=self.headers)
                    check_endpoint.raise_for_status()
                except:
                    raise ValueError(f"Data fetch failed, invalid base url or endpoint in table") from None
                if self._params.get('select'):
                    try:
                        check_selects = requests.get(f'{self.base_url}/{self.endpoint}?select={self._params['select']}&limit=1', headers=self.headers)
                        check_selects.raise_for_status()
                    except:
                        raise ValueError(f"Data fetch failed, invalid column names in select") from None
                if self._filters:
                    try:
                        check_filters = requests.get(f'{self.base_url}/{self.endpoint}?select=*&limit=1&{filter_str}', headers=self.headers)
                        check_filters.raise_for_status()
                    except:
                        raise ValueError(f"Data fetch failed, invalid filters") from None
                if self._orders:
                    try:
                        check_order = requests.get(f'{self.base_url}/{self.endpoint}?select=*&limit=5&order={self._params['order']}', headers=self.headers)
                        check_order.raise_for_status()
                    except:
                        raise ValueError(f"Data fetch failed, invalid order inputted") from None
                if self._params.get('limit'):
                    try:
                        check_limit = requests.get(f'{self.base_url}/{self.endpoint}?select=*&limit={self._params['limit']}', headers=self.headers)
                        check_limit.raise_for_status()
                    except:
                        raise ValueError(f"Data fetch failed, invalid limits applied") from None
            # fast diagnostic mode
            else:
                raise ValueError(f"Request failed for URL:\n{full_url}") from None
        return pd.DataFrame(response.json())



class cwapi:
    def __init__(self, api_token, clubcode=None, access_token=None, base_url='https://atukpostgrest.clubwise.com/'):
        self.base_url = base_url.rstrip('/')
        self.headers = {}
        self.clubcode = clubcode
        self.api_token = api_token
        self.access_token = access_token

        if not self.access_token:
            if not self.clubcode:
                raise ValueError("clubcode is required if access_token is not provided.")
            # Fetch the token
            self.get_access_token()
            
    def get_access_token(self):
        if not self.clubcode:
            raise ValueError("clubcode is required to generate access_token.")

        # Fetch the token
        request_url = f'{self.base_url}/access-token'
        request_header = {
            'CW-API-Token': self.api_token,
            'Content-Type': 'application/json'
        }
        payload = {'sClubCode': self.clubcode}
        response = requests.post(request_url, json=payload, headers=request_header, timeout=10)

        if response.status_code != 200:
            raise Exception("Failed to fetch access token.")

        self.access_token = response.json().get('access-token')
        if not self.access_token:
            raise Exception("Access token not found in response.")

        self.headers = {
            'CW-API-Token': self.api_token,
            'Authorization': f'Bearer {self.access_token}'
        }
        return self
        
    def table(self, endpoint):
        return Query(self.base_url, endpoint, self.headers)
    def raw_query(self, full_query):
        return RawQuery(self.base_url, full_query, self.headers)
    
