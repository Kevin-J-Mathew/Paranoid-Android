from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END

from ..agents.requirements_agent import run_requirements_agent
from ..agents.test_generation_agent import run_test_generation_agent
from ..agents.test_execution_agent import run_test_execution_agent
from ..agents.regression_agent import run_regression_agent
from ..agents.report_agent import run_report_agent
from ..agents.knowledge_store_agent import run_knowledge_store_agent
from ..core.rag import get_rag_pipeline


class AgentState(TypedDict):
    """Complete state object passed between agents in the LangGraph."""
    run_id: str
    story_id: str
    story_text: str
    story_title: str
    story_type: str
    parsed_requirements: Dict[str, Any]
    rag_context: Dict[str, Any]
    generated_tests: List[Dict[str, Any]]
    execution_results: List[Dict[str, Any]]
    regression_analysis: Dict[str, Any]
    report_html: str
    report_path: str
    report_filename: str
    agent_steps: List[Dict[str, Any]]
    current_step: str
    errors: List[str]


def rag_query_node(state: AgentState) -> AgentState:
    """Standalone RAG query node between requirements and test generation."""
    from datetime import datetime

    step = {
        "agent_name": "RAG Knowledge Agent",
        "status": "running",
        "message": "Querying historical test knowledge and bug database...",
        "timestamp": datetime.utcnow().isoformat(),
    }
    state["agent_steps"].append(step)
    state["current_step"] = "rag_query"

    rag = get_rag_pipeline()
    story_text = state["story_text"]

    similar_tests = rag.query_similar_tests(story_text, n_results=5)
    similar_bugs = rag.query_similar_bugs(story_text, n_results=5)
    stats = rag.get_collection_stats()

    state["rag_context"] = {
        "similar_tests": similar_tests,
        "similar_bugs": similar_bugs,
        "knowledge_base_stats": stats
    }

    state["agent_steps"][-1]["status"] = "completed"
    state["agent_steps"][-1]["message"] = (
        f"Found {len(similar_tests)} similar tests and {len(similar_bugs)} related bugs "
        f"in knowledge base ({stats['test_cases']} total tests stored)"
    )
    state["agent_steps"][-1]["data"] = {
        "similar_tests_count": len(similar_tests),
        "similar_bugs_count": len(similar_bugs),
        "knowledge_stats": stats
    }
    return state


def build_sentinel_graph() -> StateGraph:
    """Construct the full LangGraph agent pipeline."""
    graph = StateGraph(AgentState)

    # Add all agent nodes
    graph.add_node("requirements_agent", run_requirements_agent)
    graph.add_node("rag_query_agent", rag_query_node)
    graph.add_node("test_generation_agent", run_test_generation_agent)
    graph.add_node("test_execution_agent", run_test_execution_agent)
    graph.add_node("regression_agent", run_regression_agent)
    graph.add_node("report_agent", run_report_agent)
    graph.add_node("knowledge_store_agent", run_knowledge_store_agent)

    # Define the flow
    graph.set_entry_point("requirements_agent")
    graph.add_edge("requirements_agent", "rag_query_agent")
    graph.add_edge("rag_query_agent", "test_generation_agent")
    graph.add_edge("test_generation_agent", "test_execution_agent")
    graph.add_edge("test_execution_agent", "regression_agent")
    graph.add_edge("regression_agent", "report_agent")
    graph.add_edge("report_agent", "knowledge_store_agent")
    graph.add_edge("knowledge_store_agent", END)

    return graph.compile()


# Singleton compiled graph
_compiled_graph = None


def get_compiled_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_sentinel_graph()
    return _compiled_graph
