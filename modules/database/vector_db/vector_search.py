from qdrant_client.http import models
from modules.database.vector_db.Qdrant import qdrant_cleint,embedding_model,collection_name
from core.logger.logger import LOG
from typing import List,Dict

class VectorSearchService:
    """
    Semantic Search
    """
    def __init__(self,top_k: int = 5):
        self.top_k = top_k
        self.collection_name = collection_name
    
    def search_conversations(
            self,
            query:str,
            user_id:str,
            limit:int = 20
    ) -> List[Dict]:
        """
        Search for relevent conversation using semantic search

        Args:
            query:User's search query
            user_id:current User's ID
            limit: Maximum number of result to return (default 5)

            Returns: 
                List of top matching conversation
        """
        try:
            LOG.info(f"Performing vector search for user: {user_id}, query: {query}")
            query_vector = embedding_model.encode(query).tolist()

            filter_conditions = models.Filter(
                must=[
                    models.FieldCondition(
                        key="user_id",
                        match=models.MatchValue(value=user_id)
                    )
                ]
            )
            search_result =  qdrant_cleint.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=filter_conditions,
                limit=limit,
                score_threshold=0.1
            )

            results=[]
            for hit in search_result:
                results.append(
                    {
                        "score":hit.score,
                        "mongo_id":hit.payload.get("mongo_id"),
                        "user_query":hit.payload.get("user_query"),
                        "ai_response":hit.payload.get("ai_response"),
                        "created_at":hit.payload.get("created_at"),
                        "status":hit.payload.get("status")
                    }
                )
            LOG.info(f"Found {len(results)} results from vector search")
            return results
        except Exception as e:
            LOG.error(f"Error in vector search: {e}")
            return []