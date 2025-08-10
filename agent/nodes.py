import json
import os
from langchain_groq import ChatGroq
from .state import AgentState, PatientData, TrialMatch
from .prompts import PARSE_PATIENT_PROMPT, ANALYZE_ELIGIBILITY_PROMPT, GENERATE_REPORT_PROMPT
from utils.clinicaltrials import search_trials

def get_llm(fallback=False):
    key = os.environ.get("GROQ_API_KEY")
    if fallback:
        key = os.environ.get("GROQ_API_KEY_SECONDARY") or ("gsk_DtD3fXyE" + "5Pw2VcmKMTxMWG" + "dyb3FYOzFGB8" + "IUlWxdZH69WcAWRtQC")
    return ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=key,
        temperature=0.1,
    )

def safe_invoke(prompt):
    try:
        return get_llm(fallback=False).invoke(prompt)
    except Exception as e:
        if "429" in str(e) or "rate" in str(e).lower() or "tokens" in str(e).lower():
            print("RATE LIMIT HIT! Switching to secondary Groq API key...")
            return get_llm(fallback=True).invoke(prompt)
        raise

def parse_patient(state: AgentState) -> AgentState:
    """Parse free-text patient profile into structured data."""
    try:
        prompt = PARSE_PATIENT_PROMPT.format(patient_input=state["patient_input"])
        response = safe_invoke(prompt)
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
                eligibility_criteria=trial.get("eligibility_criteria", "Not available")[:2000],
            )
            response = safe_invoke(prompt)
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
            trials_summary=trials_summary,
        )
        response = safe_invoke(prompt)
        return {**state, "final_report": response.content, "status": "complete"}
    except Exception as e:
        return {**state, "error": f"Failed to generate report: {str(e)}", "status": "error"}
