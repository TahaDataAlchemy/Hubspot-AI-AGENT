import hashlib
import json
from core.utils import jsonload
from modules.auth.constant import TOKEN_FILE

def get_user_id_from_token(token_file:str = TOKEN_FILE) -> str:
    try:
        token_data = jsonload(token_file)
        refresh_token = token_data.get("refresh_token")

        if not refresh_token:
            raise ValueError("Missing refresh token in token.json")
        
        hashed_token = hashlib.sha256(refresh_token.encode()).hexdigest()
        return f"user_{hashed_token[:16]}"
    except Exception as e:
        raise RuntimeError(f"Failed to generate user_id: {e}")