import streamlit as st
import os
import time
import pypdf

st.set_page_config(page_title="Medical AI Suite", layout="wide", initial_sidebar_state="expanded")

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
    
    /* Tables for Lab Report */
    table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; }
    th { text-align: left; padding: 0.75rem; background-color: #f9fafb; border-bottom: 2px solid #e5e7eb; font-size: 0.85rem; color: #6b7280; text-transform: uppercase; }
    td { padding: 0.75rem; border-bottom: 1px solid #e5e7eb; font-size: 0.95rem; }
    
    .status-normal { color: #059669; font-weight: 600; }
    .status-high { color: #dc2626; font-weight: 600; }
    .status-low { color: #d97706; font-weight: 600; }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def get_score_class(score):
    if score >= 70: return "score-high"
    if score >= 40: return "score-med"
    return "score-low"

def extract_pdf_text(uploaded_file):
    reader = pypdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def app_trial_screener():
    st.markdown("""
    <div style="background-color: #f0fdfa; border-left: 4px solid #0d9488; padding: 1.25rem; margin-bottom: 2rem; border-radius: 4px;">
        <p style="margin: 0; font-size: 0.95rem; color: #111827; line-height: 1.5;">
            <strong>Welcome to the AI Clinical Trial Screener.</strong> This tool uses <strong>Groq Llama 3.1</strong> and <strong>LangGraph</strong> to instantly read complex clinical notes, extract key medical conditions, and cross-reference them against thousands of actively recruiting studies on ClinicalTrials.gov. Paste a patient's medical history below to automatically discover and rank the best experimental treatment options in seconds.
        </p>
    </div>
    """, unsafe_allow_html=True)

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
        
        country_filter = st.selectbox("Preferred Trial Location", ["Global", "India", "United States", "United Kingdom", "Canada", "Australia", "Europe"])
        
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
                result = run_agent(patient_input, country_filter)
                status_placeholder.empty()

                if result.get("error"):
                    st.error(f"Analysis failed: {result['error']}")
                    return

                matches = result.get("trial_matches", [])
                min_score = 40
                filtered_matches = [m for m in matches if m.get("match_score", 0) >= min_score]
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Trials Evaluated", len(matches))
                m2.metric("Filtered Results", len(filtered_matches))
                avg_score = int(sum(m.get("match_score", 0) for m in filtered_matches) / len(filtered_matches)) if filtered_matches else 0
                m3.metric("Avg Match Score", f"{avg_score}%")
                
                st.markdown("---")
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
                            status_icon = "🟢" if score >= 70 else "🟡"
                            expander_title = f"{status_icon} [Score: {score}%] {nct} — {title[:70]}..."
                            
                            with st.expander(expander_title, expanded=expand_first):
                                st.markdown(f"<div class='data-label'>Phase / Status</div>", unsafe_allow_html=True)
                                st.markdown(f"<div class='data-value'>{match.get('phase', '--')} • {match.get('status', '--')}</div>", unsafe_allow_html=True)
                                st.markdown("<div class='data-label'>Eligibility Assessment</div>", unsafe_allow_html=True)
                                st.markdown(f"<div class='data-value' style='color: #4b5563; font-size: 0.9rem;'>{match.get('match_reasoning', '--')}</div>", unsafe_allow_html=True)
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


def app_report_analyzer():
    st.markdown("""
    <div style="background-color: #fdf4ff; border-left: 4px solid #c026d3; padding: 1.25rem; margin-bottom: 2rem; border-radius: 4px;">
        <p style="margin: 0; font-size: 0.95rem; color: #111827; line-height: 1.5;">
            <strong>Welcome to the Medical Report Analyzer.</strong> Upload your 6-month checkup or lab results PDF. This tool uses AI to extract complex biomarkers, identify abnormalities, and generate a simple, plain-English explanation of your health metrics so you can understand your body better.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_upload, col_analysis = st.columns([1, 1.5], gap="large")
    
    with col_upload:
        st.markdown("### Upload Report")
        uploaded_file = st.file_uploader("Upload your Lab Report (PDF)", type=["pdf"])
        
        if uploaded_file is not None:
            st.success(f"File '{uploaded_file.name}' uploaded successfully.")
            analyze_button = st.button("Analyze Lab Results", type="primary", use_container_width=True)
            use_mock = False
        else:
            analyze_button = False
            use_mock = st.button("Load Anonymized Mock Report (Example)", type="secondary", use_container_width=True)
            
    if analyze_button or use_mock:
        if not use_mock and not os.environ.get("GROQ_API_KEY"):
            st.error("API Key missing. Please configure it in the sidebar.")
            return
            
        with col_analysis:
            st.markdown("### Health Analysis")
            
            if use_mock:
                biomarkers = [
                    {"test_name": "Hemoglobin", "result_value": "10.3", "unit": "g/dL", "reference_range": "13.0 - 17.0", "status": "Low"},
                    {"test_name": "Red Blood Cell Count", "result_value": "3.78", "unit": "mill/mm3", "reference_range": "4.6 - 6.2", "status": "Low"},
                    {"test_name": "Hematocrit", "result_value": "30.5", "unit": "%", "reference_range": "40 - 54", "status": "Low"},
                    {"test_name": "Mean Corpuscular Volume", "result_value": "80.69", "unit": "fL", "reference_range": "80 - 96", "status": "Normal"},
                    {"test_name": "TOTAL COUNT (WBC)", "result_value": "7900", "unit": "/cmm", "reference_range": "4000 - 11000", "status": "Normal"},
                    {"test_name": "Neutrophils (%)", "result_value": "69.5", "unit": "%", "reference_range": "38 - 70", "status": "Normal"},
                    {"test_name": "Lymphocytes (%)", "result_value": "18.4", "unit": "%", "reference_range": "20 - 45", "status": "Low"},
                    {"test_name": "Eosinophils (%)", "result_value": "5.8", "unit": "%", "reference_range": "1 - 4", "status": "High"}
                ]
                explanation = "### 🌟 Your Health Summary\n\n**The Good News:**\nGreat news! Your overall white blood cell count (WBC) and your main immune cells (neutrophils) are completely normal, which means your body isn't showing signs of severe active infection. Your Mean Corpuscular Volume (MCV) is also within the normal healthy range.\n\n**Areas to Watch (High/Low):**\n* **Hemoglobin, RBC, & Hematocrit (Low):** Your Hemoglobin and Red Blood Cell counts are slightly lower than the normal range. This indicates mild anemia, meaning your blood might not be carrying as much oxygen as it should. This can cause fatigue or weakness. Consider eating more iron-rich foods like leafy greens, lentils, and lean meats, or discuss iron supplements with your doctor.\n* **Lymphocytes (Low):** These are a type of white blood cell. A slightly lower value can sometimes be a temporary response to stress, a recent mild illness, or just a natural variation.\n* **Eosinophils (High):** Eosinophils are white blood cells involved in allergic responses. A slightly elevated number could just mean you're dealing with mild seasonal allergies or a minor skin/allergic reaction.\n\n---\n*Disclaimer: This analysis is generated by AI for informational purposes only. Please share these results with your primary care doctor to get a professional diagnosis and discuss if any treatments or dietary changes are right for you.*"
            else:
                with st.spinner("Extracting text from PDF..."):
                    try:
                        pdf_text = extract_pdf_text(uploaded_file)
                    except Exception as e:
                        st.error(f"Failed to read PDF: {str(e)}")
                        return
                
                if len(pdf_text.strip()) < 10:
                    st.error("Could not extract any text from this PDF. It may be a scanned image without OCR.")
                    return
                    
                with st.spinner("AI is analyzing your biomarkers..."):
                    from agent.report_analyzer import analyze_lab_report
                    try:
                        results = analyze_lab_report(pdf_text)
                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")
                        return
                        
                biomarkers = results.get("biomarkers", [])
                explanation = results.get("explanation", "")
            
            if not biomarkers:
                st.warning("No structured lab results found in the document.")
            else:
                tab_summary, tab_data = st.tabs(["💬 Plain English Summary", "📊 Extracted Data"])
                
                with tab_summary:
                    st.markdown(f"<div style='font-size: 0.95rem; line-height: 1.6;'>{explanation}</div>", unsafe_allow_html=True)
                    
                with tab_data:
                    # Build HTML table
                    html = "<table><tr><th>Test Name</th><th>Result</th><th>Units</th><th>Range</th><th>Status</th></tr>"
                    for b in biomarkers:
                        status = b.get('status', 'Normal')
                        status_class = f"status-{status.lower()}" if status in ['High', 'Low'] else "status-normal"
                        
                        html += f"<tr>"
                        html += f"<td>{b.get('test_name', '--')}</td>"
                        html += f"<td><strong>{b.get('result_value', '--')}</strong></td>"
                        html += f"<td>{b.get('unit', '--')}</td>"
                        html += f"<td>{b.get('reference_range', '--')}</td>"
                        html += f"<td class='{status_class}'>{status}</td>"
                        html += f"</tr>"
                    html += "</table>"
                    st.markdown(html, unsafe_allow_html=True)


def main():
    st.markdown('<div class="header-container"><h1 class="header-title">Medical AI Suite</h1><div class="header-subtitle">Advanced AI tools for patients and researchers</div></div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 1rem; margin-bottom: 2rem; border-radius: 4px;">
        <p style="margin: 0; font-size: 0.9rem; color: #92400e;">
            <strong>⏳ Heads up:</strong> The AI inference engine can sometimes be slow when evaluating complex medical data. Please be patient while the results are generated.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### Navigation")
        app_mode = st.radio("Select Tool", ["🧬 Clinical Trial Screener", "📄 Lab Report Analyzer"])
        
        st.markdown("---")
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            api_key = st.text_input("Groq API Key", type="password")
            if api_key:
                os.environ["GROQ_API_KEY"] = api_key
        else:
            st.caption("✅ API Key securely configured.")

    if app_mode == "🧬 Clinical Trial Screener":
        app_trial_screener()
    else:
        app_report_analyzer()

    st.markdown('<div class="footer-text">Divyansh Joshi made with my hands not love</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
