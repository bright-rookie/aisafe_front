import time
import streamlit as st
from aisafe_xgboost import model

def run_ai_analysis(info, bruise, response, lab, xray, video):
    """Run mock AI analysis and return results."""
    results = model(info = info,
                    bruise = bruise,
                    response = response,
                    lab = lab,
                    xray = xray,
                    video = video)
    abuse_risk_score = response[0]
    abuse_cause = response[1]
    return abuse_risk_score, abuse_cause
