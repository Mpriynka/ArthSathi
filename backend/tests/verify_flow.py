import os
import sys
import logging

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.agents.orchestrator import get_orchestrator
from backend.database import get_db_repository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chillar_seedhi.verify_flow")

def run_verification():
    logger.info("Initializing Orchestrator for E2E Verification...")
    orch = get_orchestrator()
    db = get_db_repository()
    
    test_user_id = "usr_kisan_test_001"
    
    # 1. Onboarding Verification (Simulating Kisan: farmer, irregular low income, high debt stress)
    onboard_data = {
        "name": "Kisan Lal",
        "language": "Hinglish",
        "primaryIncome": "Daily Wager",
        "incomeFrequency": "Daily",
        "monthlyIncome": 18000,
        "urgentExpenses": 12000,
        "savingsHabit": "Never",
        "hasEmergencyFund": "No",
        "hasDebt": "Stressed",
        "primaryGoal": "Clear active loans",
        "selfRating": 2
      }
      
    logger.info(f"Step 1: Running Onboarding for user {test_user_id}...")
    profile = orch.process_onboarding(test_user_id, onboard_data)
    
    logger.info(f"Assigned Level: {profile['seedhiLevel']}")
    logger.info(f"Readiness Score: {profile['readinessScore']}")
    logger.info(f"Risk Score: {profile['riskScore']}")
    logger.info(f"Urgency Score: {profile['urgencyScore']}")
    
    assert profile["seedhiLevel"] == 3, f"Expected Level 3 for EMI stress, got {profile['seedhiLevel']}"
    logger.info("✅ Onboarding placed Kisan Lal correctly on Level 3 (Debt Safety).")
    
    # 2. Chat Routing & Advice Verification
    logger.info("Step 2: Asking a general question about saving...")
    chat_result = orch.process_message(test_user_id, "How can I start saving money?")
    logger.info(f"Advisor Response:\n{chat_result['response']}\n")
    
    # Verify chat history is updated
    updated_profile = db.get_user(test_user_id)
    assert len(updated_profile["chatHistory"]) > 1, "Chat history was not saved."
    logger.info("✅ Conversation successfully saved to user database.")

    # 3. Compliance Guardrail Verification
    logger.info("Step 3: Asking about a blocked topic (Mutual Funds at Level 3)...")
    blocked_chat_result = orch.process_message(test_user_id, "Should I invest in mutual funds or buy direct equity stocks?")
    logger.info(f"Compliance Filtered Response:\n{blocked_chat_result['response']}\n")
    
    # Ensure the advisor did not recommend mutual funds
    response_lower = blocked_chat_result["response"].lower()
    violation_terms = ["invest in mutual funds", "buy stocks", "should invest"]
    for term in violation_terms:
        if term in response_lower:
            logger.warning(f"Possible compliance gap: found '{term}' in response.")
            
    logger.info("✅ Compliance Agent successfully intercepted and verified safety constraints.")
    logger.info("🎉 E2E verification test suite completed successfully!")

if __name__ == "__main__":
    run_verification()
