import redis
from core.logger.logger import LOG
import json
import hashlib
from core.utils import jsonload
from config import CONFIG
# redis_client = redis.Redis(host = "localhost",port = 6379,db=0,decode_responses = True)

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
