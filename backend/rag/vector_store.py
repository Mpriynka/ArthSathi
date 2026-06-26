import os
import logging
import json
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from backend.config import settings

logger = logging.getLogger("chillar_seedhi.vector_store")

class LocalVectorStore:
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.collection_name = "financial_knowledge"
        self.use_qdrant = True
        self.fallback_db_path = os.path.join(storage_path, "fallback_kb.json")
        
        # Ensure directories exist
        os.makedirs(storage_path, exist_ok=True)
        
        try:
            # Initialize local file-based Qdrant client
            self.client = QdrantClient(path=self.storage_path)
            # Check if collection exists, if not create it
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Qdrant collection '{self.collection_name}' will be auto-created by fastembed.")
            else:
                logger.info(f"Qdrant collection '{self.collection_name}' already exists.")
        except Exception as e:
            logger.warning(f"Failed to initialize Qdrant local client: {e}. Falling back to Pure-Python Search.")
            self.use_qdrant = False
            self._init_fallback_db()

    def _init_fallback_db(self):
        if not os.path.exists(self.fallback_db_path):
            with open(self.fallback_db_path, "w", encoding="utf-8") as f:
                json.dump([], f)
            logger.info("Initialized fallback keyword DB")

    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[int] = None):
        """Adds documents to the store. Uses Qdrant fastembed or falls back to JSON file."""
        if not ids:
            ids = list(range(len(documents)))
            
        if self.use_qdrant:
            try:
                # Add using Qdrant's built-in fastembed support
                self.client.add(
                    collection_name=self.collection_name,
                    documents=documents,
                    metadata=metadatas,
                    ids=ids
                )
                logger.info(f"Successfully added {len(documents)} documents to Qdrant")
                return
            except Exception as e:
                logger.error(f"Qdrant add failed: {e}. Attempting fallback DB.")
                self.use_qdrant = False
                self._init_fallback_db()

        # Fallback method: Save locally in JSON
        try:
            with open(self.fallback_db_path, "r", encoding="utf-8") as f:
                db = json.load(f)
            
            for idx, doc, meta in zip(ids, documents, metadatas):
                # Clean up existing ID if present
                db = [item for item in db if item.get("id") != idx]
                db.append({
                    "id": idx,
                    "document": doc,
                    "metadata": meta
                })
                
            with open(self.fallback_db_path, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully added {len(documents)} documents to fallback DB")
        except Exception as fe:
            logger.error(f"Fallback DB write failed: {fe}")

    def query(self, text_query: str, limit: int = 3, level: Optional[int] = None, persona_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Queries the database, filtering by level and persona_type if supplied."""
        results = []

        if self.use_qdrant:
            try:
                # Build filter list
                filter_conditions = []
                if level is not None:
                    filter_conditions.append(
                        models.FieldCondition(
                            key="seedhiLevels",
                            match=models.MatchValue(value=level)
                        )
                    )
                if persona_type is not None:
                    filter_conditions.append(
                        models.FieldCondition(
                            key="persona",
                            match=models.MatchValue(value=persona_type)
                        )
                    )
                
                query_filter = models.Filter(must=filter_conditions) if filter_conditions else None
                
                # Perform search
                search_results = self.client.query(
                    collection_name=self.collection_name,
                    query_text=text_query,
                    query_filter=query_filter,
                    limit=limit
                )
                
                for res in search_results:
                    results.append({
                        "content": res.document,
                        "metadata": res.metadata,
                        "score": res.score
                    })
                return results
            except Exception as e:
                logger.error(f"Qdrant query failed: {e}. Switching to fallback DB.")
                self.use_qdrant = False
                self._init_fallback_db()

        # Fallback keyword/token search
        try:
            with open(self.fallback_db_path, "r", encoding="utf-8") as f:
                db = json.load(f)
                
            query_words = set(text_query.lower().split())
            
            scored_items = []
            for item in db:
                meta = item["metadata"]
                
                # Metadata filtering checks
                if level is not None:
                    levels = meta.get("seedhiLevels", [])
                    if level not in levels:
                        continue
                if persona_type is not None:
                    personas = meta.get("persona", [])
                    if isinstance(personas, str):
                        personas = [personas]
                    if persona_type not in personas:
                        continue
                
                # Calculate keyword overlap score
                doc_words = item["document"].lower().split()
                if not doc_words:
                    continue
                
                overlap = len(query_words.intersection(doc_words))
                jaccard = overlap / len(query_words.union(doc_words))
                
                # Boost if exact phrase in doc
                phrase_boost = 0.5 if text_query.lower() in item["document"].lower() else 0.0
                score = jaccard + phrase_boost
                
                scored_items.append((score, item))
                
            # Sort by score descending
            scored_items.sort(key=lambda x: x[0], reverse=True)
            
            for score, item in scored_items[:limit]:
                results.append({
                    "content": item["document"],
                    "metadata": item["metadata"],
                    "score": score
                })
            
        except Exception as fe:
            logger.error(f"Fallback DB query failed: {fe}")
            
        return results

# Global vector store instance
_vector_store_instance: Optional[LocalVectorStore] = None

def get_vector_store() -> LocalVectorStore:
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = LocalVectorStore(settings.QDRANT_PATH)
    return _vector_store_instance
