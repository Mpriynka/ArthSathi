import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

class Settings(BaseSettings):
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    MONGO_URI: str = os.getenv("MONGO_URI", "")
    SQLITE_PATH: str = "chillar_seedhi.db"
    QDRANT_PATH: str = "./qdrant_db"
    PORT: int = 8000
    HOST: str = "127.0.0.1"  # Security: Always bind to 127.0.0.1 for local/testing

    # Level definition names and descriptions
    LEVEL_INFO: dict = {
        0: {
            "name": "Survival Map",
            "income_range": "₹8k - ₹20k",
            "description": "Daily or highly irregular cash flow. Needs basic money tracking, daily habits, and micro-savings (₹20-50/day).",
            "allowed_topics": ["daily money tracking", "saving tiny amounts", "protecting cash", "avoiding high interest informal loans"],
            "blocked_topics": ["mutual funds", "stocks", "PPF", "fixed deposits", "long-term retirement planning"]
        },
        1: {
            "name": "First Savings Habit",
            "income_range": "₹15k - ₹30k",
            "description": "Semi-regular low income. Needs consistency, visual goal pockets, and small savings streaks.",
            "allowed_topics": ["daily savings streak", "goal pockets", "saving jars", "saving for small objectives"],
            "blocked_topics": ["mutual funds", "stocks", "equity investments", "advanced tax-saving"]
        },
        2: {
            "name": "Safety Net",
            "income_range": "₹20k - ₹45k",
            "description": "Variable income (gig workers/freelancers). Needs emergency fund building, basic health insurance, and work-gap buffers.",
            "allowed_topics": ["emergency fund", "liquidity buffer", "basic health insurance", "saving for work gaps"],
            "blocked_topics": ["stock trading", "complex portfolio allocation", "illiquid asset investments"]
        },
        3: {
            "name": "Debt Safety & Protection",
            "income_range": "₹18k - ₹50k",
            "description": "Stressed by EMI or loans. Needs debt prioritization, loan cost education, and avoiding trap loan apps.",
            "allowed_topics": ["debt repayment", "loan interest costs", "EMI reduction", "debt snowball/avalanche", "avoiding debt traps"],
            "blocked_topics": ["investments in equity", "mutual funds", "discretionary long-term saving until debt is stabilized"]
        },
        4: {
            "name": "Formal Savings & Goal Planning",
            "income_range": "₹25k - ₹80k",
            "description": "Stable salary. Needs formal savings products: PPF, Recurring Deposit (RD), SIP, basic tax-saving, and life/health insurance.",
            "allowed_topics": ["PPF", "RD", "SIP", "mutual funds basics", "term insurance", "tax-saving (Section 80C)"],
            "blocked_topics": ["day trading", "options and derivatives", "cryptocurrency", "leveraged investments"]
        },
        5: {
            "name": "Financial Stability & Wealth Growth",
            "income_range": "₹60k - ₹2L+",
            "description": "Stable high-income professional. Needs long-term wealth growth, retirement corpus planning, and portfolio diversification.",
            "allowed_topics": ["equity mutual funds", "direct stocks", "retirement corpus planning", "portfolio diversification", "advanced insurance planning"],
            "blocked_topics": ["speculative crypto", "highly leveraged margin trading"]
        }
    }

settings = Settings()

if not settings.GROQ_API_KEY:
    raise ValueError("CRITICAL: GROQ_API_KEY environment variable is not set. Please add it to your .env file.")
