import pypdf
import sys

file_path = r"Y:\from w11\jobsearch\700026281 -   MANOHAR LAL JOSHI-2604021120 (1).pdf"
try:
    reader = pypdf.PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    print("EXTRACTED TEXT LENGTH:", len(text.strip()))
    print("--- FIRST 500 CHARS ---")
    print(text.strip()[:500])
except Exception as e:
    print("ERROR:", e)
