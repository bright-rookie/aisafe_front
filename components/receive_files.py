import streamlit as st

from components.utils import parse_data


def receive_basics(patient_number):
    st.markdown("환자 기본 정보")
    basic_info_file = st.file_uploader("기본 정보를 업로드하세요 (CSV)", type=["csv"])
    required_columns = {
        "patient_number",
        "age_months",
        "sex",
        "height_cm",
        "weight_kg",
    }
    return parse_data(basic_info_file, patient_number, required_columns)


def receive_labs(patient_number):
    st.markdown("**Lab 데이터**")
    lab_data = st.file_uploader("Lab 데이터를 업로드하세요 (CSV)", type=["csv"])
    required_columns = [
        "patient_number",
        "CBC_RBC",
        "CBC_WBC",
        "CBC_Platelet",
        "Hb",
        "PT_INR",
        "aPTT",
        "AST",
        "ALT",
        "ALP",
        "Na",
        "K",
        "Cl",
        "Calcium",
        "Phosphorus",
        "25hydroxyvitaminD",
        "Serum_albumin",
        "Pre_albumin",
        "Transferrin",
        "Glucose",
    ]
    return parse_data(lab_data, patient_number, required_columns)


def receive_xrays():
    # X-ray reports upload
    st.markdown("**X-ray 판독문**")
    xray_text = st.file_uploader(
        "X-ray 판독문을 업로드하세요 (TXT)", type=["txt"], accept_multiple_files=True
    )
    return xray_text
