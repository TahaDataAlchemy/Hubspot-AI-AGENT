from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
import requests
import time
import os
from config import CONFIG
from modules.auth.constant import SCOPES,TOKEN_FILE
from core.utils.utils import jsonDump
from core.logger.logger import LOG

router = APIRouter(prefix="/auth",tags=["Auth"])

@router.get("/authorize_user")
def authorize_user():
    LOG.info("Authorizing User")
    params = {
        "client_id": CONFIG.hubspot_client_id,
        "redirect_uri": CONFIG.hubspot_redirect_uri,
        "scope": SCOPES,
        "response_type": "code"
    }
    url = f"https://app.hubspot.com/oauth/authorize?{urlencode(params)}"
    return RedirectResponse(url)

@router.get("/callback")
def hubspot_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return {"error": "Missing code in callback"}

    token_url = "https://api.hubapi.com/oauth/v1/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "authorization_code",
        "client_id": CONFIG.hubspot_client_id,
        "client_secret": CONFIG.hubspot_client_secret,
        "redirect_uri": CONFIG.hubspot_redirect_uri,
        "code": code
    }

    res = requests.post(token_url, headers=headers, data=data)
    if res.status_code != 200:
        LOG.info("User Cannot be Authorized")
        return {"error": res.json()}

    token_data = res.json()
    token_data["expires_at"] = time.time() + token_data["expires_in"]

    jsonDump(TOKEN_FILE, token_data)
    LOG.info("User Authorized")

    return {
        "message": "Authorized and token saved!",
        "access_token": token_data["access_token"]
    }
