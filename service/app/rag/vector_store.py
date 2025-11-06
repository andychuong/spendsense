"""Vector store implementation using ChromaDB."""

import logging
import uuid
from typing import List, Dict, Any, Optional
import os

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning(
        "ChromaDB or sentence-transformers not installed. "
        "Install with: pip install chromadb sentence-transformers"
    )

from app.rag.config import RAGConfig, DEFAULT_CONFIG

logger = logging.getLogger(__name__)


class VectorStore:
    """Vector database for RAG system using ChromaDB.
    
    This class provides:
    - Document storage with embeddings
    - Semantic similarity search
    - Metadata filtering
    - Batch operations for efficiency
    
    Example:
        ```python
        vector_store = VectorStore()
        
        # Add documents
        vector_store.add_documents([
            {
                "id": "doc_1",
                "content": "User with high credit utilization...",
                "type": "user_scenario",
                "persona": "HIGH_UTILIZATION"
            }
        ])
        
        # Search
        results = vector_store.search(
            query="high credit card usage",
            top_k=5,
            filters={"type": "user_scenario"}
        )
        ```
    """
    
    def __init__(self, config: Optional[RAGConfig] = None):
        """
        Initialize vector store.
        
        Args:
            config: RAG configuration (defaults to DEFAULT_CONFIG)
        """
        if not CHROMADB_AVAILABLE:
            raise RuntimeError(
                "ChromaDB not available. Install with: "
                "pip install chromadb sentence-transformers"
            )
        
        self.config = config or DEFAULT_CONFIG
        
        # Initialize ChromaDB client
        logger.info(f"Initializing ChromaDB at {self.config.vector_db_path}")
        os.makedirs(self.config.vector_db_path, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=self.config.vector_db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.config.collection_name,
            metadata={
                "description": "SpendSense financial knowledge base for RAG",
                "embedding_model": self.config.embedding_model,
            }
        )
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {self.config.embedding_model}")
        self.encoder = SentenceTransformer(self.config.embedding_model)
        
        logger.info(
            f"✓ Vector store initialized: "
            f"{self.collection.count()} documents in collection '{self.config.collection_name}'"
        )
    
    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        batch_size: Optional[int] = None,
    ) -> int:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document dictionaries with 'id', 'content', and optional metadata
            batch_size: Batch size for embedding (defaults to config.batch_size)
        
        Returns:
            Number of documents added
        
        Example:
            ```python
            documents = [
                {
                    "id": "doc_1",
                    "content": "Financial education content...",
                    "type": "education",
                    "persona_ids": [1, 2],
                    "tags": ["credit", "debt"]
                },
                {
                    "id": "doc_2",
                    "content": "User scenario: High utilization...",
                    "type": "user_scenario",
                    "persona": "HIGH_UTILIZATION",
                    "feedback_rating": 5
                }
            ]
            count = vector_store.add_documents(documents)
            ```
        """
        if not documents:
            logger.warning("No documents to add")
            return 0
        
        batch_size = batch_size or self.config.batch_size
        
        # Validate documents
        for doc in documents:
            if "id" not in doc or "content" not in doc:
                raise ValueError("Each document must have 'id' and 'content' fields")
        
        # Extract content and metadata
        ids = [doc["id"] for doc in documents]
        contents = [doc["content"] for doc in documents]
        metadatas = [
            {k: v for k, v in doc.items() if k not in ["id", "content"]}
            for doc in documents
        ]
        
        # Generate embeddings in batches
        logger.info(f"Generating embeddings for {len(documents)} documents...")
        all_embeddings = []
        
        for i in range(0, len(contents), batch_size):
            batch_contents = contents[i:i + batch_size]
            batch_embeddings = self.encoder.encode(
                batch_contents,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
            all_embeddings.extend(batch_embeddings.tolist())
        
        # Add to collection
        logger.info(f"Adding {len(documents)} documents to collection...")
        self.collection.add(
            ids=ids,
            documents=contents,
            embeddings=all_embeddings,
            metadatas=metadatas,
        )
        
        logger.info(f"✓ Added {len(documents)} documents to vector store")
        return len(documents)
    
    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        include_distances: bool = True,
    ) -> Dict[str, Any]:
        """
        Search for similar documents.
        
        Args:
            query: Search query string
            top_k: Number of results to return (defaults to config.default_top_k)
            filters: Metadata filters (e.g., {"type": "user_scenario"})
            include_distances: Include similarity distances in results
        
        Returns:
            Dictionary with 'ids', 'documents', 'metadatas', and optionally 'distances'
        
        Example:
            ```python
            results = vector_store.search(
                query="high credit card utilization",
                top_k=5,
                filters={"type": "user_scenario", "persona": "HIGH_UTILIZATION"}
            )
            
            for doc_id, content, metadata in zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0]
            ):
                print(f"Found: {doc_id}")
                print(f"Content: {content[:100]}...")
                print(f"Metadata: {metadata}")
            ```
        """
        top_k = top_k or self.config.default_top_k
        
        # Generate query embedding
        query_embedding = self.encoder.encode([query], convert_to_numpy=True)[0]
        
        # Build where clause for filters
        where_clause = None
        if filters:
            # Convert filters to ChromaDB where clause format
            where_clause = self._build_where_clause(filters)
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=where_clause,
            include=["documents", "metadatas", "distances"] if include_distances else ["documents", "metadatas"],
        )
        
        logger.info(
            f"Search for '{query[:50]}...' returned {len(results['ids'][0])} results"
        )
        
        # Filter by similarity threshold if set
        if include_distances and self.config.similarity_threshold > 0:
            results = self._filter_by_threshold(results)
        
        return results
    
    def search_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID.
        
        Args:
            doc_id: Document ID
        
        Returns:
            Document dictionary or None if not found
        """
        try:
            result = self.collection.get(
                ids=[doc_id],
                include=["documents", "metadatas"]
            )
            
            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "content": result["documents"][0],
                    "metadata": result["metadatas"][0],
                }
        except Exception as e:
            logger.error(f"Error retrieving document {doc_id}: {e}")
        
        return None
    
    def delete_documents(self, doc_ids: List[str]) -> int:
        """
        Delete documents by IDs.
        
        Args:
            doc_ids: List of document IDs to delete
        
        Returns:
            Number of documents deleted
        """
        if not doc_ids:
            return 0
        
        self.collection.delete(ids=doc_ids)
        logger.info(f"✓ Deleted {len(doc_ids)} documents")
        return len(doc_ids)
    
    def update_document(self, doc_id: str, content: str, metadata: Dict[str, Any]) -> bool:
        """
        Update a document's content and metadata.
        
        Args:
            doc_id: Document ID
            content: New content
            metadata: New metadata
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate new embedding
            embedding = self.encoder.encode([content], convert_to_numpy=True)[0]
            
            # Update in collection
            self.collection.update(
                ids=[doc_id],
                documents=[content],
                embeddings=[embedding.tolist()],
                metadatas=[metadata],
            )
            
            logger.info(f"✓ Updated document {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating document {doc_id}: {e}")
            return False
    
    def count(self) -> int:
        """Get total number of documents in collection."""
        return self.collection.count()
    
    def clear(self) -> bool:
        """
        Clear all documents from the collection.
        
        Warning: This is destructive and cannot be undone!
        
        Returns:
            True if successful
        """
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(name=self.config.collection_name)
            self.collection = self.client.create_collection(
                name=self.config.collection_name,
                metadata={
                    "description": "SpendSense financial knowledge base for RAG",
                    "embedding_model": self.config.embedding_model,
                }
            )
            logger.info("✓ Cleared all documents from collection")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False
    
    def get_all_metadata(self, metadata_key: str) -> List[Any]:
        """
        Get all unique values for a metadata key.
        
        Args:
            metadata_key: Metadata key to retrieve (e.g., "type", "persona")
        
        Returns:
            List of unique values
        """
        # Get all documents (in batches if needed)
        all_docs = self.collection.get(
            include=["metadatas"],
            limit=self.collection.count()
        )
        
        # Extract unique values for the key
        values = set()
        for metadata in all_docs["metadatas"]:
            if metadata_key in metadata:
                value = metadata[metadata_key]
                if isinstance(value, list):
                    values.update(value)
                else:
                    values.add(value)
        
        return list(values)
    
    def _build_where_clause(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build ChromaDB where clause from filters.
        
        Args:
            filters: Dictionary of filters
        
        Returns:
            ChromaDB where clause
        """
        # Simple equality filters
        conditions = []
        
        for key, value in filters.items():
            if isinstance(value, dict):
                # Handle operators like {"$in": [1, 2, 3]}
                conditions.append({key: value})
            else:
                # Simple equality
                conditions.append({key: {"$eq": value}})
        
        # Combine with AND
        if len(conditions) == 1:
            return conditions[0]
        elif len(conditions) > 1:
            return {"$and": conditions}
        
        return {}
    
    def _filter_by_threshold(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter results by similarity threshold.
        
        Args:
            results: Search results from ChromaDB
        
        Returns:
            Filtered results
        """
        if "distances" not in results or not results["distances"]:
            return results
        
        # ChromaDB returns L2 distances (lower is better)
        # Convert to similarity scores (0-1, higher is better)
        # Similarity = 1 / (1 + distance)
        
        filtered_results = {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }
        
        for i, distance in enumerate(results["distances"][0]):
            similarity = 1 / (1 + distance)
            
            if similarity >= self.config.similarity_threshold:
                filtered_results["ids"][0].append(results["ids"][0][i])
                filtered_results["documents"][0].append(results["documents"][0][i])
                filtered_results["metadatas"][0].append(results["metadatas"][0][i])
                filtered_results["distances"][0].append(distance)
        
        logger.info(
            f"Filtered {len(results['ids'][0])} results to "
            f"{len(filtered_results['ids'][0])} by threshold {self.config.similarity_threshold}"
        )
        
        return filtered_results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with statistics
        """
        total_docs = self.count()
        
        # Get document types
        doc_types = self.get_all_metadata("type")
        
        # Get personas
        personas = self.get_all_metadata("persona")
        
        return {
            "total_documents": total_docs,
            "document_types": doc_types,
            "personas": personas,
            "collection_name": self.config.collection_name,
            "embedding_model": self.config.embedding_model,
            "embedding_dimension": self.encoder.get_sentence_embedding_dimension(),
        }

