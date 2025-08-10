from fastapi import APIRouter
from modules.crud_ops.contacts.schema import ContactProperties
import requests
from typing import Dict,Any
from modules.auth.token_manager import refresh_access_token,get_valid_access_token
from core.logger.logger import LOG

contacts_router = APIRouter()


@contacts_router.get("/allcontacts")
async def get_contacts():
    access_token = get_valid_access_token()
    if not access_token:
        return {"error": "No valid token available. Please authorize first at /"}

    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "properties": "email,firstname,lastname,phone,company",
        "archived": "false",
        "limit": 100
    }

    all_results = []

    res = requests.get(url, headers=headers, params=params)

    # Handle expired token
    if res.status_code == 401:
        LOG.info("Got 401, attempting token refresh...")
        access_token_data = refresh_access_token()
        if access_token_data:
            headers["Authorization"] = f"Bearer {access_token_data['access_token']}"
            res = requests.get(url, headers=headers, params=params)
        else:
            return {"error": "Failed to refresh token"}

    if res.status_code != 200:
        return {"error": res.status_code, "details": res.text}

    data = res.json()

    # Pagination loop
    while True:
        all_results.extend(data.get("results", []))
        try:
            url = data["paging"]["next"]["link"]  # Full URL from HubSpot
        except KeyError:
            break  # No more pages

        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            return {"error": res.status_code, "details": res.text}

        data = res.json()

    return {"results": all_results}
# async def get_contacts():
#     access_token = get_valid_access_token()
#     if not access_token:
#         return {"error": "No valid token available. Please authorize first at /"}

#     url = "https://api.hubapi.com/crm/v3/objects/contacts"
#     headers = {
#         "Authorization": f"Bearer {access_token}"
#     }
#     params = {
#         "properties": "email,firstname,lastname,phone,company"
#     }

#     res = requests.get(url, headers=headers, params=params)
    
#     # If token is invalid, try refreshing once more
#     if res.status_code == 401:
#         LOG.info("Got 401, attempting token refresh...")
#         access_token = refresh_access_token()
#         if access_token:
#             headers["Authorization"] = f"Bearer {access_token['access_token']}"
#             res = requests.get(url, headers=headers, params=params)
    
#     if res.status_code == 200:
#         return res.json()
#     else:
#         return {"error": res.status_code, "details": res.text}

@contacts_router.get("/create_contact")
async def create_contact(contact:ContactProperties) ->Dict[str,Any]:
    LOG.info("Into create func")
    access_token = get_valid_access_token()
    if not access_token:
        return {"error":"No valid access token"}
    
    url  = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    data = {"properties":contact.dict(exclude_unset=True)}
    res = requests.post(url,json=data,headers=headers)
    if res.status_code == 201:
        LOG.info(f"status code of creating contact {res.status_code}")
        return {"message":"contact_created","data":res.json()}
    LOG.info({"error":res.status_code,"details":res.text})
    return {"error":res.status_code,"details":res.text}