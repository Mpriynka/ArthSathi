import logging
from backend.rag.vector_store import get_vector_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chillar_seedhi.seed_kb")

def seed_database():
    vector_store = get_vector_store()
    
    documents = [
        # Level 0 documents
        "Daily Money Tracking: To protect yourself, write down every single rupee that comes in and goes out today. Separate ₹20 to ₹50 in a separate small container. This is your shield against unexpected small troubles.",
        "Avoiding Debt Traps: Never take quick loans from unverified mobile apps or local lenders. They charge very high interest rates (often 100%+ per year) and use threatening behavior. Always ask a local bank first.",
        "Emergency Cash Envelope: Set aside ₹10-₹20 every day in a physical paper envelope or a separate bank account. Label it 'Emergency'. Do not touch this cash unless it is a life-or-death scenario.",
        
        # Level 1 documents
        "Daily Savings Streak: Saving is like a muscle. Even if you save only ₹10 today, keeping a daily habit is what makes it strong. Log your savings daily to build a visual streak on your calendar.",
        "Goal Pockets: Divide your savings into distinct visual jars or 'goal pockets' (e.g. 'School Fees', 'Emergency Jar'). Labeling your money keeps you motivated and prevents you from spending it on daily impulses.",
        "Micro-savings: If you get daily or weekly wages, save a small fraction immediately. Even saving 5% of weekly earnings can help you build a cushion for weeks when there is no work.",
        
        # Level 2 documents
        "Emergency Fund Building: An emergency fund is cash saved to pay for food, rent, and medical bills if you lose your job or cannot work. For freelancers and gig workers, aim to build a buffer of 3 months of essential expenses.",
        "Basic Health Insurance: A single illness can wipe out all your savings and push you into debt. Look for government health schemes like Ayushman Bharat (PM-JAY) or low-cost micro-insurance plans starting at ₹300 per year.",
        "Liquidity Buffer: Keep your emergency fund in a bank account that lets you withdraw money instantly. Do not tie up emergency money in fixed deposits or assets that take days to sell.",
        
        # Level 3 documents
        "Understanding Loan Costs: Before signing any loan paper, look at the Total EMI and calculate the total amount you will pay back. Often, a small loan of ₹5,000 can cost ₹8,000 in just a few months due to hidden fees.",
        "Prioritizing Debt (Snowball vs. Avalanche): If you have multiple loans, list them all. The Avalanche method focuses on paying off the loan with the highest interest rate first to save money. The Snowball method pays off the smallest loan first to give you a quick win.",
        "Avoiding Debt Consolidation Traps: Be careful of agencies that offer to merge all your loans into one. Often they charge high fees and extend your loan duration, costing you more in the long run. Speak directly with your bank.",
        
        # Level 4 documents
        "Public Provident Fund (PPF): PPF is a government-run savings scheme in India that is 100% safe. Your money earns guaranteed tax-free interest and is locked for 15 years, making it perfect for retirement or child education.",
        "Systematic Investment Plan (SIP): An SIP is a method where you invest a fixed amount (e.g., ₹500) every month into a mutual fund. It helps you grow wealth over 5-10 years by buying stocks, but it has market risks.",
        "Recurring Deposit (RD): An RD is a safe bank product where you deposit a fixed sum monthly (e.g. ₹1000) for a fixed term (1-5 years) and earn guaranteed interest. Unlike mutual funds, there is zero risk of losing money.",
        
        # Level 5 documents
        "Retirement Corpus Planning: As a stable high-earning professional, calculate how much money you need to maintain your lifestyle after retirement. Build a corpus using low-cost index funds, PPF, and NPS.",
        "Portfolio Diversification: Do not put all your eggs in one basket. Divide your savings across equity mutual funds (for growth), fixed deposits/gold (for stability), and high-yield savings (for emergency needs).",
        "Tax Planning and Wealth: Maximize tax-saving investments under Section 80C and 80D using PPF, ELSS mutual funds, and health insurance premiums to legally reduce your tax burden while growing wealth."
    ]
    
    metadatas = [
        # Level 0
        {"source": "SEBI Guidelines", "seedhiLevels": [0], "persona": ["daily_wage", "irregular"], "category": "basics"},
        {"source": "RBI Safety Guide", "seedhiLevels": [0], "persona": ["daily_wage", "irregular", "weekly"], "category": "debt"},
        {"source": "ChillarSeedhi Coach", "seedhiLevels": [0], "persona": ["daily_wage", "irregular"], "category": "savings"},
        
        # Level 1
        {"source": "ChillarSeedhi Coach", "seedhiLevels": [1], "persona": ["daily_wage", "weekly", "monthly_salaried"], "category": "savings"},
        {"source": "SEBI Guidelines", "seedhiLevels": [1], "persona": ["daily_wage", "weekly"], "category": "goals"},
        {"source": "Financial Literacy Council", "seedhiLevels": [1], "persona": ["weekly", "irregular"], "category": "basics"},
        
        # Level 2
        {"source": "Financial Literacy Council", "seedhiLevels": [2], "persona": ["irregular", "weekly"], "category": "emergency"},
        {"source": "IRDAI Guide", "seedhiLevels": [2], "persona": ["irregular", "weekly", "monthly_salaried"], "category": "insurance"},
        {"source": "RBI Safety Guide", "seedhiLevels": [2], "persona": ["irregular", "weekly"], "category": "liquidity"},
        
        # Level 3
        {"source": "RBI Consumer Protection", "seedhiLevels": [3], "persona": ["irregular", "weekly", "monthly_salaried"], "category": "debt"},
        {"source": "ChillarSeedhi Coach", "seedhiLevels": [3], "persona": ["irregular", "monthly_salaried"], "category": "debt"},
        {"source": "RBI Consumer Protection", "seedhiLevels": [3], "persona": ["irregular", "weekly"], "category": "debt"},
        
        # Level 4
        {"source": "Post Office Savings Scheme Guide", "seedhiLevels": [4], "persona": ["monthly_salaried"], "category": "savings"},
        {"source": "AMFI Mutual Fund Guide", "seedhiLevels": [4], "persona": ["monthly_salaried"], "category": "investments"},
        {"source": "Post Office Savings Scheme Guide", "seedhiLevels": [4], "persona": ["weekly", "monthly_salaried"], "category": "savings"},
        
        # Level 5
        {"source": "AMFI Mutual Fund Guide", "seedhiLevels": [5], "persona": ["monthly_salaried"], "category": "wealth"},
        {"source": "SEBI Guidelines", "seedhiLevels": [5], "persona": ["monthly_salaried"], "category": "wealth"},
        {"source": "Income Tax Department India", "seedhiLevels": [5], "persona": ["monthly_salaried"], "category": "taxes"}
    ]
    
    logger.info("Starting knowledge base seeding...")
    vector_store.add_documents(documents, metadatas)
    logger.info("Knowledge base seeding complete.")

if __name__ == "__main__":
    seed_database()
