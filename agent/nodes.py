import json
import os
from langchain_groq import ChatGroq
from .state import AgentState, PatientData, TrialMatch
from .prompts import PARSE_PATIENT_PROMPT, ANALYZE_ELIGIBILITY_PROMPT, GENERATE_REPORT_PROMPT
from utils.clinicaltrials import search_trials

def get_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=os.environ.get("GROQ_API_KEY"),
        temperature=0.1,
    )

def parse_patient(state: AgentState) -> AgentState:
    """Parse free-text patient profile into structured data."""
    try:
        llm = get_llm()
        prompt = PARSE_PATIENT_PROMPT.format(patient_input=state["patient_input"])
        response = llm.invoke(prompt)
        text = response.content.strip()
        # Clean markdown fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        parsed = json.loads(text)
        # Build search query from conditions
        conditions = parsed.get("conditions", [])
        search_query = " OR ".join(conditions[:3]) if conditions else state["patient_input"][:100]
        return {
            **state,
            "parsed_patient": parsed,
            "search_query": search_query,
            "status": "Patient profile parsed successfully",
        }
    except Exception as e:
        return {**state, "error": f"Failed to parse patient profile: {str(e)}", "status": "error"}

def search_clinical_trials(state: AgentState) -> AgentState:
    """Search ClinicalTrials.gov for relevant trials."""
    if state.get("error"):
        return state
    try:
        query = state.get("search_query", "")
        country = state.get("country_filter", "Global")
        trials = search_trials(query, max_results=10, country=country)
        if not trials:
            return {**state, "raw_trials": [], "status": "No trials found for the given conditions"}
        return {**state, "raw_trials": trials, "status": f"Found {len(trials)} potentially relevant trials"}
    except Exception as e:
        return {**state, "error": f"Failed to search trials: {str(e)}", "status": "error"}

def analyze_eligibility(state: AgentState) -> AgentState:
    """Analyze patient eligibility for each trial."""
    if state.get("error") or not state.get("raw_trials"):
        return {**state, "trial_matches": [], "status": state.get("status", "No trials to analyze")}
    try:
        llm = get_llm()
        patient = state["parsed_patient"]
        matches = []
        for trial in state["raw_trials"][:5]:  # Limit to 5 to stay within rate limits
            prompt = ANALYZE_ELIGIBILITY_PROMPT.format(
                age=patient.get("age", "Unknown"),
                sex=patient.get("sex", "Unknown"),
                conditions=", ".join(patient.get("conditions", [])),
                medications=", ".join(patient.get("medications", [])),
                lab_values=json.dumps(patient.get("lab_values", {})),
                medical_history=", ".join(patient.get("medical_history", [])),
                trial_title=trial.get("title", ""),
                nct_id=trial.get("nct_id", ""),
                phase=trial.get("phase", "N/A"),
                trial_conditions=", ".join(trial.get("conditions", [])),
                eligibility_criteria=trial.get("eligibility_criteria", "Not available")[:2000],
            )
            response = llm.invoke(prompt)
            text = response.content.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
                text = text.rsplit("```", 1)[0]
            try:
                analysis = json.loads(text)
            except json.JSONDecodeError:
                analysis = {"match_score": 50, "match_reasoning": text}

            match = TrialMatch(
                nct_id=trial.get("nct_id", ""),
                title=trial.get("title", ""),
                status=trial.get("status", ""),
                phase=trial.get("phase", ""),
                conditions=trial.get("conditions", []),
                eligibility_criteria=trial.get("eligibility_criteria", "")[:500],
                match_score=analysis.get("match_score", 0),
                match_reasoning=analysis.get("match_reasoning", ""),
                locations=trial.get("locations", [])[:3],
                url=f"https://clinicaltrials.gov/study/{trial.get('nct_id', '')}",
            )
            matches.append(match)

        # Sort by match score descending
        matches.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        return {**state, "trial_matches": matches, "status": f"Analyzed eligibility for {len(matches)} trials"}
    except Exception as e:
        return {**state, "error": f"Failed to analyze eligibility: {str(e)}", "status": "error"}

def generate_report(state: AgentState) -> AgentState:
    """Generate a final professional report."""
    if state.get("error"):
        return state
    matches = state.get("trial_matches", [])
    if not matches:
        return {**state, "final_report": "No matching clinical trials were found for the given patient profile. Consider broadening the search criteria or consulting with a clinical trial coordinator.", "status": "complete"}
    try:
        llm = get_llm()
        patient = state["parsed_patient"]
        trials_summary = ""
        for m in matches:
            trials_summary += f"\n---\nTrial: {m.get('title', '')} ({m.get('nct_id', '')})\n"
            trials_summary += f"Phase: {m.get('phase', 'N/A')} | Status: {m.get('status', '')}\n"
            trials_summary += f"Match Score: {m.get('match_score', 0)}/100\n"
            trials_summary += f"Reasoning: {m.get('match_reasoning', '')}\n"

        prompt = GENERATE_REPORT_PROMPT.format(
            age=patient.get("age", "Unknown"),
            sex=patient.get("sex", "Unknown"),
            conditions=", ".join(patient.get("conditions", [])),
            medications=", ".join(patient.get("medications", [])),
            trials_summary=trials_summary,
        )
        response = llm.invoke(prompt)
        return {**state, "final_report": response.content, "status": "complete"}
    except Exception as e:
        return {**state, "error": f"Failed to generate report: {str(e)}", "status": "error"}
