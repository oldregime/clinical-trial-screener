# 🏥 Clinical Trial Eligibility Screener

An AI-powered clinical trial matching system that uses **LangGraph** agents to screen patients against real-time **ClinicalTrials.gov** data.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://clinical-trial-screener.streamlit.app/)

## 🚀 What It Does

Input a patient profile in natural language, and the AI agent pipeline will:

1. **Parse** the patient profile into structured clinical data using Google Gemini
2. **Search** ClinicalTrials.gov for actively recruiting trials matching the patient's conditions
3. **Analyze** eligibility criteria for each trial against the patient's profile
4. **Rank** trials by match score with detailed reasoning
5. **Generate** a professional clinical trial matching report

## 🏗️ Architecture

```
Patient Input (Free Text)
        │
        ▼
┌──────────────────┐
│  Parse Patient   │ ← Google Gemini 2.0 Flash
│  (LangGraph Node)│   Extracts: age, sex, conditions,
└────────┬─────────┘   medications, lab values
         │
         ▼
┌──────────────────┐
│  Search Trials   │ ← ClinicalTrials.gov API v2
│  (LangGraph Node)│   Finds recruiting trials
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Analyze Match    │ ← Google Gemini 2.0 Flash
│ (LangGraph Node) │   Scores 0-100 per trial
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Generate Report  │ ← Google Gemini 2.0 Flash
│ (LangGraph Node) │   Professional summary
└──────────────────┘
```

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **Agent Framework** | LangGraph (stateful multi-step agent) |
| **LLM Orchestration** | LangChain |
| **LLM** | Google Gemini 2.0 Flash |
| **Data Source** | ClinicalTrials.gov API v2 (real-time, 400K+ trials) |
| **Frontend** | Streamlit |
| **Deployment** | Streamlit Cloud |

## 📦 Installation

```bash
git clone https://github.com/oldregime/clinical-trial-screener.git
cd clinical-trial-screener
pip install -r requirements.txt
```

## 🔧 Configuration

Set your Google Gemini API key:
```bash
export GOOGLE_API_KEY="your_key_here"
```

Or enter it in the app sidebar.

## 🚀 Run Locally

```bash
streamlit run app.py
```

## 📝 Example Patient Profiles

**Type 2 Diabetes:**
> 58-year-old male with Type 2 Diabetes Mellitus, on Metformin 1000mg, HbA1c 7.8%, BMI 32, controlled hypertension.

**Breast Cancer:**
> 45-year-old female with HER2-positive breast cancer stage II, completed AC-T chemo, on Trastuzumab maintenance.

## ⚠️ Disclaimer

This tool is for **informational and educational purposes only**. It is not a substitute for professional medical advice. Always consult with healthcare professionals for clinical trial eligibility decisions.

## 📄 License

MIT License
