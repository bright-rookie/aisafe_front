from aisafe_xgboost import model


def run_ai_analysis(info, bruise, response, lab, xray, video):
    """Run mock AI analysis and return results."""
    if not info:
        info = [0 for _ in range(4)]
    if not bruise:
        bruise = [0 for _ in range(11)]
    if not response:
        response = [0 for _ in range(9)]
    if not lab:
        lab = [0 for _ in range(19)]
    if not xray:
        xray = [0 for _ in range(9)]
    if not video:
        video = [0 for _ in range(30)]
    results = model(
        info=info, bruise=bruise, response=response, lab=lab, xray=xray, video=video
    )
    abuse_risk_score = results[0]
    abuse_cause = results[1]
    return abuse_risk_score, abuse_cause
