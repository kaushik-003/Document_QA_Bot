import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
from app.config import settings as app_settings
import os

class VectorStore:
    """Manage ChromaDB vector store"""
    
    def __init__(self):
        """Initialize ChromaDB client"""
        # Create persist directory if it doesn't exist
        os.makedirs(app_settings.CHROMA_PERSIST_DIR, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=app_settings.CHROMA_PERSIST_DIR
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="document_chunks",
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        
        print(f"ChromaDB initialized with {self.collection.count()} existing chunks")
    
    def add_chunks(self, chunks: List[Dict[str, Any]], document_id: str, embeddings: List[List[float]]):
        """Add chunks with embeddings to the vector store"""
        ids = [f"{document_id}_chunk_{chunk['chunk_index']}" for chunk in chunks]
        documents = [chunk['content'] for chunk in chunks]
        metadatas = [
            {
                "document_id": document_id,
                "chunk_index": chunk['chunk_index'],
                "char_count": chunk['char_count']
            }
            for chunk in chunks
        ]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        print(f"Added {len(chunks)} chunks to vector store for document {document_id}")
    
    def search(self, query_embedding: List[float], top_k: int = 5, document_ids: List[str] = None) -> Dict[str, Any]:
        """Search for similar chunks"""
        where_filter = None
        if document_ids:
            where_filter = {"document_id": {"$in": document_ids}}
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter
        )
        
        return results
    
    def delete_by_document_id(self, document_id: str):
        """Delete all chunks for a specific document"""
        # Get all chunk IDs for this document
        results = self.collection.get(
            where={"document_id": document_id}
        )
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
            print(f"Deleted {len(results['ids'])} chunks for document {document_id}")
        
    def clear_all(self):
        """Clear all data from the vector store"""
        self.client.delete_collection("document_chunks")
        self.collection = self.client.create_collection(
            name="document_chunks",
            metadata={"hnsw:space": "cosine"}
        )
        print("Vector store cleared")
    
    def get_count(self) -> int:
        """Get total number of chunks in the store"""
        return self.collection.count()

# Global instance
_vector_store = None

def get_vector_store() -> VectorStore:
    """Get or create vector store singleton"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store