import os
import pdfplumber
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

class IngestorService:
    def __init__(self):
        # We use gemini-1.5-pro for reliable data extraction
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=api_key)
        
        self.extraction_prompt = PromptTemplate(
            input_variables=["text"],
            template='''
            You are an expert credit analyst. Extract the following information from the provided text snippet of a financial document.
            Return ONLY a valid JSON object with the following keys. If information is missing, use null.
            Keys:
            - "company_name": String
            - "total_revenue": Number or String
            - "net_profit": Number or String
            - "key_covenants": List of Strings (financial or negative covenants mentioned)
            - "identified_risks": List of Strings (any potential risks, lawsuits, or issues)

            Text Snippet:
            {text}
            '''
        )

    def _extract_text_from_pdf(self, file_path: str) -> str:
        text_content = []
        try:
            with pdfplumber.open(file_path) as pdf:
                # Limit to first 10 pages for hackathon performance
                for page in pdf.pages[:10]:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
            return "\n".join(text_content)
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            raise Exception("Failed to parse PDF document")

    def parse_pdf(self, file_path: str) -> dict:
        """
        Extracts text from PDF and sends it to LLM to extract structured data.
        """
        raw_text = self._extract_text_from_pdf(file_path)
        
        if not raw_text.strip():
            return {"error": "No text could be extracted from the PDF."}
        
        # In a real app, we'd chunk this. For hackathon, we send a large block to Gemini.
        try:
            chain = self.extraction_prompt | self.llm
            # Cut text if it's too huge, Gemini 1.5 Pro has 1M context but we want speed
            # Let's take first 50000 characters
            prompt_input = raw_text[:50000]
            
            response = chain.invoke({"text": prompt_input})
            
            # Basic cleanup if LLM returns markdown formatting
            content = response.content
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
                
            return json.loads(content.strip())
        except Exception as e:
            print(f"LLM Extraction error: {e}")
            # Fallback
            return {"raw_text_preview": raw_text[:1000], "error": "LLM failed to parse structure"}
