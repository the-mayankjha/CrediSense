import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

class EngineService:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=api_key)
        
        self.cam_prompt = PromptTemplate(
            input_variables=["company_data", "research_data", "primary_insights"],
            template='''
            You are an expert Chief Risk Officer for a corporate lending institution.
            Generate a concise but comprehensive Credit Appraisal Memo (CAM) based on the following inputs.
            Address the 5 Cs of Credit (Character, Capacity, Capital, Collateral, Conditions).
            
            Company Data (from uploaded docs/financials):
            {company_data}
            
            Research Agent Data (Risk Alerts & News):
            {research_data}
            
            Primary Insights (Credit Officer Notes):
            {primary_insights}
            
            Return ONLY a valid JSON object with the following structure:
            {{
                "overall_decision": "Approve" | "Reject" | "Hold",
                "suggested_limit_cr": "Number (in Crores)",
                "interest_rate_premium_bps": "Number",
                "explainable_logic": "String (Detailed narrative justification for the decision)",
                "five_cs_summary": {{
                    "character": "String",
                    "capacity": "String",
                    "capital": "String",
                    "collateral": "String",
                    "conditions": "String"
                }},
                "key_risk_mitigants": ["String"]
            }}
            '''
        )

    def generate_cam(self, company_data: dict, research_data: dict, primary_insights: str) -> dict:
        """
        Aggregates data and generates the CAM using Gemini.
        """
        try:
            chain = self.cam_prompt | self.llm
            
            # Serialize dicts to string for prompt
            response = chain.invoke({
                "company_data": json.dumps(company_data, indent=2),
                "research_data": json.dumps(research_data, indent=2),
                "primary_insights": primary_insights
            })
            
            content = response.content
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
                
            return json.loads(content.strip())
            
        except Exception as e:
            print(f"Engine error: {e}")
            return {"error": "Failed to generate CAM", "details": str(e)}
