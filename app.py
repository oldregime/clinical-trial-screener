import streamlit as st
import os
import time

# Page config
st.set_page_config(
    page_title="Clinical Trial Eligibility Screener",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for premium look
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
    }
    .trial-card {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1.2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .score-high { color: #28a745; font-weight: bold; font-size: 1.3em; }
    .score-medium { color: #ffc107; font-weight: bold; font-size: 1.3em; }
    .score-low { color: #dc3545; font-weight: bold; font-size: 1.3em; }
    .status-badge {
        display: inline-block;
        padding: 0.25em 0.6em;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 600;
    }
    .badge-recruiting { background: #d4edda; color: #155724; }
    .badge-phase { background: #cce5ff; color: #004085; }
    .tech-badge {
        display: inline-block;
        background: #e9ecef;
        padding: 0.2em 0.5em;
        border-radius: 4px;
        font-size: 0.8em;
        margin: 0.1em;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


def get_score_class(score):
    if score >= 70:
        return "score-high"
    elif score >= 40:
        return "score-medium"
    return "score-low"


def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏥 Clinical Trial Eligibility Screener</h1>
        <p style="font-size: 1.1em; opacity: 0.9;">AI-powered patient-to-trial matching using LangGraph agents and real-time ClinicalTrials.gov data</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # API Key handling
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            api_key = st.text_input("Groq API Key", type="password", help="Get a free key at console.groq.com")
            if api_key:
                os.environ["GROQ_API_KEY"] = api_key
        else:
            st.success("✅ API Key configured")
        
        st.markdown("---")
        st.markdown("### 🏗️ Architecture")
        st.markdown("""
        ```
        Patient Input
            │
            ▼
        ┌─────────────────┐
        │  Parse Patient  │ ← Llama 3 70B
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │  Search Trials   │ ← ClinicalTrials.gov
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Analyze Match    │ ← Llama 3 70B
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Generate Report  │ ← Llama 3 70B
        └─────────────────┘
        ```
        """)
        
        st.markdown("---")
        st.markdown("### 🛠️ Tech Stack")
        techs = ["LangGraph", "LangChain", "Groq Llama 3 70B", "ClinicalTrials.gov API", "Streamlit", "Python"]
        for t in techs:
            st.markdown(f'<span class="tech-badge">{t}</span>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📊 How It Works")
        st.markdown("""
        1. **Input** a patient profile in natural language
        2. **AI parses** structured data (age, conditions, meds)
        3. **Searches** ClinicalTrials.gov for recruiting trials
        4. **Analyzes** eligibility criteria per trial
        5. **Ranks** matches with reasoning
        """)

    # Main content
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 📝 Patient Profile")
        
        # Example profiles
        examples = {
            "Select an example...": "",
            "Type 2 Diabetes Patient": "58-year-old male with Type 2 Diabetes Mellitus diagnosed 5 years ago. Currently on Metformin 1000mg twice daily and Sitagliptin 100mg daily. Recent HbA1c of 7.8%. BMI 32. History of hypertension controlled with Lisinopril 10mg. No history of cardiovascular events. Non-smoker.",
            "Breast Cancer Patient": "45-year-old female diagnosed with HER2-positive breast cancer, stage II. Completed 4 cycles of AC-T chemotherapy. Currently on Trastuzumab maintenance therapy. ECOG performance status 1. No significant cardiac history. Previous surgical history includes lumpectomy with clear margins.",
            "Alzheimer's Patient": "72-year-old female with early-stage Alzheimer's disease, diagnosed 18 months ago. MMSE score 22. Currently on Donepezil 10mg daily. History of well-controlled hypertension and hyperlipidemia. No history of stroke or seizures. Lives independently with spouse. Non-diabetic.",
        }
        
        selected = st.selectbox("Quick examples:", options=list(examples.keys()))
        
        default_text = examples.get(selected, "")
        patient_input = st.text_area(
            "Enter patient profile (free text):",
            value=default_text,
            height=200,
            placeholder="e.g., 55-year-old male with Type 2 Diabetes, currently on Metformin 1000mg, HbA1c 7.5%, BMI 31, no cardiac history...",
        )

        run_button = st.button("🔍 Screen for Clinical Trials", type="primary", use_container_width=True)

    with col2:
        st.markdown("### 📊 Agent Pipeline Status")
        status_container = st.container()

    # Run agent
    if run_button:
        if not patient_input.strip():
            st.error("Please enter a patient profile.")
            return
        if not os.environ.get("GROQ_API_KEY"):
            st.error("Please configure your Groq API key in the sidebar.")
            return

        from agent.graph import run_agent

        with col2:
            with status_container:
                steps = [
                    ("🧬 Parsing patient profile...", 0.25),
                    ("🔍 Searching ClinicalTrials.gov...", 0.50),
                    ("🧪 Analyzing eligibility criteria...", 0.75),
                    ("📋 Generating report...", 0.90),
                ]
                progress_bar = st.progress(0, text="Starting agent pipeline...")
                status_text = st.empty()

                for step_text, progress in steps:
                    progress_bar.progress(progress, text=step_text)
                    status_text.info(step_text)
                    time.sleep(0.5)

        try:
            result = run_agent(patient_input)

            with col2:
                progress_bar.progress(1.0, text="✅ Analysis complete!")
                status_text.success("Pipeline completed successfully!")

            if result.get("error"):
                st.error(f"❌ Error: {result['error']}")
                return

            # Display parsed patient
            st.markdown("---")
            st.markdown("### 🧬 Parsed Patient Profile")
            patient = result.get("parsed_patient", {})
            pcol1, pcol2, pcol3 = st.columns(3)
            with pcol1:
                st.metric("Age", patient.get("age", "N/A"))
                st.metric("Sex", patient.get("sex", "N/A"))
            with pcol2:
                st.markdown("**Conditions:**")
                for c in patient.get("conditions", []):
                    st.markdown(f"- {c}")
            with pcol3:
                st.markdown("**Medications:**")
                for m in patient.get("medications", []):
                    st.markdown(f"- {m}")

            # Display trial matches
            matches = result.get("trial_matches", [])
            if matches:
                st.markdown("---")
                st.markdown(f"### 🏥 Matched Clinical Trials ({len(matches)} found)")
                
                for i, match in enumerate(matches):
                    score = match.get("match_score", 0)
                    score_class = get_score_class(score)
                    
                    with st.expander(f"{'🟢' if score >= 70 else '🟡' if score >= 40 else '🔴'} {match.get('title', 'Unknown Trial')} — Score: {score}/100", expanded=(i < 3)):
                        mcol1, mcol2 = st.columns([2, 1])
                        with mcol1:
                            st.markdown(f"**NCT ID:** [{match.get('nct_id', '')}]({match.get('url', '')})")
                            st.markdown(f"**Phase:** {match.get('phase', 'N/A')}")
                            st.markdown(f"**Status:** {match.get('status', '')}")
                            if match.get("conditions"):
                                st.markdown(f"**Conditions:** {', '.join(match['conditions'])}")
                            if match.get("locations"):
                                st.markdown(f"**Locations:** {', '.join(match['locations'][:3])}")
                        with mcol2:
                            st.markdown(f'<div class="{score_class}">Match Score: {score}/100</div>', unsafe_allow_html=True)
                        
                        st.markdown("**AI Reasoning:**")
                        st.info(match.get("match_reasoning", "No reasoning available"))
                        
                        if match.get("eligibility_criteria"):
                            st.markdown("**Eligibility Criteria (excerpt):**")
                            st.text(match["eligibility_criteria"][:500])

            # Display report
            report = result.get("final_report", "")
            if report:
                st.markdown("---")
                st.markdown("### 📋 Clinical Trial Matching Report")
                st.markdown(report)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6c757d; font-size: 0.85em;">
        <p>⚠️ <strong>Disclaimer:</strong> This tool is for informational purposes only. Always consult with healthcare professionals for clinical trial eligibility decisions.</p>
        <p>Built with LangGraph • LangChain • Groq Llama 3 • ClinicalTrials.gov API</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
