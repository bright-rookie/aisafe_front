import re

def get_fracture_count(text):
    if text == "NULL":
        return 0

    # Check for single fractures
    single_pattern = ["fracture"]
    for pattern in single_pattern:
        if re.search(pattern, text, re.IGNORECASE):
            return 1

    # Check for explicit no fracture statements
    no_fracture_patterns = ["no evidence of", "no fracture"]
    for pattern in no_fracture_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return 0

    # Check for multiple fractures
    multiple_patterns = ["multiple", "various", "several", "healing", "healed", "callus", "prior"]
    for pattern in multiple_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return 2
    
    return 0

def check_specific_fracture(text, fracture_type):
    if text == "NULL":
        return 0
    if re.search(fracture_type, text, re.IGNORECASE):
        return 1
    return 0

def generate_xray_vector(report):
    skull = get_fracture_count(report.get("skull", "NULL"))
    ribs = get_fracture_count(report.get("torso", "NULL"))
    pelvis = get_fracture_count(report.get("pelvis", "NULL"))

    if "radius" in report.get("arms", "").lower() or "ulna" in report.get("arms", "").lower():
        radius_ulna = get_fracture_count(report.get("arms", ""))
    if "humerus" in report.get("arms", "").lower():
        humerus = get_fracture_count(report.get("arms", ""))
    
    # Separate femur and tibia_fibula based on their specific mentions
    if "tibia" in report.get("legs", "").lower() or "fibula" in report.get("legs", "").lower():
        tibia_fibula = get_fracture_count(report.get("legs", ""))
    if "femur" in report.get("legs", "").lower() :
        femur = get_fracture_count(report.get("legs", ""))
    
    # Check for specific fracture types
    spiral_fx = check_specific_fracture(report.get("arms", "") + report.get("legs", ""), "spiral fracture")
    metaphyseal_fx = check_specific_fracture(report.get("arms", "") + report.get("legs", ""), "metaphyseal fracture")
    
    return [skull, ribs, humerus, radius_ulna, femur, tibia_fibula, pelvis, spiral_fx, metaphyseal_fx]

# Generate x-ray vectors for each patient
xray_vectors = generate_xray_vector(xray_report)
st.text_area("X-ray vector를 확인하세요", value=xray_vectors, height=300)
