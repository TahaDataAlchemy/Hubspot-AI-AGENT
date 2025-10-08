import os
import time
import requests
from config import CONFIG
from core.utils.utils import jsonload,jsonDumpRefreshToken
from core.logger.logger import LOG
from modules.auth.constant import TOKEN_FILE



TOKEN_FILE = "token.json"

def refresh_access_token():
    if not os.path.exists(TOKEN_FILE):
        return None

    token_data = jsonload(TOKEN_FILE)
    refresh_token = token_data.get("refresh_token")
    if not refresh_token:
        return None

    token_url = "https://api.hubapi.com/oauth/v1/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "refresh_token",
        "client_id": CONFIG.hubspot_client_id,
        "client_secret": CONFIG.hubspot_client_secret,
        "refresh_token": refresh_token
    }

    res = requests.post(token_url, headers=headers, data=data)
    if res.status_code != 200:
        LOG.error(f"Token refresh failed: {res.text}")
        return None

    new_token_data = res.json()
    new_token_data["expires_at"] = time.time() + new_token_data["expires_in"]
    if "refresh_token" not in new_token_data:
        new_token_data["refresh_token"] = refresh_token

    jsonDumpRefreshToken(TOKEN_FILE, new_token_data)
    LOG.info("Token refreshed Succesfully")
    return new_token_data

def get_valid_access_token():
    LOG.info("Checking For Valid Token")
    if not os.path.exists(TOKEN_FILE):
        return None

    token_data = jsonload(TOKEN_FILE)
    if time.time() >= (token_data.get("expires_at", 0) - 300):
        token_data = refresh_access_token()

    return token_data.get("access_token") if token_data else None
