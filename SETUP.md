# Shopping Assistant Setup Guide

## Prerequisites

1. **Tavily API Key**: Get a free API key at https://tavily.com (includes 1,000 free searches/month)
2. **Groq API Key**: Get a free API key at https://console.groq.com
3. **Inngest Account** (Optional): For monitoring AI API calls - https://www.inngest.com

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
- `groq` - AI analysis with Llama models
- `inngest` - API monitoring and observability

### 2. Configure API Keys

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```
TAVILY_API_KEY=tvly-your-tavily-key-here
GROQ_API_KEY=gsk-your-groq-key-here
INNGEST_APP_ID=product-safety-analyzer
INNGEST_EVENT_KEY=your-inngest-event-key-here
INNGEST_SIGNING_KEY=signkey-prod-your-signing-key-here
```

**Get API Keys:**
- Tavily: https://tavily.com (free tier: 1,000 searches/month)
- Groq: https://console.groq.com (free tier available)
- Inngest: https://www.inngest.com (optional, for monitoring)
  - Event Key: Found in your Inngest dashboard under "Keys"
  - Signing Key: Used to authenticate requests between Inngest and your app
- Tavily: https://tavily.com (free tier: 1,000 searches/month)

### 3. Run the Application

```bash
streamlit run app.py
```

## How It Works

1. **Select Stores**: Choose from Australian stores (Coles, Aldi, Chemist Warehouse, etc.)
2. **Enter Product**: Describe what you want to buy
3. **Tavily Search**: Searches the web for current product listings
4. **AI Analysis**: Groq Llama analyzes ingredients for harmful substances
5. **Save to Database**: Stores products with AI analysis in Qdrant
6. **View Results**: See products with safety ratings and harmful ingredient warnings
7. **Monitor**: All API calls tracked with Inngest for observability

## Features

- **Tavily Search API**: Fast, accurate web search specialized for products
- **Groq AI Analysis**: Llama 3.3 70B analyzes ingredients for health risks
- **Multi-Store Filtering**: Only searches specified Australian stores
- **Harmful Ingredient Detection**: AI identifies and rates dangerous substances (🔴🟡🟢✅)
- **Vector Database**: Stores all products with embeddings in Qdrant
- **Semantic Search**: Search saved products using natural language
- **Product Comparison**: AI-powered safety comparison between products
- **Q&A Assistant**: Ask questions about ingredients and allergens
- **API Monitoring**: Inngest tracks all API calls and errors
- **100% Free APIs**: Tavily (1000/mo), Groq (free tier), Qdrant (in-memory)

## Monitoring with Inngest

Inngest automatically tracks:
- **Tavily searches** - Query, stores, result count, errors
- **Groq AI calls** - Ingredient analysis, comparisons, Q&A
- **Qdrant operations** - Product saves, searches
- **Error tracking** - All API failures with context

View your monitoring dashboard at: https://app.inngest.com

## Database Features

- **Automatic Storage**: Every search result is saved to Qdrant with AI analysis
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
