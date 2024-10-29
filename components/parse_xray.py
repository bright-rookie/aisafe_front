import re
import os

import nltk  # type:ignore
import streamlit as st
from nltk.tokenize import sent_tokenize  # type:ignore

nltk_data_path = '/home/catbase/aisafe_front/nltk_data'
nltk.data.path.append(nltk_data_path)

def process_xray_text(files, input_patient_number):
    """Process uploaded X-ray text files."""
    if not files:
        return None
    body_parts = ["skull", "torso", "arms", "legs", "pelvis"]
    xray_data = {part: "Not available" for part in body_parts}

    for file in files:
        filename = file.name
        file_patient_number = filename.split("_")[0]
        part_name = filename.split("_")[1].replace(".txt", "")

        if str(file_patient_number) != str(input_patient_number):
            st.error(
                f"파일 {filename}의 환자 번호가 현재 진료 중인 환자 번호와 일치하지 않습니다."
            )
            return None

        if part_name in body_parts:
            file_content = file.read().decode("utf-8")
            xray_data[part_name] = (
                file_content if file_content.strip() else "Not available"
            )
        else:
            st.error(f"파일 {filename}에 부위 이름이 잘못되었습니다: {part_name}")
            return None

    xray_report_text = f"patient_number: {input_patient_number}\n"
    for part in body_parts:
        xray_report_text += f"{part}: {xray_data[part]}\n"

    return xray_report_text


def get_fracture_count(text):
    """Get fracture count from X-ray report text."""
    if text == "" or text == "Not available":
        return 0

    no_fracture_patterns = ["no evidence of", "no fracture", "no fx"]
    for pattern in no_fracture_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return 0

    multiple_patterns = [
        "multiple",
        "various",
        "several",
        "healing",
        "healed",
        "callus",
        "prior",
        "fractures",
    ]
    for pattern in multiple_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return 2

    single_pattern = ["fracture", "fx"]
    for pattern in single_pattern:
        if re.search(pattern, text, re.IGNORECASE):
            return 1


def check_specific_fracture(text, fracture_type):
    """Check for specific fracture types in X-ray report text."""
    if text == " " or text == "Not available Not available":
        return 0
    elif re.search(fracture_type, text, re.IGNORECASE):
        return 1
    else:
        return 0


def parse_report(text):
    """Parse X-ray report text into sections."""
    if not text:
        return {"skull": "", "torso": "", "arms": "", "legs": "", "pelvis": ""}

    report_sections = {"skull": "", "torso": "", "arms": "", "legs": "", "pelvis": ""}

    for section in report_sections:
        pattern = f"{section}:\\s*(.*?)(?=\\n\\w+:|$)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            report_sections[section] = match.group(1).strip()

    return report_sections


def split_sentences(text):
    """Split text into sentences."""
    return sent_tokenize(text)


def generate_xray_vector(text):
    """Generate X-ray vector from report text."""
    report = parse_report(text)

    skull = get_fracture_count(report.get("skull", ""))
    ribs = get_fracture_count(report.get("torso", ""))
    pelvis = get_fracture_count(report.get("pelvis", ""))

    arms_sentences = split_sentences(report.get("arms", ""))
    radius_ulna = humerus = 0
    for sentence in arms_sentences:
        if "radius" in sentence.lower() or "ulna" in sentence.lower():
            radius_ulna = get_fracture_count(sentence)
        if "humerus" in sentence.lower():
            humerus = get_fracture_count(sentence)

    legs_sentences = split_sentences(report.get("legs", ""))
    tibia_fibula = femur = 0
    for sentence in legs_sentences:
        if "tibia" in sentence.lower() or "fibula" in sentence.lower():
            tibia_fibula = get_fracture_count(sentence)
        if "femur" in sentence.lower():
            femur = get_fracture_count(sentence)

    arms_legs_text = report.get("arms", "") + " " + report.get("legs", "")
    spiral_fx = check_specific_fracture(arms_legs_text, "spiral")
    metaphyseal_fx = check_specific_fracture(arms_legs_text, "metaphyseal")

    xray_vector = [
        skull,
        ribs,
        humerus,
        radius_ulna,
        femur,
        tibia_fibula,
        pelvis,
        spiral_fx,
        metaphyseal_fx,
    ]

    return xray_vector
