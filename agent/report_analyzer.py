import json
import os
from langchain_groq import ChatGroq

EXTRACT_PROMPT = """You are a highly precise medical data extraction AI. Extract all lab test results, biomarkers, and vitals from the following medical checkup report text.

Return ONLY a valid JSON list of objects. Each object MUST have these exact keys:
- "test_name": string (e.g., "Hemoglobin", "LDL Cholesterol")
- "result_value": string or number (e.g., "14.2", "Negative")
- "unit": string (e.g., "g/dL", "mg/dL", leave empty string if none)
- "reference_range": string (e.g., "13.0 - 17.0", leave empty string if none)
- "status": string (MUST be exactly "Normal", "High", or "Low". Infer this based on the reference range if not explicitly stated as 'H' or 'L'.)

If the text contains no lab results, return an empty list: []
Return ONLY the raw JSON array. Do not wrap in markdown fences.

Medical Report Text:
{text}
"""

EXPLAIN_PROMPT = """You are an empathetic, knowledgeable health assistant. You are speaking directly to the patient ("You").
Review these extracted lab results:

{json_results}

Write a simple, plain English summary of what these results mean for a normal person checking their 6-month health report.
Follow this structure:
1. **The Good News:** Group and briefly mention the normal results. (e.g., "Great news, your Liver function, kidney function, and blood sugar are completely normal.")
2. **Areas to Watch (High/Low):** For any result marked "High" or "Low", explain in simple terms what that biomarker does in the body, why it might be out of range, and general lifestyle/dietary suggestions (e.g., "Your Vitamin D is low, which is common in winter. Try getting more sunlight or eating fortified foods.")
3. **Medical Disclaimer:** End with a strong but polite disclaimer that this is an AI analysis and they should consult their doctor for clinical decisions.

Use clean markdown formatting with bullet points and bold text for readability. Do not provide medical diagnoses.
"""

def get_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=os.environ.get("GROQ_API_KEY"),
        temperature=0.1,
    )

def analyze_lab_report(text: str) -> dict:
    llm = get_llm()
    
    # Step 1: Extract structured JSON
    extract_msg = llm.invoke(EXTRACT_PROMPT.format(text=text))
    raw_json = extract_msg.content.strip()
    
    # Use regex to find the JSON array anywhere in the text
    import re
    match = re.search(r'\[.*\]', raw_json, re.DOTALL)
    if match:
        clean_json = match.group(0)
    else:
        clean_json = raw_json
        
    try:
        biomarkers = json.loads(clean_json)
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e} \nRaw output: {raw_json}")
        biomarkers = []

    # Step 2: Generate plain English explanation
    if not biomarkers:
        explanation = "I couldn't detect any structured lab results in the uploaded text. Please ensure the document is a medical checkup report."
    else:
        explain_msg = llm.invoke(EXPLAIN_PROMPT.format(json_results=json.dumps(biomarkers, indent=2)))
        explanation = explain_msg.content

    return {
        "biomarkers": biomarkers,
        "explanation": explanation
    }
