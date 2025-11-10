import multiprocessing
multiprocessing.set_start_method("spawn", force=True)

from core.logger.logger import LOG
from modules.database.vector_db.Qdrant import qdrant_cleint,ensure_qdrant_collection_exists,embedding_model,collection_name
import os
from modules.celery.celery_ini import celery_app
from qdrant_client.http import models
import uuid
LOG.info("Checking for Vector db collection")
ensure_qdrant_collection_exists()

@celery_app.task(bind=True,max_retries=3)
def embed_and_store_task(self,document:dict):
    """
    A celery task that embeds a mongo doc and save it into qdrant
    """
    try:
        # 1. PREPARE THE TEXT FOR EMBEDDING
        # We combine the most relevant fields to create a rich text representation.
        user_query=document.get("user_query","")
        ai_response=document.get("ai_response","")

        text_to_embed = f"User asked: {user_query}. AI responded: {ai_response}."

        # 2. GENERATE THE EMBEDDING VECTOR
        LOG.info(f"Embedding document _id: {document['_id']}")
        embeding_vector = embedding_model.encode(text_to_embed).tolist()
        # 3. PREPARE THE POINT FOR QDRANT
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(document["_id"]))) # Use MongoDB _id as the unique point ID in Qdrant
        # point_id = str(document["_id"]) 

        payload = {
            "mongo_id":str(document["_id"]),
            "user_id": document.get("user_id"),
            "user_query": user_query,
            "ai_response": ai_response,
            "status": document.get("status"),
            "created_at": document.get("created_at"),
        }
        # 4. UPSERT THE POINT INTO QDRANT
        qdrant_cleint.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=embeding_vector,
                    payload=payload
                )
            ]
        )
        LOG.info(f"Successfully stored point {point_id} in Qdrant.")
        return {"status": "success", "point_id": point_id}
    except Exception as e:
        LOG.info(f"Error processing document {document.get('_id')}: {e}")
        # If the task fails, it will be retried up to `max_retries` times
        raise self.retry(exc=e, countdown=60)


