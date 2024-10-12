import time
import streamlit as st
import xgboo

def run_ai_analysis(info, bruise, response, lab, xray, video):
    """Run mock AI analysis and return results."""
    with st.spinner('AI 분석 중입니다...'):
        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.05)  # AI 분석 작업 시뮬레이션
            progress.progress(i + 1)
    results = xgboo.model(info, bruise, response, lab, xray, video)
    abuse_risk_score = response[0] * 100
    abuse_cause = response[1]

    return abuse_risk_score, abuse_cause
