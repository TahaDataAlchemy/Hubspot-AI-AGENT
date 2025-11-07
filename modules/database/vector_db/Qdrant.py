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
    try:
        qdrant_cleint.get_collection(collection_name)
        LOG.info(f"Qdrant collection '{collection_name}' already exists.")
    except Exception:
        LOG.info(f"Qdrant collection '{collection_name}' not found. Creating it...")
        qdrant_cleint.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=model_dim,distance=models.Distance.COSINE),
        )
        LOG.info(f"Qdrant collection '{collection_name}' created successfully.")
        
