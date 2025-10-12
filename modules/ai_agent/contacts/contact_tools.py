import requests
from modules.crud_ops.contacts.schema import ContactProperties,UpdateContactArgs,Search_by_query
from modules.auth.token_manager import get_valid_access_token,refresh_access_token
from typing import Dict,Any
from core.logger.logger import LOG
import json
from modules.database.redis.redis_client import (
    redis_client, redis_get_json, redis_set_json, redis_delete_pattern, get_user_namespace
)

def get_contacts():
    access_token = get_valid_access_token()
    if not access_token:
        return {"error": "No valid token available. Please authorize first at /"}
    
    user_ns = get_user_namespace()
    cache_key = f"contact:{user_ns}:all"

    cached_data = redis_get_json(cache_key)
    if cached_data:
        LOG.info("Fetched contacts from redis cache")
        return {"results":cached_data}
    
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
    
    redis_set_json(cache_key, all_results)

    return {"results": all_results}

def create_contact(contact:ContactProperties) ->Dict[str,Any]:
    LOG.info("Into create func")
    access_token = get_valid_access_token()
    if not access_token:
        return {"error":"No valid access token"}
    
    user_ns = get_user_namespace()
    url  = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    data = {"properties":contact.dict(exclude_unset=True)}
    res = requests.post(url,json=data,headers=headers)
    if res.status_code == 201:
        LOG.info(f"status code of creating contact {res.status_code}")
        response_data = res.json()
        contact_id = response_data["id"]
        redis_set_json(f"contacts:{user_ns}:{contact_id}",response_data)
        redis_delete_pattern(f"contacts:{user_ns}:all")

        return {"message":"contact_created","data":response_data}
    LOG.info({"error":res.status_code,"details":res.text})
    return {"error":res.status_code,"details":res.text}

def update_contact(args: UpdateContactArgs):
    LOG.info("Into update contact func")

    LOG.info(f"UpdateContactArgs: {json.dumps(args.dict(), indent=2)}")
    access_token = get_valid_access_token()
    if not access_token:
        return {"error": "No Valid token. Please authenticate at root"}

    user_ns = get_user_namespace()
    
    url = f"https://api.hubapi.com/crm/v3/objects/contacts/{args.contact_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Remove unset fields so we only update what's given
    properties = args.dict(exclude_unset=True)
    properties.pop("contact_id", None)  # Remove id from update payload

    data = {"properties": properties}

    res = requests.patch(url, headers=headers, json=data)

    if res.status_code == 200:
        LOG.info({"message": "Contact updated", "data": res.json()})
        updated_data = res.json()
        redis_set_json(f"contacts:{user_ns}:{args.contact_id}",updated_data)
        redis_delete_pattern(f"contacts:{user_ns}:search:{args.email.lower()}")
        redis_delete_pattern(f"contacts:{user_ns}:all")
        return {"message": "Contact updated", "data": updated_data}

    LOG.info({"error": res.status_code, "details": res.text})
    return {"error": res.status_code, "details": res.text}


def delete_contact(contact_id:str):
    LOG.info("Into delete contact func")
    access_token = get_valid_access_token()
    if not access_token:
        return {"error":"No Valid token. Please authenticate at root"}
    user_ns = get_user_namespace()
    url  = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
    headers = {"Authorization":f"Bearer {access_token}","Content-Type":"application/json"}
    res = requests.delete(url,headers=headers) 
    if res.status_code == 204:
        redis_client.delete(f"contacts:{user_ns}:{contact_id}")
        redis_delete_pattern(f"contacts:{user_ns}:all")
        LOG.info("contact deleted and cache cleared")
        return {"message":"contact deleted"}
    return {"error": res.status_code, "details": res.text}



def search_by_identifier(query:Search_by_query):
    LOG.info(f"Searching for contant email {query}")

    access_token = get_valid_access_token()
    if not access_token:
        return {"error":"No valid token available. Please authorize first"}
    
    user_ns = get_user_namespace()
    cached_key = f"contacts:{user_ns}:search:{query.query.lower()}"
    cached = redis_get_json(cached_key)
    if cached:
        LOG.info("Search result fetched from redis cache")
        return {"message":"contact fetched (cached)","data":cached}
    
    url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
    headers = {"Authorization":f"Bearer {access_token}","Content-Type":"application/json"}

    payload = {
        "query": query.query,
        "properties": [
            "email",
            "firstname", 
            "lastname",
            "phone",
            "company",
            "website",
            "jobtitle"
        ]
    }

    res = requests.post(url,headers=headers,json=payload)
    if res.status_code ==200:
        LOG.info(f"Contact Fetched Successfully: {query.query}")
        redis_set_json(cached_key,res.json())
        return {"message":"contact fetched","data":res.json()}
    return {"error": res.status_code, "details": res.text}