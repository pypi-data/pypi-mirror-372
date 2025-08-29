import json
from io import BytesIO

import requests
import pandas as pd


class BaseAPI:

    def __init__(self, token, endpoint, verify=True, timeout: int = 120):
        self.token = token
        self.endpoint = endpoint
        self.verify = verify
        self.timeout = timeout

    def _call(self, url, params={}, json_payload={}, headers={}):
        api_url = self.endpoint + url
        params["api_key"] = self.token
        try:
            r = requests.get(api_url,
                             verify=self.verify,
                             headers=headers,
                             params=params,
                             data=json_payload,
                             timeout=self.timeout)
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request to {api_url} timed out.")

        if r.status_code >= 400:
            try:
                raise ResponseCodeException(json.loads(r.content))
            except json.decoder.JSONDecodeError:
                raise ResponseCodeException(str(r.content))
        return r

    def _call_json(self, *args, **kwargs):
        return self._call(*args, **kwargs).json()

    def _call_df(self, url, format="json", *args, **kwargs):
        r = self._call(url, *args, **kwargs)
        if format == "json":
            df = pd.read_json(BytesIO(r.content), orient='records', lines=True)
        else:
            df = pd.read_csv(BytesIO(r.content))
        return df

    @staticmethod
    def _build_params(**kwargs):
        params = {}
        for param in kwargs:
            if kwargs.get(param) is not None:
                params[str(param)] = kwargs.get(param)
        return params


class ResponseCodeException(Exception):
    """
    Exception raised when the API returns an unexpected response code
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
