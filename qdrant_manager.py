import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import uuid
from datetime import datetime

# Initialize Qdrant client (using in-memory for simplicity, can switch to server)
qdrant_client = QdrantClient(":memory:")  # Use ":memory:" for in-memory or provide URL for server

# Initialize sentence transformer for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

COLLECTION_NAME = "product_ingredients"

def initialize_qdrant():
    """Initialize Qdrant collection for storing product ingredients"""
    try:
        # Check if collection exists
        collections = qdrant_client.get_collections().collections
        collection_exists = any(col.name == COLLECTION_NAME for col in collections)
        
        if not collection_exists:
            # Create collection
            qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=384,  # all-MiniLM-L6-v2 embedding size
                    distance=Distance.COSINE
                )
            )
            print(f"Created Qdrant collection: {COLLECTION_NAME}")
        else:
            print(f"Collection {COLLECTION_NAME} already exists")
        
        return True
    except Exception as e:
        print(f"Error initializing Qdrant: {e}")
        return False


def extract_ingredients_from_content(content, title):
    """
    Extract ingredients information from product content.
    This is a simple extraction - looks for ingredient-related text.
    """
    ingredients_text = ""
    
    # Common keywords that indicate ingredients section
    keywords = ["ingredients", "contains", "composition", "made with", "made from"]
    
    content_lower = content.lower()
    title_lower = title.lower()
    
    # Check if content mentions ingredients
    for keyword in keywords:
        if keyword in content_lower:
            # Try to extract the relevant part
            start_idx = content_lower.find(keyword)
            # Get text after the keyword (next 200 chars)
            ingredients_text = content[start_idx:start_idx+300]
            break
    
    # If no ingredients found in content, use the full content as context
    if not ingredients_text:
        ingredients_text = content[:300]  # First 300 chars
    
    return ingredients_text


def save_product_to_qdrant(product_data):
    """
    Save product with ingredients to Qdrant
    
    Args:
        product_data: Dict with keys - title, url, content, store, ingredients, groq_analysis
    """
    try:
        # Extract or get ingredients
        ingredients = product_data.get('ingredients', '')
        if not ingredients:
            ingredients = extract_ingredients_from_content(
                product_data.get('content', ''),
                product_data.get('title', '')
            )
        
        # Create embedding for the product (title + ingredients)
        text_to_embed = f"{product_data.get('title', '')} {ingredients}"
        embedding = model.encode(text_to_embed).tolist()
        
        # Create point
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "title": product_data.get('title', ''),
                "url": product_data.get('url', ''),
                "store": product_data.get('store', ''),
                "ingredients": ingredients,
                "content": product_data.get('content', '')[:500],  # Store first 500 chars
                "timestamp": datetime.now().isoformat(),
                "product_description": product_data.get('product_description', ''),
                "groq_analysis": product_data.get('groq_analysis', '')  # Store Groq analysis
            }
        )
        
        # Upsert to Qdrant
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=[point]
        )
        
        return True, ingredients
    except Exception as e:
        print(f"Error saving to Qdrant: {e}")
        return False, str(e)


def search_similar_products(query, limit=5):
    """
    Search for similar products in Qdrant based on query
    
    Args:
        query: Search query (product name or ingredients)
        limit: Number of results to return
    """
    try:
        # Create embedding for query
        query_embedding = model.encode(query).tolist()
        
        # Search in Qdrant
        results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=limit
        )
        
        return results
    except Exception as e:
        print(f"Error searching Qdrant: {e}")
        return []


def get_all_products():
    """Get all stored products from Qdrant"""
    try:
        # Scroll through all points
        results = qdrant_client.scroll(
            collection_name=COLLECTION_NAME,
            limit=100
        )
        return results[0]  # Returns list of points
    except Exception as e:
        print(f"Error getting products: {e}")
        return []


def get_collection_stats():
    """Get statistics about the collection"""
    try:
        info = qdrant_client.get_collection(collection_name=COLLECTION_NAME)
        return {
            "total_products": info.points_count,
            "vector_size": info.config.params.vectors.size,
            "distance": info.config.params.vectors.distance
        }
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {}
