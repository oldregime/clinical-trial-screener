import os
from agent.report_analyzer import analyze_lab_report
import pypdf

file_path = r"Y:\from w11\jobsearch\700026281 -   MANOHAR LAL JOSHI-2604021120 (1).pdf"
reader = pypdf.PdfReader(file_path)
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"

print("Sending text to LLM...")
res = analyze_lab_report(text[:10000]) # just test the first 10k chars to ensure it doesn't timeout
print("BIOMARKERS FOUND:", len(res['biomarkers']))
if not res['biomarkers']:
    print("FAILED TO EXTRACT.")
