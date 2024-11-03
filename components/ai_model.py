from aisafe_xgboost import model


def run_ai_analysis(info, bruise, response, lab, xray, video):
    """Run mock AI analysis and return results."""
    results = model(
        info=info, bruise=bruise, response=response, lab=lab, xray=xray, video=video
    )
    abuse_risk_score = results[0]
    abuse_cause = results[1]
    return abuse_risk_score, abuse_cause
