import os
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from dotenv import load_dotenv
from qdrant_manager import save_product_to_qdrant, initialize_qdrant, extract_ingredients_from_content
from groq_analyzer import analyze_ingredients_with_groq
from ingredient_analyzer import extract_harmful_ingredients, get_risk_emoji
from inngest_monitor import track_tavily_search

load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Initialize Qdrant on module load
initialize_qdrant()


def extract_image_from_result(result):
    """Extract product image URL from search result if available"""
    # Check for image in result
    if 'image' in result:
        return result['image']
    
    # Try to scrape image from product page
    url = result.get('url', '')
    if not url or url == '#':
        return None
    
    try:
        # Set a timeout and user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try different image selectors for various stores
            image_selectors = [
                # Coles
                'img[class*="product"]',
                'img[class*="Product"]',
                # Woolworths
                'img[class*="image"]',
                'img[alt*="product"]',
                # General
                'meta[property="og:image"]',
                'img[itemprop="image"]',
                'img.product-image',
                'img.main-image'
            ]
            
            for selector in image_selectors:
                if selector.startswith('meta'):
                    img = soup.select_one(selector)
                    if img and img.get('content'):
                        return img.get('content')
                else:
                    img = soup.select_one(selector)
                    if img and img.get('src'):
                        img_url = img.get('src')
                        # Make absolute URL if relative
                        if img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        elif img_url.startswith('/'):
                            from urllib.parse import urlparse
                            parsed = urlparse(url)
                            img_url = f"{parsed.scheme}://{parsed.netloc}{img_url}"
                        return img_url
    except Exception as e:
        # Silently fail - image extraction is optional
        print(f"Could not extract image from {url}: {e}")
    
    return None


def format_results_simple(search_results, product_description, stores):
    """
    Format search results without using GPT and save to Qdrant
    """
    if not search_results:
        return f"No products found for '{product_description}' in the selected stores. Try:\n- Using a different product name\n- Selecting different stores\n- Making your search more specific"
    
    # Group results by store
    store_results = {}
    saved_count = 0
    
    for result in search_results:
        url = result.get('url', '')
        # Extract store name from URL
        store_name = None
        for store in stores:
            store_domain = store.lower().replace(" ", "")
            if store_domain in url.lower():
                store_name = store
                break
        if store_name:
            if store_name not in store_results:
                store_results[store_name] = []
            store_results[store_name].append(result)
            
            # Analyze ingredients with Groq
            ingredients_for_analysis = extract_ingredients_from_content(
                result.get('content', ''),
                result.get('title', '')
            )
            
            groq_result = analyze_ingredients_with_groq(
                result.get('title', ''),
                ingredients_for_analysis,
                store_name
            )
            
            groq_analysis = groq_result.get('analysis', '') if groq_result.get('success') else ''
            
            # Save to Qdrant with Groq analysis
            image_url = extract_image_from_result(result)
            product_data = {
                'title': result.get('title', ''),
                'url': url,
                'content': result.get('content', ''),
                'store': store_name,
                'product_description': product_description,
                'groq_analysis': groq_analysis,
                'image': image_url
            }
            success, ingredients = save_product_to_qdrant(product_data)
            if success:
                saved_count += 1
                # Add to result for display
                result['extracted_ingredients'] = ingredients
                result['groq_analysis'] = groq_analysis
                result['image'] = image_url
    
    # Format output
    output = f"# Search Results for: {product_description}\n\n"
    output += f"💾 **Saved {saved_count} products to database**\n\n"
    
    for store in stores:
        output += f"## {store}\n\n"
        if store in store_results:
            for result in store_results[store]:
                title = result.get('title', 'No title')
                url = result.get('url', '#')
                content = result.get('content', 'No description available')
                ingredients = result.get('extracted_ingredients', '')
                groq_analysis = result.get('groq_analysis', '')
                image_url = result.get('image')
                
                output += f"### {title}\n"
                if image_url:
                    output += f"![Product Image]({image_url})\n\n"
                output += f"🔗 [View Product]({url})\n\n"
                
                if groq_analysis:
                    # Extract harmful ingredients summary
                    harmful_info = extract_harmful_ingredients(groq_analysis)
                    risk_emoji = get_risk_emoji(harmful_info['risk_level'])
                    
                    # Show risk level prominently
                    output += f"**Safety Rating:** {risk_emoji} {harmful_info['risk_level']}\n\n"
                    
                    if harmful_info['has_harmful']:
                        output += f"**⚠️ HARMFUL INGREDIENTS DETECTED:**\n"
                        if harmful_info['harmful_list']:
                            for harmful in harmful_info['harmful_list']:
                                output += f"- {harmful}\n"
                        output += "\n"
                    else:
                        output += f"**✅ No harmful ingredients detected**\n\n"
                    
                    output += f"**🤖 Full AI Analysis:**\n{groq_analysis}\n\n"
                elif ingredients:
                    output += f"**Ingredients/Details:** {ingredients}\n\n"
                else:
                    output += f"{content[:200]}...\n\n"
                
                output += "---\n\n"
        else:
            output += f"❌ No results found at {store}\n\n"
    
    return output


def search_products_with_tavily(product_description, stores):
    """
    Use Tavily to search the web for products.
    
    Args:
        product_description: User's description of the product they want
        stores: List of store names to search in
    
    Returns:
        Dict with search results and product information
    """
    
    if not os.getenv("TAVILY_API_KEY"):
        return {
            "success": False,
            "error": "Tavily API key not found. Please set TAVILY_API_KEY in your .env file.",
            "results": None
        }
    
    try:
        # Search with Tavily
        search_query = f"{product_description} price Australia {' '.join(stores)}"
        
        tavily_response = tavily_client.search(
            query=search_query,
            search_depth="advanced",
            max_results=10,
            include_domains=[
                "coles.com.au",
                "aldi.com.au", 
                "chemistwarehouse.com.au",
                "woolworths.com.au",
                "iga.com.au",
                "target.com.au",
                "kmart.com.au",
                "bunnings.com.au"
            ]
        )
        
        # Format results without GPT
        search_results = tavily_response.get('results', [])
        formatted_results = format_results_simple(search_results, product_description, stores)
        
        # Track with Inngest
        track_tavily_search(product_description, stores, len(search_results), True)
        
        return {
            "success": True,
            "results": formatted_results,
            "raw_results": search_results,
            "search_engine": "Tavily"
        }
        
    except Exception as e:
        # Track error with Inngest
        track_tavily_search(product_description, stores, 0, False, error=e)
        
        return {
            "success": False,
            "error": str(e),
            "results": None
        }


def search_products_with_web_search(product_description, stores):
    """
    Main search function - uses Tavily for web search
    """
    return search_products_with_tavily(product_description, stores)
