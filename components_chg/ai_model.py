import time
import streamlit as st
import aisafe_xgboost_one as xgboo
# import aisafe_xgboost_two as xgboo


def run_ai_analysis(info, bruise, response, lab, xray, video):
    """Run mock AI analysis and return results."""
    results = xgboo.model(info, bruise, response, lab, xray, video)
    abuse_risk_score = response[0]
    abuse_cause = response[1]

    return abuse_risk_score, abuse_cause
