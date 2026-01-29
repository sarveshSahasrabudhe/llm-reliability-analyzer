import streamlit as st
import pandas as pd
import requests
from db.session import SessionLocal
from db.models import Run, TestResult
import os

# Configuration
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="LLM Reliability Analyzer",
    page_icon="🔬",
    layout="wide"
)

def load_runs():
    """Load all runs from database"""
    db = SessionLocal()
    try:
        runs = db.query(Run).order_by(Run.timestamp.desc()).all()
        return runs
    finally:
        db.close()

def load_run_details(run_id: str):
    """Load detailed results for a specific run"""
    db = SessionLocal()
    try:
        run = db.query(Run).filter(Run.id == run_id).first()
        if run:
            results = db.query(TestResult).filter(TestResult.run_id == run_id).all()
            return run, results
        return None, []
    finally:
        db.close()

# Header
st.title("🔬 LLM Reliability Analyzer")
st.markdown("---")

# Sidebar - Run Selector
st.sidebar.header("📊 Test Runs")

runs = load_runs()

if not runs:
    st.warning("No test runs found. Run a test suite first using the API or CLI.")
    st.stop()

# Format run options for dropdown
run_options = {}
for run in runs:
    timestamp = run.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    pass_rate = f"{run.pass_rate*100:.0f}%" if run.pass_rate is not None else "N/A"
    label = f"{run.model_name} | {timestamp} | {pass_rate}"
    run_options[label] = run.id

selected_run_label = st.sidebar.selectbox(
    "Select a run:",
    options=list(run_options.keys())
)

selected_run_id = run_options[selected_run_label]

# Load selected run details
run, results = load_run_details(selected_run_id)

if not run:
    st.error("Failed to load run details")
    st.stop()

# Main Panel - Summary Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Model", run.model_name)

with col2:
    if run.pass_rate is not None:
        pass_rate_pct = run.pass_rate * 100
        st.metric("Pass Rate", f"{pass_rate_pct:.1f}%")
    else:
        st.metric("Pass Rate", "N/A")

with col3:
    if run.avg_latency is not None:
        st.metric("Avg Latency", f"{run.avg_latency:.0f}ms")
    else:
        st.metric("Avg Latency", "N/A")

with col4:
    st.metric("Total Tests", len(results))

st.markdown("---")

# Prepare data for table
results_data = []
failed_count = 0
for result in results:
    if result.status == "FAIL":
        failed_count += 1
    
    results_data.append({
        "test_name": result.test_name,
        "status": result.status,
        "input_prompt": result.input_prompt,
        "output_text": result.output_text,
        "failure_reasons": result.failure_reasons,
        "latency_ms": result.latency_ms,
        "tags": [], # Tags are not stored in TestResult currently
        "judge_score": result.judge_score,
        "judge_reasoning": result.judge_reasoning
    })

# --- Tabs ---
tab1, tab2 = st.tabs(["Run Details", "Compare Runs"])

with tab1:
    # Results Table
    st.subheader("Test Results")
    
    # Filter options
    filter_status = st.multiselect(
        "Filter by Status",
        ["PASS", "FAIL"],
        default=["PASS", "FAIL"]
    )
    
    filtered_results = [r for r in results_data if r["status"] in filter_status]
    
    # Display as table with colors
    for result in filtered_results:
        color = "green" if result["status"] == "PASS" else "red"
        icon = "✅" if result["status"] == "PASS" else "❌"
        
        with st.expander(f"{icon} {result['test_name']} ({result['latency_ms']:.0f}ms)"):
            st.markdown(f"**Tags:** {', '.join(result.get('tags', []))}")
            
            # Show judge score if available
            if result.get('judge_score') is not None:
                 st.info(f"⚖️ **Judge Score:** {result['judge_score']}/10\n\n**Reasoning:** {result.get('judge_reasoning', 'N/A')}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Input Prompt:**")
                st.code(result["input_prompt"], language="text")
            with col2:
                st.markdown("**Output:**")
                st.code(result["output_text"], language="text")
            
            if result["status"] == "FAIL":
                st.error(f"**Failure Reasons:**\n{result.get('failure_reasons', 'Unknown')}")

with tab2:
    st.header("Run Comparison")
    
    # Select comparison run
    st.markdown("Compare **Current Run** (selected in sidebar) against:")
    
    # Exclude current run from options
    compare_options = {k: v for k, v in run_options.items() if v != selected_run_id}
    
    if not compare_options:
        st.warning("Need at least 2 runs to compare.")
    else:
        compare_run_name = st.selectbox("Select Baseline Run", list(compare_options.keys()))
        base_run_id = compare_options[compare_run_name]
        
        if st.button("Compare Results"):
            with st.spinner("Analyzing differences..."):
                try:
                    # Call API
                    response = requests.get(
                        f"{API_URL}/compare",
                        params={"base_run": base_run_id, "compare_run": selected_run_id}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Metrics Delta
                        c1, c2, c3, c4 = st.columns(4)
                        
                        delta = data['pass_rate_delta'] * 100
                        c1.metric(
                            "Pass Rate Change", 
                            f"{data['pass_rate_delta']*100:+.1f}%",
                            delta_color="normal"
                        )
                        
                        c2.metric("Regressions", data['regressions_count'], delta_color="inverse")
                        c3.metric("Improvements", data['improvements_count'], delta_color="normal")
                        c4.metric("Latency Delta", f"{data['avg_latency_delta']:+.0f}ms", delta_color="inverse")
                        
                        # Regressions List
                        if data['regressions']:
                            st.subheader("🔴 Regressions (New Failures)")
                            for r in data['regressions']:
                                st.error(f"**{r['test_name']}**: PASS → FAIL")
                        
                        # Improvements List
                        if data['improvements']:
                            st.subheader("🟢 Improvements (Fixed)")
                            for i in data['improvements']:
                                st.success(f"**{i['test_name']}**: FAIL → PASS")
                                
                        if not data['regressions'] and not data['improvements']:
                            st.info("No status changes detected between these runs.")
                            
                    else:
                        st.error(f"Comparison failed: {response.text}")
                except Exception as e:
                    st.error(f"Error connecting to API: {e}")

# Footer
st.markdown("---")
st.caption(f"Run ID: `{run.id}` | Timestamp: {run.timestamp}")
