import logging
from datetime import datetime
from typing import Dict, Any
from backend.config import settings
from backend.database import get_db_repository, get_default_user_profile
from backend.agents.profile_agent import ProfileAgent

logger = logging.getLogger("chillar_seedhi.orchestrator")

class Orchestrator:
    def __init__(self):
        self.profile_agent = ProfileAgent()
        self.db = get_db_repository()

    def process_onboarding(self, user_id: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes onboarding form responses, updates user profile, runs profile agent 
        to calculate financial metrics, and determines initial Seedhi Level.
        """
        user_profile = self.db.get_user(user_id)
        if not user_profile:
            user_profile = get_default_user_profile(user_id)
            
        form_text = "\n".join([f"{k}: {v}" for k, v in form_data.items()])
        extracted = self.profile_agent.extract_profile(form_text)
        
        user_profile["persona"]["name"] = form_data.get("name", extracted.get("name", "Guest User"))
        user_profile["persona"]["language"] = form_data.get("language", extracted.get("language", "English"))
        user_profile["persona"]["incomePattern"] = extracted.get("incomePattern", "irregular")
        user_profile["persona"]["expenseFrequency"] = extracted.get("expenseFrequency", "daily")
        user_profile["persona"]["riskTolerance"] = extracted.get("riskTolerance", "low")
        
        user_profile["monthlyIncome"] = extracted.get("monthlyIncome", 0)
        user_profile["urgentExpenses"] = extracted.get("urgentExpenses", 0)
        user_profile["savingsHabit"] = extracted.get("savingsHabit", "none")
        user_profile["emergencyFundStatus"] = extracted.get("emergencyFundStatus", "none")
        user_profile["debtStatus"] = extracted.get("debtStatus", "none")
        user_profile["primaryGoal"] = extracted.get("primaryGoal", "daily_survival")
        
        user_profile["readinessScore"] = extracted.get("readinessScore", 30)
        user_profile["riskScore"] = extracted.get("riskScore", 70)
        user_profile["urgencyScore"] = extracted.get("urgencyScore", 40)
        
        new_level = extracted.get("seedhiLevel", 0)
        user_profile["seedhiLevel"] = new_level
        
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        user_profile["levelHistory"] = [{"level": new_level, "achievedOn": today_str}]
        
        welcome_msg = (
            f"Namaste {user_profile['persona']['name']}! Welcome to Level {new_level}: "
            f"{settings.LEVEL_INFO[new_level]['name']}. I have analyzed your details and set up your dashboard. "
            "How can I help you take your next safe step today?"
        )
        user_profile["chatHistory"] = [
            {"role": "assistant", "content": welcome_msg}
        ]
        
        user_profile["lastActive"] = datetime.utcnow().isoformat() + "Z"
        
        self.db.save_user(user_id, user_profile)
        logger.info(f"Completed onboarding for user {user_id}. Assigned Level {new_level}")
        return user_profile

    def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """
        Runs the multi-agent chat process via the compiled LangGraph state workflow.
        """
        user_profile = self.db.get_user(user_id)
        if not user_profile:
            user_profile = get_default_user_profile(user_id)
            self.db.save_user(user_id, user_profile)

        # Build initial LangGraph State
        initial_state = {
            "user_id": user_id,
            "messages": user_profile.get("chatHistory", []),
            "user_profile": user_profile,
            "current_query": message,
            "target_agent": "",
            "intent": "",
            "requires_rag": False,
            "search_keywords": "",
            "rag_context": "",
            "proposed_response": "",
            "final_response": ""
        }

        # Run the compiled LangGraph state graph
        from backend.agents.langgraph_orchestrator import compiled_graph
        final_state = compiled_graph.invoke(initial_state)

        return {
            "response": final_state["final_response"],
            "profile": final_state["user_profile"],
            "intent": final_state["intent"]
        }

# Global Orchestrator instance
_orchestrator_instance = None

def get_orchestrator() -> Orchestrator:
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = Orchestrator()
    return _orchestrator_instance
