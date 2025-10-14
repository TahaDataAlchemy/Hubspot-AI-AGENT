from pymongo import MongoClient
from core.logger.logger import LOG
from config import CONFIG

def get_mongo_db():
    try:
        client = MongoClient(CONFIG.mongo_uri,serverSelectionTimeoutMS=5000)
        client.server_info()
        LOG.info(f"Connected to MongoDB: {CONFIG.mongo_db}")
        return client[CONFIG.mongo_db]
    except Exception as e:
        LOG.error(f"MongoDB connection failed: {e}")
        raise e

db = get_mongo_db()

