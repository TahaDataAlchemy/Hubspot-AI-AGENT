from core.logger.logger import LOG
from groq import Groq
from config import CONFIG
client = Groq()
# MODEL = CONFIG.model_name
MODEL = "llama-3.1-8b-instant"


def should_perform_vector_search(query: str, redis_messages: list) -> bool:
    """
    Use LLM to determine if vector search is needed based on query and Redis messages
    """
    if not redis_messages:
        LOG.info("No Redis messages, performing vector search")
        return True
    
    # Prepare the context for the LLM
    redis_context = ""
    if redis_messages:
        # Limit to the last 5 messages to avoid token limit issues
        recent_messages = redis_messages[-5:]
        redis_context = "\n".join([f"{msg.get('role', '')}: {msg.get('content', '')}" for msg in recent_messages])
    
    # Simplified, more direct prompt
    prompt = f"""Current conversation:
redis data: {redis_context}

User's new query: "{query}"

Is the information needed to answer this query already in the conversation above?
Answer with exactly one word: YES (information is present) or NO (need to search past history)

if information is empty and there is only user query and redis data is empty , return NO

Answer:"""
    
    try:
        # Make a call to the LLM
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers only with YES or NO."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,  # Zero temperature for deterministic output
            max_tokens=50  # Only need 1-2 tokens for YES/NO
        )
        
        # Log the full response object for debugging
        LOG.info(f"Full LLM response object: {response}")
        
        # Check if we got a response
        if not response.choices or len(response.choices) == 0:
            LOG.warning("No choices in LLM response, defaulting to YES")
            return True
        
        content = response.choices[0].message.content
        LOG.info(f"Raw LLM response content: '{content}'")
        
        if not content:
            LOG.warning("Empty content in LLM response, defaulting to YES")
            return True
            
        decision = content.strip().upper()
        LOG.info(f"LLM decision for vector search: '{decision}'")
        
        # More flexible matching
        if "YES" in decision:
            # YES means info IS present, so NO vector search needed
            return False
        elif "NO" in decision:
            # NO means info NOT present, so YES vector search needed
            return True
        else:
            LOG.warning(f"Unclear LLM response: '{decision}', defaulting to YES")
            return True
            
    except Exception as e:
        LOG.error(f"Error determining vector search need: {e}", exc_info=True)
        # Default to performing vector search if there's an error
        return True