import logging
from datetime import datetime
from typing import Dict, Any, List, TypedDict
from langgraph.graph import StateGraph, END

from backend.config import settings
from backend.database import get_db_repository, get_default_user_profile
from backend.rag.vector_store import get_vector_store

from backend.agents.profile_agent import ProfileAgent
from backend.agents.advisor_agent import AdvisorAgent
from backend.agents.teaching_agent import TeachingAgent
from backend.agents.compliance_agent import ComplianceAgent
from backend.agents.routing_agent import RoutingAgent

logger = logging.getLogger("chillar_seedhi.langgraph_orchestrator")

# 1. Define LangGraph State Schema
class AgentState(TypedDict):
    user_id: str
    messages: List[Dict[str, Any]]
    user_profile: Dict[str, Any]
    current_query: str
    target_agent: str
    intent: str
    requires_rag: bool
    search_keywords: str
    rag_context: str
    proposed_response: str
    final_response: str

# Initialize Agent Classes
profile_agent = ProfileAgent()
advisor_agent = AdvisorAgent()
teaching_agent = TeachingAgent()
compliance_agent = ComplianceAgent()
routing_agent = RoutingAgent()

# 2. Define Nodes

def route_query_node(state: AgentState) -> Dict[str, Any]:
    """Node: Classifies user intent and routes to correct agent."""
    query = state["current_query"]
    route = routing_agent.route_query(query)
    logger.info(f"LangGraph Route: {route['target_agent']} (intent: {route['intent']})")
    return {
        "target_agent": route["target_agent"],
        "intent": route["intent"],
        "requires_rag": route["requires_rag"],
        "search_keywords": route["search_keywords"]
    }

def retrieve_context_node(state: AgentState) -> Dict[str, Any]:
    """Node: Queries Qdrant vector database (or fallback) for RAG context."""
    rag_context = ""
    if state.get("requires_rag") and state.get("search_keywords"):
        user_profile = state["user_profile"]
        vector_store = get_vector_store()
        search_results = vector_store.query(
            text_query=state["search_keywords"],
            limit=2,
            level=user_profile["seedhiLevel"],
            persona_type=user_profile["persona"]["incomePattern"]
        )
        if search_results:
            rag_context = "\n\n".join([
                f"[Document Source: {res['metadata'].get('source', 'Unknown')}]\n{res['content']}"
                for res in search_results
            ])
            logger.info(f"LangGraph RAG: Retrieved {len(search_results)} relevant document(s)")
            
    return {"rag_context": rag_context}

def profile_updater_node(state: AgentState) -> Dict[str, Any]:
    """Node: Processes updates to financial profile and handles level progression."""
    user_profile = state["user_profile"]
    query = state["current_query"]
    
    # Extract updated details
    updated_data = profile_agent.extract_profile(query)
    
    # Merge values
    for key in ["monthlyIncome", "urgentExpenses", "savingsHabit", "emergencyFundStatus", "debtStatus"]:
        if updated_data.get(key) not in [None, 0, "none"]:
            user_profile[key] = updated_data[key]
            
    user_profile["readinessScore"] = updated_data.get("readinessScore", user_profile["readinessScore"])
    user_profile["riskScore"] = updated_data.get("riskScore", user_profile["riskScore"])
    user_profile["urgencyScore"] = updated_data.get("urgencyScore", user_profile["urgencyScore"])
    
    # Check for level up
    old_level = user_profile.get("seedhiLevel", 0)
    new_level = updated_data.get("seedhiLevel", old_level)
    
    level_changed = False
    if new_level != old_level:
        user_profile["seedhiLevel"] = new_level
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        user_profile["levelHistory"].append({"level": new_level, "achievedOn": today_str})
        level_changed = True
        
    level_name = settings.LEVEL_INFO[new_level]["name"]
    
    if level_changed:
        proposed = (
            f"Asha! I have updated your profile based on our conversation. "
            f"Congratulations! You have moved from Level {old_level} to **Level {new_level}: {level_name}**. "
            "I have updated your dashboard tools. Let's start with your new focus!"
        )
    else:
        proposed = (
            f"Asha! I have recorded those updates in your profile and adjusted your metrics. "
            f"You are currently at Level {new_level}: {level_name}."
        )
        
    return {"proposed_response": proposed, "user_profile": user_profile}

def teaching_node(state: AgentState) -> Dict[str, Any]:
    """Node: Explains financial terms in local language without jargon."""
    proposed = teaching_agent.explain_concept(
        user_profile=state["user_profile"],
        concept_query=state["current_query"],
        rag_context=state["rag_context"]
    )
    return {"proposed_response": proposed}

def advisor_node(state: AgentState) -> Dict[str, Any]:
    """Node: Generates level-appropriate suggestions."""
    proposed = advisor_agent.generate_advice(
        user_profile=state["user_profile"],
        chat_history=state["messages"],
        query=state["current_query"],
        rag_context=state["rag_context"]
    )
    return {"proposed_response": proposed}

def compliance_node(state: AgentState) -> Dict[str, Any]:
    """Node: Verifies proposed advice against safety guardrails and commits updates to DB."""
    user_profile = state["user_profile"]
    proposed = state["proposed_response"]
    
    # Run safety checks
    final = compliance_agent.verify_advice(user_profile, proposed)
    
    # Append to chat history in state
    user_profile["chatHistory"].append({"role": "user", "content": state["current_query"]})
    user_profile["chatHistory"].append({"role": "assistant", "content": final})
    
    # Keep history bounded to 30 messages
    if len(user_profile["chatHistory"]) > 30:
        user_profile["chatHistory"] = user_profile["chatHistory"][-30:]
        
    user_profile["lastActive"] = datetime.utcnow().isoformat() + "Z"
    
    # Save back to DB
    db = get_db_repository()
    db.save_user(state["user_id"], user_profile)
    logger.info(f"LangGraph Compliance: Completed and saved state for user {state['user_id']}")
    
    return {"final_response": final, "user_profile": user_profile}

# 3. Define Router Conditional Routing Logic
def select_agent_route(state: AgentState) -> str:
    target = state.get("target_agent", "advisor")
    if target == "profile":
        return "profile_node"
    elif target == "teaching":
        return "teaching_node"
    else:
        return "advisor_node"

# 4. Compile the LangGraph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("route_query", route_query_node)
workflow.add_node("retrieve_context", retrieve_context_node)
workflow.add_node("profile_node", profile_updater_node)
workflow.add_node("teaching_node", teaching_node)
workflow.add_node("advisor_node", advisor_node)
workflow.add_node("compliance_node", compliance_node)

# Set Entry Point and Edges
workflow.set_entry_point("route_query")
workflow.add_edge("route_query", "retrieve_context")

# Add Dynamic Conditional Routing
workflow.add_conditional_edges(
    "retrieve_context",
    select_agent_route,
    {
        "profile_node": "profile_node",
        "teaching_node": "teaching_node",
        "advisor_node": "advisor_node"
    }
)

# Connect back to compliance check
workflow.add_edge("profile_node", "compliance_node")
workflow.add_edge("teaching_node", "compliance_node")
workflow.add_edge("advisor_node", "compliance_node")
workflow.add_edge("compliance_node", END)

# Compile Workflow
compiled_graph = workflow.compile()
logger.info("Compiled LangGraph multi-agent state workflow.")
