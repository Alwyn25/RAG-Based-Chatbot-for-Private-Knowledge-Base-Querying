import asyncio
from typing import List
import hashlib
import json

class EmbeddingGenerator:
    def __init__(self, model_name: str = "simple-hash-embedding"):
        """Initialize embedding generator with simple hash-based approach"""
        self.model_name = model_name
        self.dimension = 384  # Standard embedding dimension
        print(f"Using simple hash-based embeddings: {self.model_name}")

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text using hash-based approach"""
        try:
            # Simple hash-based embedding for development
            # In production, replace with actual sentence-transformers
            return self._hash_to_embedding(text)
            
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * self.dimension

    def _hash_to_embedding(self, text: str) -> List[float]:
        """Convert text to embedding using hash functions"""
        # Normalize text
        text = text.lower().strip()
        
        # Generate multiple hashes to create embedding
        embeddings = []
        
        # Use different hash functions and seeds
        for i in range(self.dimension // 4):
            # Create different variations of the text
            variations = [
                text,
                text + str(i),
                text[::-1] + str(i),  # Reversed text
                ''.join(sorted(text)) + str(i)  # Sorted characters
            ]
            
            for variation in variations:
                hash_obj = hashlib.md5((variation + str(i)).encode())
                hash_int = int(hash_obj.hexdigest(), 16)
                # Normalize to [-1, 1] range
                normalized = (hash_int % 2000000) / 1000000 - 1
                embeddings.append(normalized)
                
                if len(embeddings) >= self.dimension:
                    break
            
            if len(embeddings) >= self.dimension:
                break
        
        # Ensure we have exactly the right dimension
        while len(embeddings) < self.dimension:
            embeddings.append(0.0)
        
        return embeddings[:self.dimension]

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            embeddings = []
            for text in texts:
                embedding = await self.generate_embedding(text)
                embeddings.append(embedding)
            return embeddings
            
        except Exception as e:
            print(f"Error generating batch embeddings: {e}")
            # Return zero vectors as fallback
            return [[0.0] * self.dimension for _ in texts]

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        return self.dimension
