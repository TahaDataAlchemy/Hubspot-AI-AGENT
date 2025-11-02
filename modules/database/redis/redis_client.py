import redis
from core.logger.logger import LOG
import json
import hashlib
from core.utils import jsonload
from config import CONFIG
from modules.ai_agent.system_Prompt import system_prompt
# redis_client = redis.Redis(host = "localhost",port = 6379,db=0,decode_responses = True)
from core.utils.utils import message_to_dict
redis_client = redis.Redis(
    host = CONFIG.redis_host,
    port = CONFIG.redis_port,
    decode_responses = True,
    username = CONFIG.redis_username,
    password = CONFIG.redis_pass
)

def get_user_namespace(token_file: str = "modules/auth/token.json") -> str:
    try:
        token_data = jsonload(token_file)
        refresh_token = token_data.get("refresh_token")

        if not refresh_token:
            raise ValueError("Refresh token missing in token.json")

        hashed_token = hashlib.sha256(refresh_token.encode()).hexdigest()
        return f"user:{hashed_token[:16]}" 

    except Exception as e:
        raise RuntimeError(f"Failed to generate user namespace: {e}")

def redis_set_json(key:str,value:dict,ex:int = 3600):
    redis_client.set(key,json.dumps(value),ex = ex)

def redis_get_json(key:str):
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None

def redis_delete_pattern(pattern:str):
    for key in redis_client.scan_iter(pattern):
        redis_client.delete(key)

def get_converstaion_key(user_id: str):
    return f"conversation:{user_id}:messages"

def get_messages_from_redis(user_id:str):
    key = get_converstaion_key(user_id)
    try:
        data = redis_client.get(key)
        if data:
            messages = json.loads(data)
            LOG.info(f"loaded {len(messages)} messages from Redis for user {user_id}")
            return messages
        else:
            messages = [{"role":"system","content":system_prompt}]
            save_messages_to_redis(user_id,messages)
            return messages
    except Exception as e:
        LOG.error(f"Error loading from redis:{e}")

def save_messages_to_redis(user_id:str,messages:list,ttl:int = 3600):
    key = get_converstaion_key(user_id)
    try:
        messages_dict = [message_to_dict(msg) for msg in messages]
        redis_client.set(key,json.dumps(messages_dict))
        redis_client.expire(key,ttl)
        LOG.info(f"saved {len(messages_dict)} messages to redis for user {user_id}")

    except Exception as e:
        LOG.error(f"Error saving to redis: {e}")