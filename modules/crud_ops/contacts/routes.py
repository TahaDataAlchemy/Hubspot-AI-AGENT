from fastapi import APIRouter #type: ignore
from modules.crud_ops.contacts.schema import ContactProperties,Search_by_query
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

@contacts_router.patch("/{contact_id}")
def update_contact(contact_id:str,contact:ContactProperties):
    access_token = get_valid_access_token()
    if not access_token:
        return {"error":"No Valid token. Please authenticate at root"}
    
    url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
    headers = {"Authorization":f"Bearer {access_token}","Content-Type": "application/json"}
    data = {"properties": contact.dict(exclude_unset=True)}
    res = requests.patch(url, headers=headers, json=data)
    
    if res.status_code == 200:
        return {"message": "Contact updated", "data": res.json()}
    return {"error": res.status_code, "details": res.text}

@contacts_router.post("/create_contact")
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

@contacts_router.delete("/{contact_id}")
def delete_contact(contact_id:str):
    LOG.info("Into delete contact func")
    access_token = get_valid_access_token()
    if not access_token:
        return {"error":"No Valid token. Please authenticate at root"}
    url  = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
    headers = {"Authorization":f"Bearer {access_token}","Content-Type":"application/json"}
    res = requests.delete(url,headers=headers) 
    if res.status_code == 204:
        return {"message":"contact deleted"}
    return {"error": res.status_code, "details": res.text}

@contacts_router.post("/search_by_email")
def search_by_identifier(query:Search_by_query):
    LOG.info(f"Searching for contant email {query}")

    access_token = get_valid_access_token()
    if not access_token:
        return {"error":"No valid token available. Please authorize first"}
    
    url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
    headers = {"Authorization":f"Bearer {access_token}","Content-Type":"application/json"}

    payload = {"query":query.query}

    res = requests.post(url,headers=headers,json=payload)
    if res.status_code ==200:
        LOG.info(f"Contact Fetched Successfully: {query.query}")
        return {"message":"contact fetched","data":res.json()}
    return {"error": res.status_code, "details": res.text}


