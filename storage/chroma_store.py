import os
import logging
from typing import Optional, List, Dict, Any

LOG = logging.getLogger(__name__)
CHROMA_COLLECTION = os.environ.get("CHROMA_COLLECTION", "snacks")
CHROMA_SERVER = os.environ.get("CHROMA_SERVER", "")
CHROMA_API_KEY = os.environ.get("CHROMA_API_KEY", "")

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError as e:
    CHROMA_AVAILABLE = False
    LOG.warning(f"ChromaDB import failed: {e}. ChromaDB operations will be skipped.")
except Exception as e:
    CHROMA_AVAILABLE = False
    LOG.warning(f"Unexpected error importing ChromaDB: {e}. ChromaDB operations will be skipped.")

_client = None
_collection = None

def init_client() -> Optional[chromadb.Client]:
    global _client, _collection
    
    if not CHROMA_AVAILABLE:
        LOG.info("ChromaDB not available - skipping initialization.")
        return None
        
    if _client is not None:
        return _client
        
    try:
        if CHROMA_SERVER:
            settings = Settings(
                chroma_api_impl="rest", 
                chroma_server_host=CHROMA_SERVER,
                chroma_server_http_headers={"Authorization": f"Bearer {CHROMA_API_KEY}"} if CHROMA_API_KEY else None
            )
            _client = chromadb.Client(settings=settings)
        else:
            _client = chromadb.Client()
            
        # Initialize collection
        try:
            _collection = _client.get_collection(CHROMA_COLLECTION)
            LOG.info(f"Connected to existing ChromaDB collection: {CHROMA_COLLECTION}")
        except Exception:
            _collection = _client.create_collection(CHROMA_COLLECTION)
            LOG.info(f"Created new ChromaDB collection: {CHROMA_COLLECTION}")
            
        return _client
        
    except Exception as e:
        LOG.error(f"Failed to initialize ChromaDB client: {e}")
        _client = None
        _collection = None
        return None

def _validate_embedding(embedding: List[float]) -> bool:
    """
    Validate embedding format for ChromaDB.
    ChromaDB expects a list of floats.
    """
    if not isinstance(embedding, list):
        LOG.error(f"Embedding must be a list, got {type(embedding)}")
        return False
        
    if not embedding:
        LOG.error("Embedding list is empty")
        return False
        
    if not all(isinstance(x, (int, float)) for x in embedding):
        LOG.error("Embedding must contain only numbers (int/float)")
        return False
        
    return True

def upsert_item(uid: str, text: str, metadata: dict, embedding: Optional[List[float]] = None) -> bool:
    """
    Upsert an item into ChromaDB collection.
    
    Args:
        uid: Unique identifier for the item
        text: Document text
        metadata: Metadata dictionary
        embedding: Optional embedding vector (list of floats)
        
    Returns:
        bool: True if successful, False otherwise
    """
    client = init_client()
    if client is None or _collection is None:
        LOG.info("ChromaDB not available, skipping upsert.")
        return False
        
    try:
        if embedding is not None:
            if not _validate_embedding(embedding):
                LOG.error(f"Invalid embedding format for uid: {uid}")
                return False
            _collection.upsert(
                ids=[uid], 
                documents=[text], 
                metadatas=[metadata], 
                embeddings=[embedding]
            )
            LOG.debug(f"Upserted item with embedding: {uid}")
        else:
            _collection.upsert(
                ids=[uid], 
                documents=[text], 
                metadatas=[metadata]
            )
            LOG.debug(f"Upserted item without embedding: {uid}")
            
        return True
        
    except Exception as e:
        LOG.error(f"ChromaDB upsert failed for uid {uid}: {e}")
        return False

def query_similar(text: str, n: int = 5) -> List[Dict[str, Any]]:
    """
    Query ChromaDB for similar items.
    
    Args:
        text: Query text
        n: Number of results to return
        
    Returns:
        List of query results or empty list on failure
    """
    client = init_client()
    if client is None or _collection is None:
        LOG.info("ChromaDB not available, returning empty results.")
        return []
        
    try:
        results = _collection.query(query_texts=[text], n_results=n)
        LOG.debug(f"ChromaDB query returned {len(results.get('ids', [[]])[0])} results")
        return results
        
    except Exception as e:
        LOG.error(f"ChromaDB query failed: {e}")
        return []
