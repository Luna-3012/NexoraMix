import os
import logging
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

LOG = logging.getLogger(__name__)

# Try to import LlamaIndex components
try:
    from llama_index.core import VectorStoreIndex, Document, Settings
    from llama_index.vector_stores.chroma import ChromaVectorStore
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    import chromadb
    LLAMA_AVAILABLE = True
except ImportError as e:
    LOG.warning(f"LlamaIndex not available: {e}")
    LLAMA_AVAILABLE = False

class LlamaIndexService:
    def __init__(self):
        self.index = None
        self.query_engine = None
        self.initialized = False
        
        if LLAMA_AVAILABLE:
            self._initialize()
    
    def _initialize(self):
        """Initialize LlamaIndex with ChromaDB backend"""
        try:
            # Set up embedding model
            embed_model = HuggingFaceEmbedding(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            Settings.embed_model = embed_model
            
            # Initialize ChromaDB client
            chroma_client = chromadb.PersistentClient(path="./data/chroma")
            
            # Get or create collection
            try:
                collection = chroma_client.get_collection("brands")
                LOG.info("Connected to existing ChromaDB collection")
            except:
                collection = chroma_client.create_collection("brands")
                LOG.info("Created new ChromaDB collection")
            
            # Create vector store
            vector_store = ChromaVectorStore(chroma_collection=collection)
            
            # Create index
            self.index = VectorStoreIndex.from_vector_store(vector_store)
            self.query_engine = self.index.as_query_engine(similarity_top_k=5)
            
            self.initialized = True
            LOG.info("LlamaIndex service initialized successfully")
            
        except Exception as e:
            LOG.error(f"Failed to initialize LlamaIndex: {e}")
            self.initialized = False
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add brand documents to the index"""
        if not self.initialized:
            LOG.warning("LlamaIndex not initialized, skipping document addition")
            return
        
        try:
            docs = []
            for doc_data in documents:
                doc = Document(
                    text=f"{doc_data.get('brand', '')} - {doc_data.get('description', '')}",
                    metadata={
                        'brand': doc_data.get('brand', ''),
                        'category': doc_data.get('category', ''),
                        'product': doc_data.get('product', ''),
                        'tagline': doc_data.get('tagline', ''),
                        'source_url': doc_data.get('source_url', '')
                    }
                )
                docs.append(doc)
            
            # Add documents to index
            for doc in docs:
                self.index.insert(doc)
            
            LOG.info(f"Added {len(docs)} documents to LlamaIndex")
            
        except Exception as e:
            LOG.error(f"Failed to add documents to LlamaIndex: {e}")
    
    def query_brands(self, brand1: str, brand2: str) -> Dict[str, Any]:
        """Query for information about two brands"""
        if not self.initialized:
            LOG.warning("LlamaIndex not initialized, using fallback")
            return self._fallback_brand_info(brand1, brand2)
        
        try:
            # Query for both brands
            query1 = f"Tell me about {brand1} brand, products, and characteristics"
            query2 = f"Tell me about {brand2} brand, products, and characteristics"
            
            response1 = self.query_engine.query(query1)
            response2 = self.query_engine.query(query2)
            
            return {
                'brand1_info': str(response1),
                'brand2_info': str(response2),
                'brand1_sources': [node.metadata for node in response1.source_nodes] if hasattr(response1, 'source_nodes') else [],
                'brand2_sources': [node.metadata for node in response2.source_nodes] if hasattr(response2, 'source_nodes') else []
            }
            
        except Exception as e:
            LOG.error(f"Failed to query brands: {e}")
            return self._fallback_brand_info(brand1, brand2)
    
    def _fallback_brand_info(self, brand1: str, brand2: str) -> Dict[str, Any]:
        """Fallback method when LlamaIndex is not available"""
        # Try to load from processed data
        try:
            processed_dir = Path("data/processed")
            brand_data = {}
            
            if processed_dir.exists():
                kb_file = processed_dir / "brands_knowledge_base.json"
                if kb_file.exists():
                    with open(kb_file, 'r', encoding='utf-8') as f:
                        all_brands = json.load(f)
                    
                    for brand_info in all_brands:
                        brand_name = brand_info.get('brand', '').lower()
                        if brand1.lower() in brand_name or brand_name in brand1.lower():
                            brand_data['brand1_info'] = brand_info.get('description', f"Information about {brand1}")
                        if brand2.lower() in brand_name or brand_name in brand2.lower():
                            brand_data['brand2_info'] = brand_info.get('description', f"Information about {brand2}")
            
            return {
                'brand1_info': brand_data.get('brand1_info', f"Popular brand {brand1} with strong market presence"),
                'brand2_info': brand_data.get('brand2_info', f"Well-known brand {brand2} with distinctive characteristics"),
                'brand1_sources': [],
                'brand2_sources': []
            }
            
        except Exception as e:
            LOG.error(f"Fallback brand info failed: {e}")
            return {
                'brand1_info': f"Popular brand {brand1} with strong market presence",
                'brand2_info': f"Well-known brand {brand2} with distinctive characteristics", 
                'brand1_sources': [],
                'brand2_sources': []
            }

# Global service instance
llama_service = LlamaIndexService()