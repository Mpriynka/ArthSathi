import logging
from groq import Groq
from backend.config import settings

logger = logging.getLogger("chillar_seedhi.teaching_agent")

class TeachingAgent:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"

    def explain_concept(self, user_profile: dict, concept_query: str, rag_context: str = "") -> str:
        """
        Explains complex financial terminology or systems without jargon,
        tailored to the user's preferred language and level.
        """
        language = user_profile.get("persona", {}).get("language", "English")
        user_name = user_profile.get("persona", {}).get("name", "Friend")
        level = user_profile.get("seedhiLevel", 0)

        system_prompt = f"""
        You are the Teaching Agent of ChillarSeedhi. Your job is to act as a friendly schoolteacher, explaining financial concepts to someone with zero financial background.
        
        Guidelines:
        1. Keep explanations completely jargon-free. If you must use a term (e.g. "Interest"), explain it immediately as "the rent the bank pays you for keeping your money there".
        2. Speak in the user's preferred language ({language}) (or Hinglish if applicable).
        3. Use visual analogies (e.g. jars, pockets, a shield against rain, a seed growing into a tree).
        4. Address the user ({user_name}) warmly.
        5. Limit the response to 3 short bullet points or a single paragraph.
        6. Reference their current level (Level {level}) to explain why this concept matters to them now, or if it is a level-up concept, explain what they need to achieve before starting it.
        
        RAG Knowledge context:
        {rag_context}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Explain this concept simply: {concept_query}"}
                ],
                temperature=0.2,
                max_tokens=600
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in TeachingAgent: {e}")
            return f"Namaste. Let's make this simple: {concept_query} is like a storage bin where you keep extra cash safe from rain. I'll explain more when our systems are fully online."
