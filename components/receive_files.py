import streamlit as st
import pandas as pd
import os
import re
import io

from components.utils import parse_data
from aisafe_xgboost.utils import ParseGrowth


def receive_basics(patient_number):
    st.markdown("**환자 기본 정보**")
    basic_info_df = pd.read_csv('./example_files/info.csv')
    required_columns = {
        "patient_number",
        "age_months",
        "sex",
        "height_cm",
        "weight_kg",
    }
    info_vector_pre = parse_data(basic_info_df, patient_number, required_columns, "기본")
    parser = ParseGrowth(*info_vector_pre)
    info_vector = parser.get_percentiles()
    return info_vector

def receive_labs(patient_number):
    st.markdown("**Lab 데이터**")
    lab_data_df = pd.read_csv('./example_files/lab.csv')
    required_columns = {
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
    }
    return parse_data(lab_data_df, patient_number, required_columns, "Lab")


def receive_xrays(file_path, patient_number):
    files = os.listdir(file_path)
    pattern = rf'^{patient_number}_.+\.txt$'
    matching_files = [f for f in files if re.match(pattern, f)]

    uploaded_files = []
    for file_name in matching_files:
        file_path_full = os.path.join(file_path, file_name)
        with open(file_path_full, 'rb') as file:  # 바이너리 모드로 읽음
            file_content = file.read()  # 파일 내용을 읽음

            # 파일을 임시 메모리에 저장하기 위해 io.BytesIO 사용 (바이너리 파일 지원)
            file_obj = io.BytesIO(file_content)
            file_obj.name = file_name  # 파일명 추가

            # 파일을 리스트에 추가
            uploaded_files.append(file_obj)

    return uploaded_files
