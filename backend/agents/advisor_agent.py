import logging
from groq import Groq
from backend.config import settings

logger = logging.getLogger("chillar_seedhi.advisor_agent")

class AdvisorAgent:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"

    def generate_advice(self, user_profile: dict, chat_history: list, query: str, rag_context: str = "") -> str:
        """
        Generates level-appropriate financial advice for the user based on their
        assigned Seedhi Level and persona. Employs strict level-based limits.
        """
        level = user_profile.get("seedhiLevel", 0)
        level_details = settings.LEVEL_INFO.get(level, settings.LEVEL_INFO[0])
        
        allowed_topics_str = ", ".join(level_details["allowed_topics"])
        blocked_topics_str = ", ".join(level_details["blocked_topics"])
        
        language = user_profile.get("persona", {}).get("language", "English")
        user_name = user_profile.get("persona", {}).get("name", "Friend")
        income_pattern = user_profile.get("persona", {}).get("incomePattern", "irregular")
        
        # Build conversational context
        messages = [
            {
                "role": "system",
                "content": f"""
                You are the Financial Advisor Agent of ChillarSeedhi, a warm, patient, and wise guide who helps users build financial readiness.
                The user is at Level {level}: {level_details['name']}.
                
                Level Guidelines:
                - Description: {level_details['description']}
                - Income Pattern: {income_pattern}
                - Allowed Topics to discuss: {allowed_topics_str}
                - BLOCKED Topics (DO NOT DISCUSS OR SUGGEST): {blocked_topics_str}
                
                Instructions:
                1. Speak in a simple, local-friendly tone. Speak in the user's preferred language ({language}). If they write in Hinglish (Hindi written in Latin script), reply in Hinglish.
                2. Address the user by their name ({user_name}) warmly.
                3. Use simple, real-life analogies (like storing grains in jars, saving drops of water, or avoiding quicksand).
                4. Limit your response to 2-3 short, clear paragraphs.
                5. Provide EXACTLY ONE safe, actionable next step that matches their current level.
                6. If the user asks about a BLOCKED topic (e.g. asking about stocks at Level 0), politely explain that before talking about {blocked_topics_str}, they need to secure their current step (e.g. Level {level} - {level_details['name']}) by building a steady foundation first.
                
                RAG Knowledge Base context (use this facts if relevant to answer the query, but do not make up facts outside this):
                {rag_context}
                """
            }
        ]
        
        # Append historical logs (up to 5 recent turns)
        for msg in chat_history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
            
        # Append current user query
        messages.append({"role": "user", "content": query})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in AdvisorAgent generate_advice: {e}")
            return f"Namaste {user_name}. I am having trouble connecting to my system. Please try again. For now, remember: take it one safe step at a time."
