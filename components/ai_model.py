import time
import streamlit as st

def run_ai_analysis():
    """Run mock AI analysis and return results."""
    with st.spinner('AI 분석 중입니다...'):
        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.05)  # AI 분석 작업 시뮬레이션
            progress.progress(i + 1)
    
    # Mock AI output
    abuse_risk_score = 63
    abuse_cause = ["멍", 43, "진술", 13, "검사결과", 5, "동영상", 2]
    
    return abuse_risk_score, abuse_cause