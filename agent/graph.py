from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import parse_patient, search_clinical_trials, analyze_eligibility, generate_report

def build_graph():
    """Build the LangGraph agent workflow."""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("parse_patient", parse_patient)
    workflow.add_node("search_trials", search_clinical_trials)
    workflow.add_node("analyze_eligibility", analyze_eligibility)
    workflow.add_node("generate_report", generate_report)

    # Define edges
    workflow.set_entry_point("parse_patient")
    workflow.add_edge("parse_patient", "search_trials")
    workflow.add_edge("search_trials", "analyze_eligibility")
    workflow.add_edge("analyze_eligibility", "generate_report")
    workflow.add_edge("generate_report", END)

    return workflow.compile()

def run_agent(patient_input: str) -> AgentState:
    """Run the clinical trial screening agent."""
    graph = build_graph()
    initial_state = AgentState(
        patient_input=patient_input,
        parsed_patient={},
        search_query="",
        raw_trials=[],
        trial_matches=[],
        final_report="",
        error=None,
        status="Starting analysis...",
    )
    result = graph.invoke(initial_state)
    return result
