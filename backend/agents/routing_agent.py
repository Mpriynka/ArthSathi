import json
import logging
from groq import Groq
from backend.config import settings

logger = logging.getLogger("chillar_seedhi.routing_agent")

class RoutingAgent:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"

    def route_query(self, query: str) -> dict:
        """
        Classifies the user input to route it to the correct agent and determine 
        if RAG lookup is required.
        """
        system_prompt = """
        You are the Knowledge Routing Agent of ChillarSeedhi. Your role is to classify the user's input.
        
        You must output a single JSON object with these keys:
        - "intent": (string, one of: "onboard_update", "explain_concept", "financial_advice", "daily_tracker", "general_chat")
          - "onboard_update": User is describing their jobs, income, expenses, debts, or wanting to update their profile parameters.
          - "explain_concept": User is asking "What is X?", "Explain X", "how does Y work?", or asking about general financial terms (like PPF, SIP, Emergency funds, interest rates).
          - "financial_advice": User is asking what they should do next, how to manage their money, or seeking guidance for their situation.
          - "daily_tracker": User wants to log a transaction, daily expense, income, or view their tracker.
          - "general_chat": User is saying hello, greeting you, or general chatter.
        - "target_agent": (string, "profile" for onboard_update, "teaching" for explain_concept, "advisor" for financial_advice/daily_tracker, "general" for general_chat)
        - "requires_rag": (boolean, true if they ask about specific financial products like PPF, RD, mutual funds, insurance, or SEBI rules, false otherwise)
        - "search_keywords": (string, search terms to send to the vector database if requires_rag is true, otherwise empty string "")
        
        Return ONLY the raw JSON object. Do not include markdown formatting or extra text.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"User Message: {query}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result_json = response.choices[0].message.content
            parsed = json.loads(result_json)
            
            return {
                "intent": parsed.get("intent", "general_chat"),
                "target_agent": parsed.get("target_agent", "general"),
                "requires_rag": bool(parsed.get("requires_rag", False)),
                "search_keywords": parsed.get("search_keywords", "")
            }
        except Exception as e:
            logger.error(f"Error in RoutingAgent: {e}")
            # Safe defaults
            return {
                "intent": "financial_advice",
                "target_agent": "advisor",
                "requires_rag": False,
                "search_keywords": ""
            }
        
