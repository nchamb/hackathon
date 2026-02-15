import os
from inngest import Inngest, Event
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Initialize Inngest client for sending events
inngest = Inngest(
    app_id=os.getenv("INNGEST_APP_ID", "product-safety-analyzer"),
    event_key=os.getenv("INNGEST_EVENT_KEY")
)

EVENT_KEY = os.getenv("INNGEST_EVENT_KEY")


def track_tavily_search(product_description, stores, result_count, success, error=None):
    """Track Tavily API search events"""
    if not EVENT_KEY:
        return
    
    try:
        event = Event(
            name="api/tavily.search",
            data={
                "timestamp": datetime.now().isoformat(),
                "product_description": product_description,
                "stores": stores,
                "result_count": result_count,
                "success": success,
                "error": str(error) if error else None,
                "api": "tavily"
            }
        )
        inngest.send_sync(event)
        print(f"✓ Inngest event sent: api/tavily.search")
    except Exception as e:
        print(f"⚠️ Inngest tracking error: {e}")


def track_groq_analysis(product_title, store, success, model="llama-3.3-70b-versatile", error=None):
    """Track Groq AI analysis events"""
    if not EVENT_KEY:
        return
    
    try:
        event = Event(
            name="api/groq.analyze",
            data={
                "timestamp": datetime.now().isoformat(),
                "product_title": product_title,
                "store": store,
                "model": model,
                "success": success,
                "error": str(error) if error else None,
                "api": "groq"
            }
        )
        inngest.send_sync(event)
        print(f"✓ Inngest event sent: api/groq.analyze")
    except Exception as e:
        print(f"⚠️ Inngest tracking error: {e}")


def track_groq_comparison(product_count, success, model="llama-3.3-70b-versatile", error=None):
    """Track Groq product comparison events"""
    if not EVENT_KEY:
        return
    
    try:
        event = Event(
            name="api/groq.compare",
            data={
                "timestamp": datetime.now().isoformat(),
                "product_count": product_count,
                "model": model,
                "success": success,
                "error": str(error) if error else None,
                "api": "groq"
            }
        )
        inngest.send_sync(event)
        print(f"✓ Inngest event sent: api/groq.compare")
    except Exception as e:
        print(f"⚠️ Inngest tracking error: {e}")


def track_groq_qa(question, context_count, success, model="llama-3.3-70b-versatile", error=None):
    """Track Groq Q&A events"""
    if not EVENT_KEY:
        return
    
    try:
        event = Event(
            name="api/groq.qa",
            data={
                "timestamp": datetime.now().isoformat(),
                "question": question,
                "context_products": context_count,
                "model": model,
                "success": success,
                "error": str(error) if error else None,
                "api": "groq"
            }
        )
        inngest.send_sync(event)
        print(f"✓ Inngest event sent: api/groq.qa")
    except Exception as e:
        print(f"⚠️ Inngest tracking error: {e}")


def track_qdrant_save(product_title, store, success, error=None):
    """Track Qdrant database save events"""
    if not EVENT_KEY:
        return
    
    try:
        event = Event(
            name="db/qdrant.save",
            data={
                "timestamp": datetime.now().isoformat(),
                "product_title": product_title,
                "store": store,
                "success": success,
                "error": str(error) if error else None,
                "database": "qdrant"
            }
        )
        inngest.send_sync(event)
        print(f"✓ Inngest event sent: db/qdrant.save")
    except Exception as e:
        print(f"⚠️ Inngest tracking error: {e}")


def track_qdrant_search(query, result_count, success, error=None):
    """Track Qdrant search events"""
    if not EVENT_KEY:
        return
    
    try:
        event = Event(
            name="db/qdrant.search",
            data={
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "result_count": result_count,
                "success": success,
                "error": str(error) if error else None,
                "database": "qdrant"
            }
        )
        inngest.send_sync(event)
        print(f"✓ Inngest event sent: db/qdrant.search")
    except Exception as e:
        print(f"⚠️ Inngest tracking error: {e}")
