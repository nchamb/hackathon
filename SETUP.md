# Shopping Assistant Setup Guide

## Prerequisites

1. **Tavily API Key**: Get a free API key at https://tavily.com (includes 1,000 free searches/month)

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `streamlit` - Web interface
- `tavily-python` - Web search API
- `qdrant-client` - Vector database for storing products
- `sentence-transformers` - For creating product embeddings

### 2. Configure API Key

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
TAVILY_API_KEY=tvly-your-tavily-key-here
```

**Get API Key:**
- Tavily: https://tavily.com (free tier: 1,000 searches/month)

### 3. Run the Application

```bash
streamlit run app.py
```

## How It Works

1. **Select Stores**: Choose from Australian stores (Coles, Aldi, Chemist Warehouse, etc.)
2. **Enter Product**: Describe what you want to buy
3. **Tavily Search**: Searches the web for current product listings
4. **Extract Ingredients**: Automatically extracts ingredients/details from product pages
5. **Save to Database**: Stores products in Qdrant vector database for future searches
6. **View Results**: See products organized by store with direct links and ingredients

## Features

- **Tavily Search API**: Fast, accurate web search specialized for products
- **Multi-Store Filtering**: Only searches specified Australian stores
- **Ingredient Extraction**: Automatically extracts ingredients from product content
- **Vector Database**: Stores all products with embeddings in Qdrant
- **Semantic Search**: Search saved products using natural language
- **Direct Links**: Provides URLs to product pages
- **100% Free**: No OpenAI costs - uses only Tavily's free tier

## Database Features

- **Automatic Storage**: Every search result is saved to Qdrant
- **Ingredient Tracking**: Extracts and stores ingredient information
- **Similarity Search**: Find similar products using AI embeddings
- **View History**: See all previously searched products
- **In-Memory Database**: Fast access, data persists during session

## Cost Breakdown

- **Tavily**: Free tier includes 1,000 searches/month
- **Qdrant**: In-memory (free, no server needed)
- **Sentence Transformers**: Local model (free)
- **Total**: Completely free!

## Notes

- Tavily searches official store websites for current prices
- Results include direct links to products
- Ingredients are extracted automatically from product descriptions
- Database is in-memory, so data persists only while app is running
- For persistent storage, configure Qdrant server (optional)

## Troubleshooting

**Error: "Tavily API key not found"**
- Make sure you created the `.env` file with your Tavily API key
- Get your key at https://tavily.com
- Restart the Streamlit app after adding the key

**No search results**
- Check your internet connection
- Verify your API key is valid
- Try a more specific product description
- Ensure selected stores sell the product type

**Database errors**
- First time running may download sentence transformer model (~80MB)
- Check you have enough RAM for in-memory database
- Restart the app if database seems corrupted
