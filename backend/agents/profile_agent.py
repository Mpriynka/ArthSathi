import json
import logging
from typing import Dict, Any
from groq import Groq
from backend.config import settings

logger = logging.getLogger("chillar_seedhi.profile_agent")

class ProfileAgent:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"

    def extract_profile(self, user_input: str) -> Dict[str, Any]:
        """
        Uses Groq API with JSON mode to extract a structured financial profile 
        from raw conversational text or structured form input strings.
        """
        system_prompt = """
        You are the Profile Agent of ChillarSeedhi. Your role is to analyze a user's verbal or written description of their financial situation and extract a structured profile.

        You MUST output a single valid JSON object containing the following keys:
        - name: (string, default "Guest")
        - language: (string, default "English", language they are speaking/writing in or prefer)
        - incomePattern: (string, "daily_wage" / "weekly" / "monthly_salaried" / "irregular")
        - expenseFrequency: (string, "daily" / "weekly" / "monthly")
        - riskTolerance: (string, "low" / "moderate" / "high")
        - monthlyIncome: (integer, estimate of monthly income in INR. If daily wage, multiply daily wage by active work days, e.g., 20 days. Default: 0)
        - urgentExpenses: (integer, estimate of urgent recurring or monthly expenses in INR. Default: 0)
        - savingsHabit: (string, "regular" / "irregular" / "none")
        - emergencyFundStatus: (string, "none" / "partial" / "complete")
        - debtStatus: (string, "none" / "low_pressure" / "emi_stressed")
        - primaryGoal: (string, "daily_survival" / "emergency" / "education" / "debt_free" / "home" / "retirement" / "wealth_growth")
        
        Reasoning guidelines for scores (on a scale of 0 to 100):
        - readinessScore: Score indicating financial preparedness. High (70+) if they have regular savings, low debt, stable income, and complete/partial emergency fund. Low (<40) if they live hand-to-mouth or are heavily debt stressed.
        - riskScore: Vulnerability to financial shocks. High (60+) if income is irregular/seasonal, savings are none/irregular, or they have no emergency fund.
        - urgencyScore: Current stress/danger levels. High (70+) if they are EMI-stressed, have immediate loan traps, or urgent unpaid expenses.
        
        Level Assignment Matrix:
        - Level 0 (Survival Map): Monthly income is low (<20k), highly irregular flow, no savings, main goal is daily survival.
        - Level 1 (First Savings Habit): Income 15k-30k, low/semi-regular, irregular/no savings, no immediate high-debt stress.
        - Level 2 (Safety Net): Income 20k-45k, variable income, irregular savings, wants to build emergency fund/buffer.
        - Level 3 (Debt Safety & Protection): Stressed by informal/formal loans or high EMI pressure.
        - Level 4 (Formal Savings & Goal Planning): Stable monthly income 25k-80k, low debt pressure, ready for formal savings (PPF, RD, SIP, basic insurance).
        - Level 5 (Financial Stability & Wealth Growth): Stable high income (60k+), has safety nets, seeks retirement/wealth growth.
        
        Calculate:
        - readinessScore: (integer, 0 to 100)
        - riskScore: (integer, 0 to 100)
        - urgencyScore: (integer, 0 to 100)
        - seedhiLevel: (integer, 0 to 5, the assigned capability level based on the matrix)

        Return ONLY the raw JSON object. Do not include markdown formatting or extra text.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"User Financial Description:\n{user_input}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result_json = response.choices[0].message.content
            parsed = json.loads(result_json)
            
            # Post-processing/Validation to ensure all keys exist and have safe default fallbacks
            return {
                "name": parsed.get("name", "Guest"),
                "language": parsed.get("language", "English"),
                "incomePattern": parsed.get("incomePattern", "irregular"),
                "expenseFrequency": parsed.get("expenseFrequency", "daily"),
                "riskTolerance": parsed.get("riskTolerance", "low"),
                "monthlyIncome": int(parsed.get("monthlyIncome", 0)),
                "urgentExpenses": int(parsed.get("urgentExpenses", 0)),
                "savingsHabit": parsed.get("savingsHabit", "none"),
                "emergencyFundStatus": parsed.get("emergencyFundStatus", "none"),
                "debtStatus": parsed.get("debtStatus", "none"),
                "primaryGoal": parsed.get("primaryGoal", "daily_survival"),
                "readinessScore": max(0, min(100, int(parsed.get("readinessScore", 10)))),
                "riskScore": max(0, min(100, int(parsed.get("riskScore", 80)))),
                "urgencyScore": max(0, min(100, int(parsed.get("urgencyScore", 50)))),
                "seedhiLevel": max(0, min(5, int(parsed.get("seedhiLevel", 0))))
            }
        except Exception as e:
            logger.error(f"Error in ProfileAgent extraction: {e}")
            # Safe basic rule-based default fallback
            return {
                "name": "Guest",
                "language": "English",
                "incomePattern": "irregular",
                "expenseFrequency": "daily",
                "riskTolerance": "low",
                "monthlyIncome": 10000,
                "urgentExpenses": 6000,
                "savingsHabit": "none",
                "emergencyFundStatus": "none",
                "debtStatus": "none",
                "primaryGoal": "daily_survival",
                "readinessScore": 30,
                "riskScore": 75,
                "urgencyScore": 40,
                "seedhiLevel": 0
            }
