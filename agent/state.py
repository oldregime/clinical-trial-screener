from typing import TypedDict, Optional


class PatientData(TypedDict, total=False):
    age: int
    sex: str
    conditions: list[str]
    medications: list[str]
    lab_values: dict
    medical_history: list[str]


class TrialMatch(TypedDict, total=False):
    nct_id: str
    title: str
    status: str
    phase: str
    conditions: list[str]
    eligibility_criteria: str
    match_score: int
    match_reasoning: str
    locations: list[str]
    url: str


class AgentState(TypedDict, total=False):
    patient_input: str
    parsed_patient: PatientData
    search_query: str
    raw_trials: list[dict]
    trial_matches: list[TrialMatch]
    final_report: str
    error: Optional[str]
    status: str
