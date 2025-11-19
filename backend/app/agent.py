"""
LangGraph agent for analyzing support tickets
"""
import logging
import os
from typing import TypedDict, List, Dict, Any
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from app.database import Ticket

logger = logging.getLogger(__name__)

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not set. Agent will use mock responses.")


class AgentState(TypedDict):
    """State for the LangGraph agent"""
    tickets: List[Ticket]
    analysis_results: List[Dict[str, Any]]
    summary: str
    run_id: int


def analyze_single_ticket(ticket: Ticket, llm: ChatOpenAI) -> Dict[str, Any]:
    """
    Analyze a single ticket to determine category, priority, and notes.
    
    Args:
        ticket: Ticket object to analyze
        llm: Language model instance
        
    Returns:
        Dictionary with category, priority, and notes
    """
    prompt = f"""Analyze the following support ticket and provide:
1. Category (choose one: billing, bug, feature_request, account, technical, other)
2. Priority (choose one: low, medium, high, critical)
3. Brief notes explaining your reasoning

Ticket Title: {ticket.title}
Ticket Description: {ticket.description}

Respond in the following JSON format:
{{
    "category": "category_name",
    "priority": "priority_level",
    "notes": "brief explanation"
}}"""

    try:
        if OPENAI_API_KEY:
            messages = [
                SystemMessage(content="You are a support ticket analyst. Analyze tickets and provide structured responses in JSON format."),
                HumanMessage(content=prompt)
            ]
            response = llm.invoke(messages)
            content = response.content
            
            # Parse JSON from response (handle markdown code blocks if present)
            import json
            import re
            
            # Extract JSON from markdown code blocks if present
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            
            result = json.loads(content)
            
            # Validate and normalize category
            valid_categories = ["billing", "bug", "feature_request", "account", "technical", "other"]
            category = result.get("category", "other").lower()
            if category not in valid_categories:
                category = "other"
            
            # Validate and normalize priority
            valid_priorities = ["low", "medium", "high", "critical"]
            priority = result.get("priority", "medium").lower()
            if priority not in valid_priorities:
                priority = "medium"
            
            return {
                "category": category,
                "priority": priority,
                "notes": result.get("notes", "").strip()
            }
        else:
            # Mock response when API key is not available
            logger.warning("Using mock analysis (OPENAI_API_KEY not set)")
            return mock_analyze_ticket(ticket)
            
    except Exception as e:
        logger.error(f"Error analyzing ticket {ticket.id}: {e}")
        # Fallback to mock analysis on error
        return mock_analyze_ticket(ticket)


def mock_analyze_ticket(ticket: Ticket) -> Dict[str, Any]:
    """
    Mock analysis function for when OpenAI API is not available.
    Uses simple keyword matching.
    """
    title_lower = ticket.title.lower()
    desc_lower = ticket.description.lower()
    text = f"{title_lower} {desc_lower}"
    
    # Determine category
    if any(word in text for word in ["billing", "charge", "payment", "refund", "invoice", "subscription"]):
        category = "billing"
    elif any(word in text for word in ["bug", "crash", "error", "broken", "not working", "issue"]):
        category = "bug"
    elif any(word in text for word in ["feature", "request", "add", "would like", "suggest"]):
        category = "feature_request"
    elif any(word in text for word in ["login", "account", "access", "password", "authentication"]):
        category = "account"
    elif any(word in text for word in ["technical", "server", "api", "integration"]):
        category = "technical"
    else:
        category = "other"
    
    # Determine priority
    if any(word in text for word in ["critical", "urgent", "immediately", "emergency", "data loss"]):
        priority = "critical"
    elif any(word in text for word in ["high", "important", "asap", "soon"]):
        priority = "high"
    elif any(word in text for word in ["low", "minor", "whenever"]):
        priority = "low"
    else:
        priority = "medium"
    
    notes = f"Auto-categorized as {category} with {priority} priority based on keywords."
    
    return {
        "category": category,
        "priority": priority,
        "notes": notes
    }


def analyze_tickets_node(state: AgentState) -> AgentState:
    """
    Node that analyzes all tickets using the LLM.
    """
    logger.info(f"Analyzing {len(state['tickets'])} tickets")
    
    # Initialize LLM if API key is available
    llm = None
    if OPENAI_API_KEY:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            api_key=OPENAI_API_KEY
        )
    
    analysis_results = []
    for ticket in state['tickets']:
        result = analyze_single_ticket(ticket, llm)
        analysis_results.append({
            "ticket_id": ticket.id,
            "category": result["category"],
            "priority": result["priority"],
            "notes": result["notes"]
        })
    
    state['analysis_results'] = analysis_results
    return state


def generate_summary_node(state: AgentState) -> AgentState:
    """
    Node that generates an overall summary of the analysis.
    """
    logger.info("Generating analysis summary")
    
    if not state['analysis_results']:
        state['summary'] = "No tickets analyzed."
        return state
    
    # Count categories and priorities
    category_counts = {}
    priority_counts = {}
    
    for result in state['analysis_results']:
        category = result['category']
        priority = result['priority']
        category_counts[category] = category_counts.get(category, 0) + 1
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    # Generate summary
    total_tickets = len(state['analysis_results'])
    critical_count = priority_counts.get('critical', 0)
    high_count = priority_counts.get('high', 0)
    
    summary_parts = [
        f"Analyzed {total_tickets} ticket(s).",
        f"Categories: {', '.join(f'{k}({v})' for k, v in category_counts.items())}.",
        f"Priorities: {', '.join(f'{k}({v})' for k, v in priority_counts.items())}."
    ]
    
    if critical_count > 0 or high_count > 0:
        summary_parts.append(f"⚠️ {critical_count + high_count} ticket(s) require immediate attention.")
    
    state['summary'] = " ".join(summary_parts)
    return state


def create_analysis_graph() -> StateGraph:
    """
    Create and configure the LangGraph state graph.
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("analyze_tickets", analyze_tickets_node)
    workflow.add_node("generate_summary", generate_summary_node)
    
    # Define the flow
    workflow.set_entry_point("analyze_tickets")
    workflow.add_edge("analyze_tickets", "generate_summary")
    workflow.add_edge("generate_summary", END)
    
    return workflow.compile()


async def analyze_tickets_with_agent(
    tickets: List[Ticket],
    run_id: int
) -> Dict[str, Any]:
    """
    Main function to analyze tickets using LangGraph agent.
    
    Args:
        tickets: List of Ticket objects to analyze
        run_id: ID of the analysis run
        
    Returns:
        Dictionary with:
            - analysis_results: List of analysis results per ticket
            - summary: Overall summary string
    """
    logger.info(f"Starting LangGraph agent analysis for {len(tickets)} tickets")
    
    # Initialize state
    initial_state: AgentState = {
        "tickets": tickets,
        "analysis_results": [],
        "summary": "",
        "run_id": run_id
    }
    
    # Create and run the graph
    graph = create_analysis_graph()
    final_state = graph.invoke(initial_state)
    
    logger.info(f"Analysis complete. Summary: {final_state['summary']}")
    
    return {
        "analysis_results": final_state['analysis_results'],
        "summary": final_state['summary']
    }

