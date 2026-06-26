import json
import logging
from groq import Groq
from backend.config import settings

logger = logging.getLogger("chillar_seedhi.compliance_agent")

class ComplianceAgent:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"

    def verify_advice(self, user_profile: dict, advice: str) -> str:
        """
        Inspects advice to ensure no blocked financial topics for the user's 
        current Seedhi Level are recommended. If a violation is found, it overrides 
        or rewrites the text.
        """
        level = user_profile.get("seedhiLevel", 0)
        level_details = settings.LEVEL_INFO.get(level, settings.LEVEL_INFO[0])
        
        blocked_topics = level_details.get("blocked_topics", [])
        if not blocked_topics:
            return advice

        system_prompt = f"""
        You are the Compliance and Safety Agent of ChillarSeedhi. Your role is to enforce financial advice guardrails.
        The user is at Level {level}: {level_details['name']}.
        
        At this level, the following topics are STRICTLY FORBIDDEN/BLOCKED: {", ".join(blocked_topics)}.
        The advisor MUST NOT suggest, explain, or refer the user to these topics.
        
        Review the proposed financial advice. 
        Determine if it violates the safety rule.
        
        You must output a JSON object with:
        - "is_compliant": (boolean, true if no blocked topics are recommended, false otherwise)
        - "revised_advice": (string, if compliant, return the original advice verbatim. If NOT compliant, return a sanitized version of the advice that completely removes any reference to the forbidden topics and redirects the user's focus back to Level {level} goals: {level_details['description']})

        Return ONLY the raw JSON object. Do not include markdown formatting or extra text.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Proposed Financial Advice:\n{advice}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result_json = response.choices[0].message.content
            parsed = json.loads(result_json)
            
            if not parsed.get("is_compliant", True):
                logger.warning(f"Compliance violation detected for Level {level}. Sanitizing advice.")
                return parsed.get("revised_advice", advice)
            
            return advice
        except Exception as e:
            logger.error(f"Error in ComplianceAgent: {e}")
            # Safe python-level check fallback
            for topic in blocked_topics:
                if topic.lower() in advice.lower():
                    logger.warning(f"Python fallback triggered: Blocked topic '{topic}' found in advice. Overriding.")
                    return f"At Level {level} ({level_details['name']}), we focus exclusively on building a safe foundation like: {', '.join(level_details['allowed_topics'])}. Let's work on this step before discussing other options."
            return advice
