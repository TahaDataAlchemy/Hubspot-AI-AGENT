from modules.database.mongo_db.mongo_client import db
from modules.database.mongo_db.models import Message
from core.logger.logger import LOG
from typing import List, Dict, Optional
from bson import ObjectId

class MessageOperations:
    def __init__(self):
        self.collection = db["user_history"]
    
    def save_message(self, message_data: dict) -> str:
        try:
            message = Message(**message_data)
            result = self.collection.insert_one(message.dict())
            LOG.info(f"Message saved to MongoDB with _id: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            LOG.error(f"Error saving message to MongoDB: {e}")
            raise
    
    def get_user_messages(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Fetch recent messages for a user
        Returns: List of {user_query, ai_response} for context building
        """
        try:
            cursor = (
                self.collection.find(
                    {"user_id": user_id, "status": "completed"},
                    {"user_query": 1, "ai_response": 1, "created_at": 1, "_id": 0}
                )
                .sort("created_at", -1)
                .limit(limit)
            )
            messages = list(cursor)
            messages.reverse()  
            LOG.info(f"Fetched {len(messages)} messages for user: {user_id}")
            return messages
        except Exception as e:
            LOG.error(f"Error fetching messages: {e}")
            return []
    
    def get_message_by_id(self, message_id: str) -> Optional[Dict]:
        try:
            message = self.collection.find_one({"message_id": message_id})
            if message:
                LOG.info(f"Message fetched: {message_id}")
            return message
        except Exception as e:
            LOG.error(f"Error fetching message {message_id}: {e}")
            return None
    
    def get_all_user_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get full history for a user (with all details)"""
        try:
            cursor = (
                self.collection.find({"user_id": user_id})
                .sort("created_at", -1)
                .limit(limit)
            )
            messages = list(cursor)
            LOG.info(f"Fetched {len(messages)} full messages for user: {user_id}")
            return messages
        except Exception as e:
            LOG.error(f"Error fetching user history: {e}")
            return []
    
    def get_failed_messages(self, user_id: Optional[str] = None) -> List[Dict]:
        """Get messages that failed"""
        try:
            query = {"status": "error"}
            if user_id:
                query["user_id"] = user_id
            
            cursor = self.collection.find(query).sort("created_at", -1)
            messages = list(cursor)
            LOG.info(f"Fetched {len(messages)} failed messages")
            return messages
        except Exception as e:
            LOG.error(f"Error fetching failed messages: {e}")
            return []
    
    def count_user_messages(self, user_id: str) -> int:
        """Count total messages for a user"""
        try:
            count = self.collection.count_documents({"user_id": user_id})
            LOG.info(f"User {user_id} has {count} messages")
            return count
        except Exception as e:
            LOG.error(f"Error counting messages: {e}")
            return 0
    
    def delete_message(self, message_id: str) -> bool:
        """Delete a message by message_id"""
        try:
            result = self.collection.delete_one({"message_id": message_id})
            if result.deleted_count > 0:
                LOG.info(f"Message deleted: {message_id}")
                return True
            else:
                LOG.warning(f"Message not found: {message_id}")
                return False
        except Exception as e:
            LOG.error(f"Error deleting message: {e}")
            return False
    
    def get_messages_by_tool(self, tool_name: str, user_id: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get messages where a specific tool was called"""
        try:
            query = {"react_cycles.tool_calls.function_name": tool_name}
            if user_id:
                query["user_id"] = user_id
            
            cursor = self.collection.find(query).sort("created_at", -1).limit(limit)
            messages = list(cursor)
            LOG.info(f"Fetched {len(messages)} messages using tool: {tool_name}")
            return messages
        except Exception as e:
            LOG.error(f"Error fetching messages by tool: {e}")
            return []
    
    def get_high_token_messages(self, threshold: int = 5000, limit: int = 50) -> List[Dict]:
        """Get messages with high token usage"""
        try:
            cursor = (
                self.collection.find({"total_tokens": {"$gte": threshold}})
                .sort("total_tokens", -1)
                .limit(limit)
            )
            messages = list(cursor)
            LOG.info(f"Fetched {len(messages)} high-token messages")
            return messages
        except Exception as e:
            LOG.error(f"Error fetching high-token messages: {e}")
            return []