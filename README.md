# Sophiie AI Agents Hackathon 2026

**Build the future of AI-human interaction.**

## My Submission

### Participant

| Field | Your Answer |
|-------|-------------|
| **Name** | Cham Bandara |
| **University / Employer** | University of Southern Queensland |

### Project

| Field | Your Answer |
|-------|-------------|
| **Project Name** | Product Safety Analyzer |
| **One-Line Description** | An AI-powered tool that helps consumers make informed decisions about product safety by analyzing ingredients and identifying harmful substances. |
| **Demo Video Link** | https://youtu.be/1KHRLQDkMtA |
| **Tech Stack** | Streamlit, Tavily API, Groq API, Qdrant, BeautifulSoup4, Requests, Inngest |
| **AI Provider(s) Used** | Tavily API, Groq API |

### About the Project
Project is a product safety analyzer that allows users to search for products across Australian stores, analyze their ingredients using AI, and identify potential health risks. The tool uses the Tavily API for web search, Groq API with Llama 3.3 70B for ingredient analysis, and Qdrant for storing product data and embeddings. Users can view safety ratings, harmful ingredient warnings, and compare products based on AI analysis.

#### What does it do?
Application allows users to enter a product they want to buy, searches for it across multiple Australian stores, and uses AI to analyze the ingredients for potential health risks. It provides safety ratings, highlights harmful substances, and allows users to compare products based on their safety profiles.

<!-- 2-3 paragraphs explaining your agent, the problem it solves, and why the interaction matters -->

#### How does the interaction work?
It features a simple web interface where users can select stores, enter a product query, and view results in an intuitive format. The interaction is designed to be quick and informative, with AI analysis presented in a way that helps users understand the safety of products at a glance. The use of expanders allows users to dive deeper into the details if they choose, while the overall design emphasizes clarity and ease of use.

<!-- Describe the user experience — what does a user see, hear, or do when using your agent? -->

#### What makes it special?
The combination of real-time web search, AI-powered ingredient analysis, and a user-friendly interface makes this tool unique. It addresses a common pain point for consumers — understanding product safety — in a way that is accessible and actionable. The use of AI to identify harmful ingredients and provide safety ratings adds significant value beyond what traditional product search tools offer.

<!-- What are you most proud of? What would you want the judges to notice? -->

#### How to run it
1. Clone the repo
2. Install dependencies
3. Configure API keys in `.env`
4. Run the Streamlit app using command:
```bash
streamlit run app.py
```

### For detailed setup instructions, see [SETUP.md](./SETUP.md)

<!-- Step-by-step instructions to set up and run your project locally -->

#### Architecture / Technical Notes
- **Frontend:** Streamlit
- **Search:** Tavily API
- **AI Analysis:** Groq API with Llama 3.3 70B
- **Vector Database:** Qdrant (in-memory) with sentence-transformers
- **Web Scraping:** BeautifulSoup4 + Requests for product images
- **Monitoring:** Inngest for event tracking and observability