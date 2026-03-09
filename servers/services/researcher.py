import os
import json
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

class ResearcherService:
    def __init__(self):
        self.search = DuckDuckGoSearchRun()
        
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=api_key)
        
        self.summarize_prompt = PromptTemplate(
            input_variables=["company_name", "search_results"],
            template='''
            You are an expert credit risk researcher. Review the following recent search results for the company "{company_name}".
            Extract and cluster into valid JSON format any actionable "Risk Alerts". 
            Examples: MCA filings issues, sector headwinds, recent litigation, management changes, negative news.
            
            Return ONLY a valid JSON object with the following structure:
            {{
                "overall_sentiment": "Positive" | "Neutral" | "Negative",
                "risk_alerts": [
                    {{
                        "category": "String (e.g., Regulatory, Financial, Legal)",
                        "description": "String (Brief explanation of the risk)",
                        "severity": "Low" | "Medium" | "High"
                    }}
                ],
                "positive_indicators": ["String"]
            }}

            Search Results Context:
            {search_results}
            '''
        )

    def search_company(self, company_name: str) -> dict:
        """
        Uses DuckDuckGo to search for recent news/info about the company and uses LLM to summarize risks.
        """
        search_results = ""
        try:
            # Construct a targeted search query
            query = f"{company_name} financial news OR controversies OR MCA filings OR regulatory issues"
            search_results = self.search.invoke(query)
        except Exception as e:
            print(f"DuckDuckGo Search error (likely rate limit): {e}")
            search_results = "No recent search results available due to rate limiting or search error."

        try:
            if not search_results or len(str(search_results)) < 50:
                 search_results = "No distinct search results found. Base the risk alerts on general knowledge of the company if possible, or state that realtime data is unavailable."
            
            # Use LLM to summarize based on results or general knowledge if results failed
            chain = self.summarize_prompt | self.llm
            response = chain.invoke({"company_name": company_name, "search_results": search_results})
            
            content = response.content
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
                
            return json.loads(content.strip())
            
        except Exception as e:
            print(f"Researcher LLM error: {e}")
            return {"error": "Failed to research company", "details": str(e)}
