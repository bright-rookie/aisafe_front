import streamlit as st
import pandas as pd

from components.utils import parse_data


def receive_basics(patient_number):
    st.markdown("**환자 기본 정보**")
    basic_info_file = st.file_uploader("기본 정보를 업로드하세요 (CSV)", type=["csv"])
    if basic_info_file is not None:
            try:
                # Read CSV
                basic_info_df = pd.read_csv(basic_info_file)

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

                        info_uploaded = True

                        return info_vector

                    else:
                        st.error(
                            "CSV 파일에 필요한 기본 정보가 포함되어 있지 않습니다. (연령, 성별, 키, 체중)"
                        )
                else:
                    st.error("CSV 파일에 필요한 기본 컬럼이 포함되어 있지 않습니다.")

            except Exception as e:
                st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {e}")


def receive_labs(patient_number):
    st.markdown("**Lab 데이터**")
    lab_data = st.file_uploader("Lab 데이터를 업로드하세요 (CSV)", type=["csv"])
    if lab_data is not None:
            try:
                # Read the CSV file
                lab_data_df = pd.read_csv(lab_data)

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
                        lab_uploaded = True
                        st.success("Lab 데이터가 성공적으로 업로드 되었습니다!")
                        return lab_vector

                    else:
                        st.warning(
                            f"환자 번호 {patient_number}에 해당하는 데이터가 없습니다."
                        )
                else:
                    st.error("CSV 파일에 필요한 컬럼들이 포함되어 있지 않습니다.")

            except Exception as e:
                st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {e}")

def receive_xrays():
    # X-ray reports upload
    st.markdown("**X-ray 판독문**")
    xray_text = st.file_uploader(
        "X-ray 판독문을 업로드하세요 (TXT)", type=["txt"], accept_multiple_files=True
    )
    return xray_text
