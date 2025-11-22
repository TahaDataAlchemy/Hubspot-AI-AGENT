import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from config import CONFIG
from sentence_transformers import SentenceTransformer
from core.logger.logger import LOG

LOG.info("loading embedding model...")
embedding_model = SentenceTransformer(CONFIG.embeding_model)
model_dim = embedding_model.get_sentence_embedding_dimension()
LOG.info("Model loaded")

#connecting vector db
qdrant_cleint = QdrantClient(
    url=CONFIG.vector_db_url,
    api_key=CONFIG.vector_db_api,
    prefer_grpc=False
)

collection_name = CONFIG.vector_collection


def ensure_qdrant_collection_exists():
    """
    Ensure Qdrant collection exists with proper indexing for user_id
    """
    try:
        # Try to get the collection
        qdrant_cleint.get_collection(collection_name)
        LOG.info(f"Qdrant collection '{collection_name}' already exists.")
        
        # Ensure index exists (even if collection exists)
        try:
            qdrant_cleint.create_payload_index(
                collection_name=collection_name,
                field_name="user_id",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
            LOG.info("Created index for user_id field")
        except Exception as e:
            # Index might already exist, that's okay
            LOG.info(f"Index for user_id might already exist: {e}")
            
    except Exception:
        LOG.info(f"Qdrant collection '{collection_name}' not found. Creating it...")
        
        # Create the collection
        qdrant_cleint.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=model_dim,
                distance=models.Distance.COSINE
            ),
        )
        LOG.info(f"Qdrant collection '{collection_name}' created successfully.")
        
        # Create index for user_id field
        LOG.info("Creating index for user_id field")
        qdrant_cleint.create_payload_index(
            collection_name=collection_name,
            field_name="user_id",
            field_schema=models.PayloadSchemaType.KEYWORD
        )
        LOG.info("Index created for user_id field successfully")
