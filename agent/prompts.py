PARSE_PATIENT_PROMPT = """You are a clinical data extraction specialist. Extract structured patient information from the following free-text patient profile.

Return a JSON object with these fields:
- age (integer)
- sex (string: "Male", "Female", or "Unknown")
- conditions (list of medical conditions/diagnoses)
- medications (list of current medications)
- lab_values (dict of lab test names to values, e.g. {{"HbA1c": "7.2%"}})
- medical_history (list of past medical events, surgeries, etc.)

If a field is not mentioned, use an empty list/dict or null.

Patient Profile:
{patient_input}

Return ONLY valid JSON, no markdown fences."""

ANALYZE_ELIGIBILITY_PROMPT = """You are a clinical trial eligibility analyst. Given a patient profile and a clinical trial's eligibility criteria, determine how well the patient matches.

Patient Profile:
- Age: {age}
- Sex: {sex}
- Conditions: {conditions}
- Medications: {medications}
- Lab Values: {lab_values}
- Medical History: {medical_history}

Clinical Trial: {trial_title} ({nct_id})
Phase: {phase}
Conditions Studied: {trial_conditions}

Eligibility Criteria:
{eligibility_criteria}

Analyze the patient's eligibility. Return a JSON object with:
- match_score: integer 0-100 (0 = definitely ineligible, 100 = perfect match)
- match_reasoning: string explaining why the patient does or doesn't match, citing specific criteria

Consider inclusion AND exclusion criteria. If information is missing, note it but don't disqualify. Be realistic but generous.

Return ONLY valid JSON, no markdown fences."""

GENERATE_REPORT_PROMPT = """You are a medical informatics specialist. Generate a clear, professional report summarizing clinical trial matches for a patient.

Patient Summary:
- Age: {age}, Sex: {sex}
- Conditions: {conditions}
- Medications: {medications}

Matched Trials (sorted by match score):
{trials_summary}

Generate a professional clinical trial matching report with:
1. A brief patient summary
2. Top trial recommendations with clear reasoning
3. Important notes about next steps
4. A disclaimer about consulting healthcare providers

Use clear headings and bullet points. Be professional but readable."""
