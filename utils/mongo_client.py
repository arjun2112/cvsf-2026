"""
FinOps MongoDB Client with Voyage AI Vector Search
Handles database operations and infrastructure knowledge search
"""

import os
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import voyageai


class FinOpsDB:
    """
    MongoDB client for FinOps multi-agent system with Voyage AI embeddings.
    Supports vector search for infrastructure knowledge.
    """
    
    def __init__(self, mongodb_uri: Optional[str] = None, voyage_api_key: Optional[str] = None):
        """
        Initialize FinOpsDB connection.
        
        Args:
            mongodb_uri: MongoDB connection URI (defaults to MONGODB_URI env var)
            voyage_api_key: Voyage AI API key (defaults to VOYAGE_API_KEY env var)
        """
        self.mongodb_uri = mongodb_uri or os.getenv('MONGODB_URI')
        self.voyage_api_key = voyage_api_key or os.getenv('VOYAGE_API_KEY')
        
        if not self.mongodb_uri:
            raise ValueError("MONGODB_URI must be provided or set in environment variables")
        if not self.voyage_api_key:
            raise ValueError("VOYAGE_API_KEY must be provided or set in environment variables")
        
        # Initialize MongoDB client
        try:
            self.client = MongoClient(self.mongodb_uri)
            # Test connection
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB Atlas")
        except ConnectionFailure as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}")
        
        # Initialize Voyage AI client
        self.voyage_client = voyageai.Client(api_key=self.voyage_api_key)
        
        # Database and collection setup - use finops_engine database
        self.db = self.client['finops_engine']
        self.infra_collection = self.db['infra_knowledge']
        self.audit_collection = self.db['audit_trail']
        
        # Vector search configuration
        self.embedding_model = "voyage-3.5"
        self.vector_dimension = 1024  # voyage-3.5 dimension
        self.vector_index_name = "vector_index"
    
    def _generate_embeddings(
        self, 
        texts: List[str], 
        input_type: str = 'document'
    ) -> List[List[float]]:
        """
        Generate embeddings using Voyage AI.
        
        Args:
            texts: List of texts to embed
            input_type: 'document' for storage, 'query' for search
            
        Returns:
            List of embedding vectors
        """
        try:
            result = self.voyage_client.embed(
                texts=texts,
                model=self.embedding_model,
                input_type=input_type
            )
            return result.embeddings
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            raise
    
    def seed_infra_knowledge(
        self, 
        documents: List[Dict[str, Any]], 
        text_field: str = 'content'
    ) -> int:
        """
        Seed infrastructure knowledge with Voyage AI embeddings.
        
        Args:
            documents: List of documents with infrastructure knowledge
            text_field: Field name containing text to embed
            
        Returns:
            Number of documents inserted
        """
        if not documents:
            print("No documents to seed")
            return 0
        
        try:
            # Extract texts for embedding
            texts = [doc.get(text_field, '') for doc in documents]
            
            # Generate embeddings with input_type='document'
            print(f"Generating embeddings for {len(texts)} documents...")
            embeddings = self._generate_embeddings(texts, input_type='document')
            
            # Add embeddings to documents
            docs_with_embeddings = []
            for doc, embedding in zip(documents, embeddings):
                doc_copy = doc.copy()
                doc_copy['embedding'] = embedding
                docs_with_embeddings.append(doc_copy)
            
            # Insert into MongoDB
            result = self.infra_collection.insert_many(docs_with_embeddings)
            inserted_count = len(result.inserted_ids)
            
            print(f"Successfully seeded {inserted_count} documents")
            return inserted_count
            
        except Exception as e:
            print(f"Error seeding infrastructure knowledge: {str(e)}")
            raise
    
    def search_infra_context(
        self, 
        query: str, 
        limit: int = 5,
        score_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search infrastructure knowledge using Atlas Vector Search.
        
        Args:
            query: Search query text
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score (0.0 to 1.0)
            
        Returns:
            List of documents with similarity scores, or empty list if no results
        """
        if not query or not query.strip():
            print("⚠ Empty query provided")
            return []
        
        try:
            # Generate query embedding with input_type='query'
            query_embedding = self._generate_embeddings([query], input_type='query')[0]
            
            # Atlas Vector Search aggregation pipeline
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": self.vector_index_name,
                        "path": "embedding",
                        "queryVector": query_embedding,
                        "numCandidates": limit * 10,  # Oversample for better results
                        "limit": limit
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "content": 1,
                        "metadata": 1,
                        "score": {"$meta": "vectorSearchScore"}
                    }
                }
            ]
            
            # Execute search
            results = list(self.infra_collection.aggregate(pipeline))
            
            # Filter by score threshold
            filtered_results = [
                doc for doc in results 
                if doc.get('score', 0) >= score_threshold
            ]
            
            if not filtered_results:
                print(f"⚠ No results found for query: '{query[:50]}...'")
                return []
            
            print(f"✓ Found {len(filtered_results)} results")
            return filtered_results
            
        except OperationFailure as e:
            # Handle case where vector index doesn't exist
            if "index not found" in str(e).lower():
                print("⚠ Vector search index not found. Please create the index first.")
                print(f"   Index name: {self.vector_index_name}")
                return []
            raise
        except Exception as e:
            print(f"Error searching infrastructure context: {str(e)}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the infra_knowledge collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.infra_collection.count_documents({})
            sample = list(self.infra_collection.find().limit(1))
            
            return {
                "document_count": count,
                "has_documents": count > 0,
                "sample_document": sample[0] if sample else None
            }
        except Exception as e:
            print(f"Error getting collection stats: {str(e)}")
            return {"error": str(e)}
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            print("✓ MongoDB connection closed")


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    # Initialize client
    try:
        db = FinOpsDB()
        
        # Get stats
        stats = db.get_collection_stats()
        print(f"\n✓ Connection successful!")
        print(f"Database: finops_engine")
        print(f"Collection: infra_knowledge")
        print(f"Documents: {stats.get('document_count', 0)}")
        
        # Clean up
        db.close()
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        exit(1)
