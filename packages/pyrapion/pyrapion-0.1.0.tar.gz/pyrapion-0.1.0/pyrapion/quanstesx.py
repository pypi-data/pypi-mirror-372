# Description: This file contains the QuantesX API client
"""docstring
"""
import requests


class QuantesApiClient():
    def __init__(self, api_key, env_url=None) -> None:
        self.env_url = env_url
        self.api_key = api_key
        self.headers = {
            "accept": "application/json",
            "X-Api-Key": api_key
        }
        if self.env_url and not self.env_url[-1] == "/":
            raise Exception(
                "The environment url must be ended with a forward slash"
            )
        if not self.env_url:
            raise Exception(
                "The env_url is missing, please provide the env_url"
            )

    def get_sensor_list(self, site_name):
        """
        """
        api_url = "/get_sensor_list"
        url = self.env_url + api_url
        params = {"site_name": site_name}
        r_ds = requests.get(
            url,
            headers=self.headers,
            params=params,
            verify=False
        )
        if r_ds.status_code == 200:
            return r_ds
        else:
            r_ds.raise_for_status()

    def get_site_list(self):
        """
        """
        api_url = "/get_site_list"
        url = self.env_url + api_url
        r_ds = requests.get(
            url,
            headers=self.headers,
            verify=False
        )
        if r_ds.status_code == 200:
            return r_ds
        else:
            r_ds.raise_for_status()

    def get_site_calculated_data(self, site_names, date_from, date_to):
        """
        """
        api_url = "/get_site_calculated_data"
        url = self.env_url + api_url
        params = {
            "site_names": site_names,
            "date_from": date_from,
            "date_to": date_to
        }
        r_ds = requests.get(
            url,
            headers=self.headers,
            params=params,
            verify=False
        )
        if r_ds.status_code == 200:
            return r_ds
        else:
            r_ds.raise_for_status()

    def get_site_calculated_data_daily(
        self,
        site_names,
        date_from,
        date_to
    ):
        api_url = "/get_site_calculated_data_daily"
        url = self.env_url + api_url
        params = {
            "site_names": site_names,
            "date_from": date_from,
            "date_to": date_to
        }
        r_ds = requests.get(
            url,
            headers=self.headers,
            params=params,
            verify=False
        )
        if r_ds.status_code == 200:
            return r_ds
        else:
            r_ds.raise_for_status()

    def get_site_raw_data(
        self,
        site_name,
        client_name,
        date_from=None,
        date_to=None,
        **kwargs
    ):
        """
        """
        api_url = "/get_site_raw_data"
        url = self.env_url + api_url
        params = {
            "site_name": site_name,
            "client_name": client_name
        }
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        if kwargs:
            params.update(kwargs)

        r_ds = requests.get(
            url,
            headers=self.headers,
            params=params,
            verify=False
        )
        if r_ds.status_code == 200:
            return r_ds
        else:
            r_ds.raise_for_status()
