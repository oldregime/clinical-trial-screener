import streamlit as st
import os
import time

st.set_page_config(page_title="Clinical Trial Screener", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #111827; }
    .header-container { padding-top: 1rem; padding-bottom: 1.5rem; border-bottom: 1px solid #e5e7eb; margin-bottom: 2rem; }
    .header-title { font-size: 2rem; font-weight: 600; letter-spacing: -0.025em; color: #111827; margin: 0; padding: 0; }
    .header-subtitle { color: #6b7280; font-size: 1rem; margin-top: 0.25rem; font-weight: 400; }
    .data-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #6b7280; font-weight: 600; margin-bottom: 0.25rem; }
    .data-value { font-size: 0.95rem; color: #111827; margin-bottom: 1rem; }
    
    div[data-testid="stExpander"] { border: 1px solid #e5e7eb; border-radius: 8px; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); background-color: white; margin-bottom: 1rem;}
    div[data-testid="stExpander"] > summary { padding: 1rem; font-weight: 600; color: #111827; }
    div[data-testid="stExpander"] > summary:hover { background-color: #f9fafb; }
    
    .footer-text { text-align: center; color: #9ca3af; font-size: 0.85rem; margin-top: 4rem; padding-top: 1rem; border-top: 1px solid #f3f4f6; }
    .apply-box { background-color: #f0fdfa; border: 1px solid #ccfbf1; padding: 1rem; border-radius: 6px; margin-top: 1rem; }
    .apply-box h5 { margin-top: 0; color: #0f766e; font-size: 0.9rem; margin-bottom: 0.5rem;}
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<div class="header-container"><h1 class="header-title">Clinical Trial Screener</h1><div class="header-subtitle">Automated eligibility analysis against ClinicalTrials.gov</div></div>', unsafe_allow_html=True)

    # Removed sidebar for cleaner UI

    col_input, col_results = st.columns([1, 1.3], gap="large")

    with col_input:
        st.markdown("### Patient Profile")
        examples = {
            "Custom Input...": "",
            "Oncology: Breast Cancer": "45-year-old female diagnosed with HER2-positive breast cancer, stage II. Completed 4 cycles of AC-T chemotherapy. Currently on Trastuzumab maintenance therapy. ECOG performance status 1. No significant cardiac history. Previous surgical history includes lumpectomy with clear margins.",
            "Endocrinology: Type 2 Diabetes": "58-year-old male with Type 2 Diabetes Mellitus diagnosed 5 years ago. Currently on Metformin 1000mg twice daily and Sitagliptin 100mg daily. Recent HbA1c of 7.8%. BMI 32. History of hypertension controlled with Lisinopril 10mg. No history of cardiovascular events. Non-smoker.",
            "Cardiology: Heart Failure": "68-year-old male with NYHA Class II Heart Failure with reduced Ejection Fraction (HFrEF). Recent echo shows LVEF of 35%. Currently prescribed Entresto 49/51mg twice daily, Carvedilol 12.5mg twice daily, and Spironolactone 25mg daily. History of myocardial infarction 3 years ago. Blood pressure stable at 118/75 mmHg. eGFR 55 mL/min.",
            "Oncology: Lung Cancer (NSCLC)": "62-year-old male with newly diagnosed Stage III Non-Small Cell Lung Cancer (NSCLC). EGFR mutation negative, ALK negative, PD-L1 TPS 60%. ECOG 0. History of COPD, well-controlled on fluticasone/salmeterol inhaler. Former smoker (quit 5 years ago). Normal kidney and liver function.",
            "Autoimmune: Rheumatoid Arthritis": "41-year-old female with severe, active Rheumatoid Arthritis for 8 years. Failed methotrexate and Humira (adalimumab). Currently experiencing joint swelling in hands and knees. RF positive, anti-CCP positive. ESR 45 mm/hr, CRP 28 mg/L. Otherwise healthy."
        }
        selected = st.selectbox("Load Example", options=list(examples.keys()), label_visibility="collapsed")
        patient_input = st.text_area("Clinical Notes", value=examples.get(selected, ""), height=300, placeholder="Paste raw clinical notes or patient history here...", label_visibility="collapsed")
        run_button = st.button("Run Eligibility Screen", type="primary", use_container_width=True)

    if run_button:
        if not patient_input.strip():
            st.error("Please provide a patient profile.")
            return
        if not os.environ.get("GROQ_API_KEY"):
            st.error("API Key missing. Please configure it in the sidebar.")
            return

        from agent.graph import run_agent

        with col_results:
            st.markdown("### Analysis Dashboard")
            status_placeholder = st.empty()
            with status_placeholder.container():
                progress = st.progress(0, text="Initializing analysis pipeline...")
                time.sleep(0.3)
                progress.progress(25, text="Extracting clinical entities...")
                time.sleep(0.3)
                progress.progress(50, text="Querying clinicaltrials.gov...")
                time.sleep(0.3)
                progress.progress(75, text="Running LLM eligibility evaluation...")

            try:
                result = run_agent(patient_input)
                status_placeholder.empty()

                if result.get("error"):
                    st.error(f"Analysis failed: {result['error']}")
                    return

                matches = result.get("trial_matches", [])
                
                # Apply UI Filters
                min_score = 40  # Hardcoded filter to keep UI clean
                filtered_matches = [m for m in matches if m.get("match_score", 0) >= min_score]
                
                # Top-level metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Trials Evaluated", len(matches))
                m2.metric("Filtered Results", len(filtered_matches))
                avg_score = int(sum(m.get("match_score", 0) for m in filtered_matches) / len(filtered_matches)) if filtered_matches else 0
                m3.metric("Avg Match Score", f"{avg_score}%")
                
                st.markdown("---")

                # UI Tabs for better organization
                tab1, tab2, tab3 = st.tabs(["📋 Trial Matches", "🧬 Extracted Profile", "📄 Clinical Report"])
                
                with tab1:
                    if not filtered_matches:
                        st.info("No trials met the minimum score threshold.")
                    else:
                        high_matches = [m for m in filtered_matches if m.get("match_score", 0) >= 70]
                        med_matches = [m for m in filtered_matches if m.get("match_score", 0) < 70]
                        
                        def render_match(match, expand_first=False):
                            score = match.get("match_score", 0)
                            title = match.get('title', 'Unknown Trial')
                            nct = match.get('nct_id', '')
                            
                            # Add status emoji based on score directly to title
                            status_icon = "🟢" if score >= 70 else "🟡"
                            
                            # Score is now visible directly in the drop down menu
                            expander_title = f"{status_icon} [Score: {score}%] {nct} — {title[:70]}..."
                            
                            with st.expander(expander_title, expanded=expand_first):
                                st.markdown(f"<div class='data-label'>Phase / Status</div>", unsafe_allow_html=True)
                                st.markdown(f"<div class='data-value'>{match.get('phase', '--')} • {match.get('status', '--')}</div>", unsafe_allow_html=True)
                                
                                st.markdown("<div class='data-label'>Eligibility Assessment</div>", unsafe_allow_html=True)
                                st.markdown(f"<div class='data-value' style='color: #4b5563; font-size: 0.9rem;'>{match.get('match_reasoning', '--')}</div>", unsafe_allow_html=True)
                                
                                # New How to Apply section
                                st.markdown(f"""
                                <div class='apply-box'>
                                    <h5>📝 How to Apply / Enroll</h5>
                                    <p style='font-size: 0.85rem; margin-bottom: 0;'>
                                    To pursue this trial, provide the ClinicalTrials.gov identifier <strong>{nct}</strong> to your primary care physician or oncologist to discuss your medical suitability. 
                                    <br><br>
                                    Read the full protocol and find contact information for the study coordinators here:<br>
                                    <a href='{match.get('url', '#')}' target='_blank'>{match.get('url', '#')}</a>
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)

                        if high_matches:
                            st.markdown("##### High Confidence Matches (>70%)")
                            for i, match in enumerate(high_matches):
                                render_match(match, expand_first=(i==0))
                        
                        if med_matches:
                            st.markdown("<br>##### Moderate Confidence Matches", unsafe_allow_html=True)
                            for match in med_matches:
                                render_match(match, expand_first=False)

                with tab2:
                    patient = result.get("parsed_patient", {})
                    p1, p2 = st.columns(2)
                    with p1:
                        st.markdown(f"<div class='data-label'>Demographics</div><div class='data-value'>{patient.get('age', '--')} yr {patient.get('sex', '--')}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='data-label'>Conditions</div><div class='data-value'>{', '.join(patient.get('conditions', [])) or '--'}</div>", unsafe_allow_html=True)
                    with p2:
                        st.markdown(f"<div class='data-label'>Medications</div><div class='data-value'>{', '.join(patient.get('medications', [])) or '--'}</div>", unsafe_allow_html=True)

                with tab3:
                    report = result.get("final_report", "")
                    if report:
                        st.markdown(f"<div style='font-size: 0.9rem; color: #374151; line-height: 1.6;'>{report}</div>", unsafe_allow_html=True)
                    else:
                        st.info("No report generated.")

            except Exception as e:
                status_placeholder.empty()
                st.error("An unexpected error occurred during execution.")
                with st.expander("View Error Trace"):
                    import traceback
                    st.code(traceback.format_exc())

    # Personal signature footer
    st.markdown('<div class="footer-text">Divyansh Joshi made with my hands not love</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
