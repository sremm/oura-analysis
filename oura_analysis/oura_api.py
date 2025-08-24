"""
OURA API docs https://cloud.ouraring.com/v2/docs#section/Overview

For adding new methods to access new data refer to the docs.
"""

import webbrowser
from urllib.parse import urlencode

import requests
from loguru import logger


class OuraApi:
    def __init__(
        self,
        client_id,
        client_secret,
        redirect_uri,
        scope: str = "daily heartrate personal sleep activity",
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = None
        self.refresh_token = None
        self.scope = scope

        self._token_url = "https://api.ouraring.com/oauth/token"

    def start_auth_flow(self):
        # Step 1: Direct user to authorization page
        auth_params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": self.scope,
        }
        auth_url = (
            f"https://cloud.ouraring.com/oauth/authorize?{urlencode(auth_params)}"
        )
        print(f"Please visit this URL to authorize: {auth_url}")
        webbrowser.open(auth_url)

        # Step 2: Exchange authorization code for access token
        # After user authorizes, they'll be redirected to your redirect URI with a code parameter
        auth_code = input("Enter the authorization code from the redirect URL: ")

        token_data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
        }
        response = requests.post(self._token_url, data=token_data)
        tokens = response.json()
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens["refresh_token"]

    def refresh_access_token(self):
        token_data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        response = requests.post(self._token_url, data=token_data)
        new_tokens = response.json()
        self.access_token = new_tokens["access_token"]
        self.refresh_token = new_tokens["refresh_token"]

    def get_sleep_data(self, start_date, end_date):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        sleep_data = requests.get(
            "https://api.ouraring.com/v2/usercollection/sleep",
            headers=headers,
            params={"start_date": start_date, "end_date": end_date},
        )
        return sleep_data.json()

    def get_sleep_score_data(self, start_date, end_date):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        sleep_score_data = requests.get(
            "https://api.ouraring.com/v2/usercollection/daily_sleep",
            headers=headers,
            params={"start_date": start_date, "end_date": end_date},
        )
        return sleep_score_data.json()

    def get_tags_data(self, start_date, end_date):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        tags_data = requests.get(
            "https://api.ouraring.com/v2/usercollection/enhanced_tag",
            headers=headers,
            params={"start_date": start_date, "end_date": end_date},
        )
        return tags_data.json()
