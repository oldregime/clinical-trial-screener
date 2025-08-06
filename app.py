import streamlit as st
import os
import time

# Page config
st.set_page_config(
    page_title="Clinical Trial Screener",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Minimalist, modern SaaS styling
st.markdown("""
<style>
    /* Base typography and colors */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #111827;
    }
    
    /* Clean header */
    .header-container {
        padding-top: 1rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 2rem;
    }
    .header-title {
        font-size: 2rem;
        font-weight: 600;
        letter-spacing: -0.025em;
        color: #111827;
        margin: 0;
        padding: 0;
    }
    .header-subtitle {
        color: #6b7280;
        font-size: 1rem;
        margin-top: 0.25rem;
        font-weight: 400;
    }

    /* Cards and Data Display */
    .data-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #6b7280;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    .data-value {
        font-size: 0.95rem;
        color: #111827;
        margin-bottom: 1rem;
    }

    /* Expander override for cleaner look */
    div[data-testid="stExpander"] {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        background-color: white;
    }
    div[data-testid="stExpander"] > summary {
        padding: 1rem;
    }
    div[data-testid="stExpander"] > summary:hover {
        background-color: #f9fafb;
    }
    
    /* Score styling */
    .score-indicator {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    .score-high { background-color: #d1fae5; color: #065f46; }
    .score-med { background-color: #fef3c7; color: #92400e; }
    .score-low { background-color: #fee2e2; color: #991b1b; }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def get_score_class(score):
    if score >= 70: return "score-high"
    if score >= 40: return "score-med"
    return "score-low"


def main():
    # Header
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">Clinical Trial Screener</h1>
        <div class="header-subtitle">Automated eligibility analysis against ClinicalTrials.gov</div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar Settings
    with st.sidebar:
        st.markdown("### Settings")
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            api_key = st.text_input("Groq API Key", type="password")
            if api_key:
                os.environ["GROQ_API_KEY"] = api_key
        else:
            st.caption("API Key configured.")
            
        st.markdown("---")
        st.caption("Powered by Llama 3.3 and LangGraph")

    # Main layout
    col_input, col_results = st.columns([1, 1.2], gap="large")

    with col_input:
        st.markdown("### Patient Profile")
        
        examples = {
            "Custom Input...": "",
            "Oncology: Breast Cancer": "45-year-old female diagnosed with HER2-positive breast cancer, stage II. Completed 4 cycles of AC-T chemotherapy. Currently on Trastuzumab maintenance therapy. ECOG performance status 1. No significant cardiac history. Previous surgical history includes lumpectomy with clear margins.",
            "Endocrinology: Type 2 Diabetes": "58-year-old male with Type 2 Diabetes Mellitus diagnosed 5 years ago. Currently on Metformin 1000mg twice daily and Sitagliptin 100mg daily. Recent HbA1c of 7.8%. BMI 32. History of hypertension controlled with Lisinopril 10mg. No history of cardiovascular events. Non-smoker.",
            "Neurology: Alzheimer's": "72-year-old female with early-stage Alzheimer's disease, diagnosed 18 months ago. MMSE score 22. Currently on Donepezil 10mg daily. History of well-controlled hypertension and hyperlipidemia. No history of stroke or seizures. Lives independently with spouse. Non-diabetic.",
        }
        
        selected = st.selectbox("Load Example", options=list(examples.keys()), label_visibility="collapsed")
        
        patient_input = st.text_area(
            "Clinical Notes",
            value=examples.get(selected, ""),
            height=250,
            placeholder="Paste raw clinical notes or patient history here...",
            label_visibility="collapsed"
        )

        run_button = st.button("Run Eligibility Screen", type="primary", use_container_width=True)

    # Process and display results
    if run_button:
        if not patient_input.strip():
            st.error("Please provide a patient profile.")
            return
        if not os.environ.get("GROQ_API_KEY"):
            st.error("API Key missing. Please configure it in the sidebar.")
            return

        from agent.graph import run_agent

        with col_results:
            st.markdown("### Analysis")
            
            # Progress handling
            status_placeholder = st.empty()
            with status_placeholder.container():
                st.caption("Initializing analysis pipeline...")
                progress = st.progress(0)
                
                time.sleep(0.3)
                progress.progress(25)
                st.caption("Extracting clinical entities...")
                
                time.sleep(0.3)
                progress.progress(50)
                st.caption("Querying clinicaltrials.gov...")
                
                time.sleep(0.3)
                progress.progress(75)
                st.caption("Running LLM eligibility evaluation...")

            try:
                result = run_agent(patient_input)
                
                status_placeholder.empty()

                if result.get("error"):
                    st.error(f"Analysis failed: {result['error']}")
                    return

                # Parsed Patient Summary
                patient = result.get("parsed_patient", {})
                st.markdown("#### Extracted Clinical Profile")
                
                p1, p2 = st.columns(2)
                with p1:
                    st.markdown(f"<div class='data-label'>Demographics</div><div class='data-value'>{patient.get('age', '--')} yr {patient.get('sex', '--')}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='data-label'>Conditions</div><div class='data-value'>{', '.join(patient.get('conditions', [])) or '--'}</div>", unsafe_allow_html=True)
                with p2:
                    st.markdown(f"<div class='data-label'>Medications</div><div class='data-value'>{', '.join(patient.get('medications', [])) or '--'}</div>", unsafe_allow_html=True)
                
                st.markdown("---")

                # Match Results
                matches = result.get("trial_matches", [])
                st.markdown(f"#### Identified Trials ({len(matches)})")
                
                if not matches:
                    st.info("No matching recruiting trials found for this clinical profile.")
                else:
                    for i, match in enumerate(matches):
                        score = match.get("match_score", 0)
                        score_class = get_score_class(score)
                        title = match.get('title', 'Unknown Trial')
                        nct = match.get('nct_id', '')
                        
                        # Custom expander title showing score clearly
                        with st.expander(f"{title}", expanded=(i == 0)):
                            st.markdown(f"""
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                                <div>
                                    <div class="data-label">Identifier</div>
                                    <a href="{match.get('url', '#')}" target="_blank" style="text-decoration: none; color: #0d9488; font-weight: 500;">{nct}</a>
                                </div>
                                <div class="score-indicator {score_class}">Match Score: {score}/100</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown("<div class='data-label'>Phase / Status</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='data-value'>{match.get('phase', '--')} • {match.get('status', '--')}</div>", unsafe_allow_html=True)

                            st.markdown("<div class='data-label'>Eligibility Assessment</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='data-value' style='color: #4b5563; font-size: 0.9rem;'>{match.get('match_reasoning', '--')}</div>", unsafe_allow_html=True)

                # Report download or text
                report = result.get("final_report", "")
                if report:
                    st.markdown("---")
                    st.markdown("#### Clinical Summary Report")
                    st.markdown(f"<div style='font-size: 0.9rem; color: #374151; line-height: 1.6;'>{report}</div>", unsafe_allow_html=True)

            except Exception as e:
                status_placeholder.empty()
                st.error("An unexpected error occurred during execution.")
                with st.expander("View Error Trace"):
                    import traceback
                    st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
