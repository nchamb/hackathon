import streamlit as st
from search_agent import search_products_with_web_search
from qdrant_manager import get_collection_stats, get_all_products, search_similar_products
from groq_analyzer import compare_products_with_groq, ask_about_ingredients
from ingredient_analyzer import extract_harmful_ingredients, get_risk_emoji
import os

# Set page configuration
st.set_page_config(
    page_title="Shopping Assistant",
    page_icon="🛒",
    layout="centered"
)

# Initialize session state
if 'selected_stores' not in st.session_state:
    st.session_state.selected_stores = []
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'search_items' not in st.session_state:
    st.session_state.search_items = ""
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'is_searching' not in st.session_state:
    st.session_state.is_searching = False

# Available stores
stores = [
    "Coles",
    "Aldi",
    "Chemist Warehouse",
    "Woolworths",
    "IGA",
    "Target",
    "Kmart",
    "Bunnings"
]

# Progress indicator
st.progress((st.session_state.step - 1) / 2)

# STEP 1: Store Selection
if st.session_state.step == 1:
    st.title("🛒 Step 1: Select Stores")
    st.write("Please select the stores you'd like to search:")
    
    # Store selection using checkboxes
    st.subheader("Available Stores")
    selected = []

    for store in stores:
        if st.checkbox(store, key=f"checkbox_{store}"):
            selected.append(store)

    # Update session state
    st.session_state.selected_stores = selected

    # Display selected stores
    if selected:
        st.success(f"**Selected stores:** {', '.join(selected)}")
        
        if st.button("Next: What do you want to buy?", type="primary"):
            st.session_state.step = 2
            st.rerun()
    else:
        st.warning("Please select at least one store to continue.")

# STEP 2: Item Search
elif st.session_state.step == 2:
    st.title("🛍️ Step 2: What do you want to buy?")
    st.write(f"Searching in: **{', '.join(st.session_state.selected_stores)}**")
    
    # Text input for single item
    search_query = st.text_input(
        "Enter the item you're looking for:",
        placeholder="e.g., milk",
        value=st.session_state.search_items,
        on_change=lambda: setattr(st.session_state, 'search_triggered', True) if search_query else None
    )
    
    st.session_state.search_items = search_query
    
    # Trigger search on Enter key press
    search_triggered = getattr(st.session_state, 'search_triggered', False)
    if search_triggered and search_query:
        st.session_state.is_searching = True
        st.session_state.search_triggered = False
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Back to Stores"):
            st.session_state.step = 1
            st.rerun()
    
    with col2:
        if st.button("Search", type="primary", disabled=not search_query):
            st.session_state.is_searching = True
            
            # Check if API key is set
            if not os.getenv("TAVILY_API_KEY"):
                st.error("⚠️ Tavily API key not found. Please set TAVILY_API_KEY in your .env file.")
                st.info("Get your free API key at: https://tavily.com")
                st.session_state.is_searching = False
            else:
                with st.spinner("🔍 Searching for products..."):
                    # Call the search agent
                    results = search_products_with_web_search(
                        search_query,
                        st.session_state.selected_stores
                    )
                    st.session_state.search_results = results
                    st.session_state.is_searching = False
    
    # Display search results
    if st.session_state.search_results:
        st.divider()
        st.subheader("Search Results")
        
        if st.session_state.search_results.get("success"):
            st.markdown(st.session_state.search_results["results"])
            st.caption(f"Results powered by {st.session_state.search_results.get('search_engine', 'Tavily')}")
        else:
            st.error(f"❌ Search failed: {st.session_state.search_results.get('error')}")
        
        if st.button("New Search"):
            st.session_state.search_results = None
            st.session_state.search_items = ""
            st.rerun()

# Display current selection in sidebar
with st.sidebar:
    st.header("Summary")
    
    st.subheader("📍 Step " + str(st.session_state.step) + " of 2")
    
    if st.session_state.selected_stores:
        st.write("**Selected Stores:**")
        for store in st.session_state.selected_stores:
            st.write(f"✓ {store}")
    else:
        st.write("No stores selected yet")
    
    if st.session_state.search_items:
        st.write("**Search Query:**")
        st.write(st.session_state.search_items)
    # Database stats
    st.divider()
    st.subheader("💾 Database Stats")
    try:
        stats = get_collection_stats()
        if stats:
            st.metric("Total Products Saved", stats.get('total_products', 0))
            
            # View all products button
            if st.button("View Saved Products"):
                st.session_state.show_database = True
            
            # Ask AI button
            if st.button("🤖 Ask AI About Products"):
                st.session_state.show_ai_chat = True
        else:
            st.write("Database not initialized")
    except Exception as e:
        st.write("Database initializing...")

# Show database view if requested
if st.session_state.get('show_database', False):
    st.divider()
    st.subheader("💾 Saved Products Database")
    
    try:
        products = get_all_products()
        if products:
            st.write(f"Found {len(products)} products in database")
            
            # Search within saved products
            search_query = st.text_input("Search saved products:", key="db_search")
            if search_query:
                similar = search_similar_products(search_query, limit=10)
                for result in similar:
                    payload = result.payload
                    
                    # Extract harmful info if analysis exists
                    harmful_info = None
                    if payload.get('groq_analysis'):
                        harmful_info = extract_harmful_ingredients(payload.get('groq_analysis'))
                    
                    # Title with risk indicator
                    title_display = f"{payload.get('title', 'Unknown')} - {payload.get('store', 'Unknown Store')}"
                    if harmful_info:
                        risk_emoji = get_risk_emoji(harmful_info['risk_level'])
                        title_display = f"{risk_emoji} {title_display}"
                    
                    with st.expander(title_display):
                        # Show product image if available
                        if payload.get('image'):
                            st.image(payload.get('image'), width=200)
                        
                        st.write(f"**Store:** {payload.get('store', 'Unknown')}")
                        st.write(f"**URL:** {payload.get('url', 'N/A')}")
                        
                        if harmful_info:
                            st.write(f"**Safety Rating:** {get_risk_emoji(harmful_info['risk_level'])} {harmful_info['risk_level']}")
                            
                            if harmful_info['has_harmful']:
                                st.warning("**⚠️ Harmful Ingredients Detected**")
                                if harmful_info['harmful_list']:
                                    for h in harmful_info['harmful_list']:
                                        st.write(f"- {h}")
                            else:
                                st.success("**✅ No harmful ingredients detected**")
                        
                        if payload.get('groq_analysis'):
                            with st.expander("View Full AI Analysis"):
                                st.write(payload.get('groq_analysis'))
                        else:
                            st.write(f"**Ingredients/Details:** {payload.get('ingredients', 'N/A')}")
                        
                        st.write(f"**Similarity Score:** {result.score:.2f}")
            else:
                # Show all products
                for product in products[:20]:  # Show first 20
                    payload = product.payload
                    with st.expander(f"{payload.get('title', 'Unknown')} - {payload.get('store', 'Unknown Store')}"):
                        # Show product image if available
                        if payload.get('image'):
                            st.image(payload.get('image'), width=200)
                        
                        st.write(f"**Store:** {payload.get('store', 'Unknown')}")
                        st.write(f"**URL:** {payload.get('url', 'N/A')}")
                        
                        if payload.get('groq_analysis'):
                            st.write(f"**🤖 AI Analysis:**")
                            st.write(payload.get('groq_analysis'))
                        else:
                            st.write(f"**Ingredients/Details:** {payload.get('ingredients', 'N/A')}")
        else:
            st.info("No products saved yet. Search for products to populate the database!")
    except Exception as e:
        st.error(f"Error accessing database: {e}")
    
    if st.button("Close Database View"):
        st.session_state.show_database = False
        st.rerun()

# AI Chat Interface
if st.session_state.get('show_ai_chat', False):
    st.divider()
    st.subheader("🤖 AI Product Assistant")
    st.write("Ask questions about saved products and their ingredients")
    
    # Get all products for context
    try:
        all_products = get_all_products()
        
        if all_products:
            # Question input
            user_question = st.text_input(
                "Ask about ingredients, allergens, or product comparisons:",
                placeholder="e.g., Which products are gluten-free? Compare the healthiest options."
            )
            
            if user_question and st.button("Ask AI"):
                with st.spinner("AI is analyzing..."):
                    # Get relevant products
                    relevant_products = search_similar_products(user_question, limit=5)
                    
                    # Prepare context
                    context_products = []
                    for prod in relevant_products:
                        context_products.append(prod.payload)
                    
                    # Ask Groq
                    result = ask_about_ingredients(user_question, context_products)
                    
                    if result.get('success'):
                        st.success("**AI Answer:**")
                        st.write(result.get('answer'))
                        st.caption(f"Powered by {result.get('model')}")
                    else:
                        st.error(f"Error: {result.get('error')}")
            
            # Compare products feature
            st.divider()
            st.subheader("Compare Products")
            
            if len(all_products) >= 2:
                st.write("Select products to compare:")
                
                # Create product selection
                product_options = {f"{p.payload.get('title')} ({p.payload.get('store')})": p for p in all_products[:10]}
                selected_products = st.multiselect(
                    "Choose 2-5 products",
                    options=list(product_options.keys()),
                    max_selections=5
                )
                
                if len(selected_products) >= 2 and st.button("Compare Selected Products"):
                    with st.spinner("AI is comparing..."):
                        # Prepare product data
                        products_to_compare = []
                        for prod_key in selected_products:
                            prod = product_options[prod_key]
                            products_to_compare.append({
                                'title': prod.payload.get('title'),
                                'store': prod.payload.get('store'),
                                'ingredients': prod.payload.get('ingredients', 'Not available'),
                                'groq_analysis': prod.payload.get('groq_analysis', '')
                            })
                        
                        # Get comparison
                        comparison_result = compare_products_with_groq(products_to_compare)
                        
                        if comparison_result.get('success'):
                            st.success("**Comparison Results:**")
                            st.write(comparison_result.get('comparison'))
                            st.caption(f"Powered by {comparison_result.get('model')}")
                        else:
                            st.error(f"Error: {comparison_result.get('error')}")
            else:
                st.info("Need at least 2 products in database to compare. Search for more products!")
        
        else:
            st.info("No products in database yet. Search for products first!")
    
    except Exception as e:
        st.error(f"Error: {e}")
    
    if st.button("Close AI Assistant"):
        st.session_state.show_ai_chat = False
        st.rerun()
