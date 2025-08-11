# 🏥 Medical AI Suite: Clinical Trial Screener & Lab Report Analyzer

An AI-powered healthcare platform that uses **LangGraph** agents, **PyPDF**, and **Groq (Llama 3.1)** to bridge the gap between complex medical data and actionable patient insights. 

<div align="center">
  <br>
  <a href="https://clinical-trial-screener-divyansh.streamlit.app">
    <img src="https://img.shields.io/badge/Try_the_Project-Live_Demo-0d9488?style=for-the-badge&logo=streamlit&logoColor=white" alt="Try Live Demo">
  </a>
  <br><br>
</div>

This platform contains **two highly advanced, distinct applications** packaged into a single seamless dashboard:

### 1. 🧬 Clinical Trial Screener
Instantly cross-references unstructured patient medical profiles against the **ClinicalTrials.gov API** (400,000+ active studies).
* **Information Extraction:** Parses free-text patient profiles (conditions, age, medications) into structured JSON.
* **Geographic Filtering:** Seamlessly filters recruiting trials globally or in specific countries (US, UK, India, Canada, etc.).
* **Automated Evaluation:** Analyzes thousands of words of dense trial eligibility criteria to calculate a precise "Match Score" (0-100%).
* **Actionable Reports:** Generates professional referral letters to help patients enroll.

### 2. 📄 Lab Report Analyzer
A highly empathetic AI tool that translates confusing PDF lab results into plain English.
* **PDF OCR Pipeline:** Uses `pypdf` and NLP to scrape unstructured text directly from medical checkups.
* **Biomarker Structuring:** Identifies distinct biomarkers (e.g., LDL, Vitamin D, AST/ALT) and evaluates them against reference ranges to flag them as Normal, High, or Low.
* **Patient-Centric Explanations:** Explains what each abnormal value means for the human body and offers simple lifestyle tips.

---

## 🏗️ Technical Architecture

```text
               [ STREAMLIT FRONTEND ]
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
[ 1. Trial Screener ]              [ 2. Lab Analyzer ]
        │                                 │
  LangGraph Agent                   PyPDF Extraction
        │                                 │
  ClinicalTrials.gov API            JSON Biomarker Map
        │                                 │
  Groq (Llama 3.1 8B)               Groq (Llama 3.1 8B)
        │                                 │
   Match Scoring &                  Plain English
   Evaluation logic                 Explanation logic
```

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **Agent Framework** | LangGraph, LangChain |
| **Large Language Model** | Groq API (Llama 3.1 8B Instant) |
| **Data Orchestration** | ClinicalTrials.gov API v2, PyPDF |
| **Frontend UI** | Streamlit, Custom HTML/CSS |
| **Deployment** | Streamlit Cloud, GitHub Actions |

## 📦 Installation

```bash
git clone https://github.com/oldregime/clinical-trial-screener.git
cd clinical-trial-screener
pip install -r requirements.txt
```

## 🔧 Configuration

Set your Groq API key (You can also set a secondary key to enable automatic failover if the primary key hits a rate limit):
```bash
export GROQ_API_KEY="your_primary_key_here"
export GROQ_API_KEY_SECONDARY="your_backup_key_here"
```

*Note: You can also just enter your API key directly into the app's sidebar when it launches.*

## 🚀 Run Locally

```bash
streamlit run app.py
```

## ⚠️ Disclaimer

This tool is for **informational and educational purposes only**. It is not a substitute for professional medical advice. Always consult with healthcare professionals for clinical trial enrollment or health diagnosis decisions.

## 📄 License

MIT License
