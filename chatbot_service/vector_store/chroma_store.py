import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import uuid
import os

class ChromaStore:
    def __init__(self, collection_name: str = "customer_support_docs"):
        """Initialize ChromaDB connection"""
        self.collection_name = collection_name
        
        # Create ChromaDB client with persistent storage
        self.chroma_path = os.path.join(os.getcwd(), "chroma_db")
        os.makedirs(self.chroma_path, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=self.chroma_path)
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"Loaded existing ChromaDB collection: {collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Customer support documents"}
            )
            print(f"Created new ChromaDB collection: {collection_name}")

    async def add_document(self, doc_id: str, embedding: List[float], metadata: Dict[str, Any]) -> None:
        """Add a document to the vector store"""
        try:
            # Ensure doc_id is unique
            unique_id = f"{doc_id}_{uuid.uuid4().hex[:8]}"
            
            self.collection.add(
                embeddings=[embedding],
                documents=[metadata.get("text", "")],
                metadatas=[metadata],
                ids=[unique_id]
            )
            
        except Exception as e:
            print(f"Error adding document to ChromaDB: {e}")
            raise

    async def similarity_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            # Generate query embedding
            from utils.embeddings import EmbeddingGenerator
            embedding_gen = EmbeddingGenerator()
            query_embedding = await embedding_gen.generate_embedding(query)
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    result = {
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                        'distance': results['distances'][0][i] if results['distances'] and results['distances'][0] else 0.0,
                        'id': results['ids'][0][i] if results['ids'] and results['ids'][0] else ""
                    }
                    formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching ChromaDB: {e}")
            return []

    async def get_document_count(self) -> int:
        """Get total number of documents in the collection"""
        try:
            return self.collection.count()
        except Exception as e:
            print(f"Error getting document count: {e}")
            return 0

    def clear_collection(self) -> None:
        """Clear all documents from the collection"""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Customer support documents"}
            )
            print(f"Cleared ChromaDB collection: {self.collection_name}")
            
        except Exception as e:
            print(f"Error clearing collection: {e}")
            raise

    async def delete_document(self, doc_id: str) -> bool:
        """Delete a specific document"""
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False

    async def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents from the collection"""
        try:
            results = self.collection.get()
            
            formatted_results = []
            if results['documents']:
                for i in range(len(results['documents'])):
                    result = {
                        'text': results['documents'][i],
                        'metadata': results['metadatas'][i] if results['metadatas'] else {},
                        'id': results['ids'][i] if results['ids'] else ""
                    }
                    formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            print(f"Error getting all documents: {e}")
            return []

    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        try:
            count = self.collection.count()
            return {
                'name': self.collection_name,
                'document_count': count,
                'path': self.chroma_path
            }
        except Exception as e:
            print(f"Error getting collection info: {e}")
            return {
                'name': self.collection_name,
                'document_count': 0,
                'path': self.chroma_path,
                'error': str(e)
            }
