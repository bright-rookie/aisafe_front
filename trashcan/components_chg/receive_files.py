import streamlit as st
import pandas as pd
import os
import re
import io

from components.utils import parse_data



def receive_basics(patient_number):
        st.markdown("**환자 기본 정보**")
        basic_info_df = pd.read_csv('./final_files/Basic_information.csv')

        # 필요한 컬럼들
        required_columns = [
            "patient_number",
            "age_months",
            "sex",
            "height_cm",
            "weight_kg",
        ]

        # 필수 컬럼들이 존재하는지 확인
        if set(required_columns).issubset(basic_info_df.columns):
            filtered_df = basic_info_df[
                basic_info_df["patient_number"] == patient_number
            ]

            if not filtered_df.empty:
                st.success("기본 정보가 성공적으로 업로드되었습니다!")
                info_vector = filtered_df.drop(
                    columns=["patient_number"]
                ).values.flatten()
                patient_age = info_vector[0]
                patient_sex = int(info_vector[1])
                patient_height = info_vector[2]
                patient_weight = info_vector[3]

                st.write(f"환자 번호: {patient_number}")
                st.write(f"연령: {patient_age} 개월")
                st.write(f"성별: {'남' if patient_sex == 0 else '여'}")
                st.write(f"키: {patient_height} cm")
                st.write(f"체중: {patient_weight} kg")

                return info_vector

            else:
                st.error(
                    "CSV 파일에 필요한 기본 정보가 포함되어 있지 않습니다. (연령, 성별, 키, 체중)"
                )
        else:
            st.error("CSV 파일에 필요한 기본 컬럼이 포함되어 있지 않습니다.")


def receive_labs(patient_number):
    st.markdown("**Lab 데이터**")

    lab_data_df = pd.read_csv('./final_files/EMR_lab.csv')

    # Ensure the necessary columns are present
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

    if set(required_columns).issubset(lab_data_df.columns):
        # Filter the data by patient number
        patient_data = lab_data_df[
            lab_data_df["patient_number"] == patient_number
        ]

        if not patient_data.empty:
            # Drop the 'patient_number' column and convert the rest to a 1x20 vector
            lab_vector = patient_data.drop(
                columns=["patient_number"]
            ).values.flatten()
            st.success("Lab 데이터가 성공적으로 업로드 되었습니다!")
            return lab_vector

        else:
            st.warning(
                f"환자 번호 {patient_number}에 해당하는 데이터가 없습니다."
            )
    else:
        st.error("CSV 파일에 필요한 컬럼들이 포함되어 있지 않습니다.")


def receive_xrays(file_path, patient_number):
    # 파일 목록 가져오기
    files = os.listdir(file_path)

    # 정규 표현식으로 정확한 환자 번호를 가진 파일 필터링
    pattern = rf'^{patient_number}_.+\.txt$'
    matching_files = [f for f in files if re.match(pattern, f)]

    # 매칭되는 파일들을 메모리에 임시로 저장 (BytesIO로 처리)
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
