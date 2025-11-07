from modules.celery.tasks import embed_and_store_task
import os
import pymongo
from modules.database.mongo_db.mongo_client import db
from core.logger.logger import LOG
from bson import ObjectId

def watch_collection():
    """
    Watches a MongoDB collection for new documents and triggers a Celery task.
    """
    client = db.client
    collection=db["user_history"]

    pipeline = [{'$match':{'operationType':'insert'}}]
    LOG.info(f"Starting watcher on {collection}...")

    try:
        with collection.watch(pipeline) as stream:
            for change in stream:
                #when a new document is inserted
                full_document = change.get('fullDocument')
                if full_document:
                    if isinstance(full_document.get("_id"), ObjectId):
                        full_document["_id"] = str(full_document["_id"])
                    LOG.info(f"New document detected: {full_document['_id']}")
                    # Dispatch the task to the Celery queue
                    embed_and_store_task.delay(full_document)
    except pymongo.errors.PyMongoError as e:
        LOG.info(f"Error watching MongoDB collection: {e}")
    finally:
        client.close()



if __name__ == "__main__":
    watch_collection()