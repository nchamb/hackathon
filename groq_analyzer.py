import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_ingredients_with_groq(product_title, ingredients_text, store):
    """
    Use Groq's Llama model to analyze product ingredients
    
    Args:
        product_title: Name of the product
        ingredients_text: Raw ingredients text from product
        store: Store name
    
    Returns:
        Dict with analysis results
    """
    
    if not os.getenv("GROQ_API_KEY"):
        return {
            "success": False,
            "error": "Groq API key not found",
            "analysis": None
        }
    
    try:
        prompt = f"""Analyze the following product and its ingredients in detail:

Product: {product_title}
Store: {store}
Ingredients/Details: {ingredients_text}

Please provide a comprehensive analysis with the following structure:

1. **INGREDIENTS BREAKDOWN:**
   - List each ingredient identified
   - For EACH ingredient, explain what it is and its purpose

2. **HARMFUL/CONCERNING INGREDIENTS:**
   - ⚠️ List any ingredients that are potentially harmful, controversial, or should be consumed with caution
   - Explain WHY each is concerning (health risks, side effects, regulatory concerns)
   - Rate severity: HIGH RISK, MODERATE RISK, or LOW RISK
   - If NO harmful ingredients found, clearly state "✅ No harmful ingredients detected"

3. **ALLERGENS:**
   - List all potential allergens
   - Include both declared and hidden allergens

4. **ADDITIVES & PRESERVATIVES:**
   - List artificial colors, flavors, preservatives
   - Note any E-numbers and their safety profile

5. **HEALTH CONSIDERATIONS:**
   - Nutritional highlights (if mentioned)
   - Who should avoid this product
   - Safe consumption guidelines

6. **DIETARY SUITABILITY:**
   - Vegan/Vegetarian status
   - Gluten-free status
   - Other dietary restrictions

Be specific about harmful ingredients. If any ingredient has known health risks, regulatory warnings, or is banned in certain countries, mention it explicitly."""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert toxicologist and nutritionist who specializes in food safety and ingredient analysis. Your primary focus is identifying harmful, controversial, or potentially dangerous ingredients in products. Be thorough and err on the side of caution when identifying risks. Provide clear, evidence-based warnings about harmful substances."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,  # Lower temperature for more factual analysis
            max_tokens=2000
        )
        
        analysis = response.choices[0].message.content
        
        return {
            "success": True,
            "analysis": analysis,
            "model": "llama-3.3-70b-versatile"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "analysis": None
        }


def compare_products_with_groq(products_data):
    """
    Compare multiple products using Groq with focus on harmful ingredients
    
    Args:
        products_data: List of dicts with product info
    
    Returns:
        Comparison analysis
    """
    
    if not os.getenv("GROQ_API_KEY"):
        return {
            "success": False,
            "error": "Groq API key not found",
            "comparison": None
        }
    
    try:
        # Build comparison prompt
        products_text = ""
        for idx, prod in enumerate(products_data, 1):
            products_text += f"\n**Product {idx}:** {prod['title']}\n"
            products_text += f"Store: {prod['store']}\n"
            products_text += f"Ingredients: {prod.get('ingredients', 'Not available')}\n"
            products_text += "---\n"
        
        prompt = f"""Compare these products with a focus on safety and health:

{products_text}

Provide a comprehensive comparison including:

1. **HARMFUL INGREDIENTS COMPARISON:**
   - Which product has the MOST harmful/concerning ingredients?
   - Which product has the LEAST harmful ingredients?
   - List specific harmful ingredients in each product with risk levels
   - Rank products from SAFEST to MOST CONCERNING

2. **OVERALL SAFETY RANKING:**
   - Rank all products from 1 (safest) to {len(products_data)} (most concerning)
   - Provide clear justification for each ranking

3. **ADDITIVES & PRESERVATIVES:**
   - Which has most/least artificial additives?
   - Which has most/least preservatives?

4. **HEALTH RECOMMENDATION:**
   - Best choice for health-conscious consumers
   - Which to avoid and why
   - Any products with red-flag ingredients

5. **VALUE ASSESSMENT:**
   - Best balance of safety and value
   - Worth the price considering ingredient quality

Be objective, evidence-based, and prioritize consumer safety."""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a product safety expert and toxicologist. Your primary concern is consumer health and safety. Be critical of harmful ingredients and provide clear safety rankings. Prioritize health over taste or price."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=2000
        )
        
        comparison = response.choices[0].message.content
        
        return {
            "success": True,
            "comparison": comparison,
            "model": "llama-3.3-70b-versatile"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "comparison": None
        }


def ask_about_ingredients(question, context_products):
    """
    Answer questions about ingredients using Groq
    
    Args:
        question: User's question
        context_products: Relevant products from database
    
    Returns:
        Answer to the question
    """
    
    if not os.getenv("GROQ_API_KEY"):
        return {
            "success": False,
            "error": "Groq API key not found",
            "answer": None
        }
    
    try:
        # Build context from products
        context = "Available product information:\n\n"
        for prod in context_products[:5]:  # Limit to 5 most relevant
            context += f"- {prod.get('title', 'Unknown')}\n"
            context += f"  Store: {prod.get('store', 'Unknown')}\n"
            context += f"  Ingredients: {prod.get('ingredients', 'Not available')}\n\n"
        
        prompt = f"""{context}

User question: {question}

Please answer based on the product information above. If the information is insufficient, say so clearly."""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions about product ingredients. Be accurate and cite specific products when relevant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,
            max_tokens=800
        )
        
        answer = response.choices[0].message.content
        
        return {
            "success": True,
            "answer": answer,
            "model": "llama-3.3-70b-versatile"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "answer": None
        }
