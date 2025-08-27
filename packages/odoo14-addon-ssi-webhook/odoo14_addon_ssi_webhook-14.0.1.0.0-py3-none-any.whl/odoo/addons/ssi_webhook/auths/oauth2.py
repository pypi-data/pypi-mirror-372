# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import requests
from oauthlib.oauth2 import BackendApplicationClient, LegacyApplicationClient
from requests_oauthlib import OAuth2Session


def _handle_response(resp, grant_type="oauth2"):
    try:
        resp_json = resp.json()
    except Exception:
        err_msg = f"{grant_type}: Invalid response: {resp.text}"
        raise Exception(err_msg)

    if resp.status_code != 200:
        err_desc = resp_json.get("error_description")
        err = resp_json.get("error")
        error_msg = err_desc or err or resp.text
        err_msg = f"{grant_type} failed: {error_msg}"
        raise Exception(err_msg)

    if "access_token" not in resp_json:
        err_msg = f"{grant_type} failed: No access_token in response"
        raise Exception(err_msg)

    return resp_json


def password(token_url, client_id, client_secret, username, password):
    client = LegacyApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)

    data = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    resp = requests.post(token_url, data=data)
    token = _handle_response(resp, "password")
    oauth.token = dict(token)
    return oauth


def client_credentials(token_url, client_id, client_secret):
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)

    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    resp = requests.post(token_url, data=data)
    token = _handle_response(resp, "client_credentials")
    oauth.token = dict(token)
    return oauth
