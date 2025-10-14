from modules.database.mongo_db.mongo_client import db
from modules.database.mongo_db.models import Message
from core.logger.logger import LOG

class MessageOperations:
    def __init__(self):
        self.collection = db["user_history"]
    
    def save_message(self,message_data:dict):
        try:
            message = Message(**message_data)
            result = self.collection.insert_one(message.dict())
            LOG.info(f"Message saved to MongoDB with _id: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            LOG.error(f"Error saving message to MongoDB: {e}")
    
    def get_user_messages(self,user_id: str, limit: int = 10):
        """Fetch recent messages for a user"""
        try:
            cursor = (
                self.collection.find({"user_id": user_id})
                .sort("created_at", -1)
                .limit(limit)
            )
            return list(cursor)
        except Exception as e:
            LOG.error(f"Error fetching messages: {e}")
            return []
    
    def get_message_by_id(self,message_id: str):
        """Fetch a specific message by ID"""
        try:
            return self.collection.find_one({"message_id": message_id})
        except Exception as e:
            LOG.error(f"Error fetching message {message_id}: {e}")
            return None
        
