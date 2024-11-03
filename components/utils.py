import pandas as pd  # type:ignore #noqa
import streamlit as st


def parse_data(data_df, patient_number, required_columns, data_type):
    """Parse basic information from CSV file."""
    if not required_columns.issubset(data_df.columns):
        missing_columns = list(required_columns - set(data_df.columns))
        st.error(
            f"CSV 파일에서 정보를 확인하기 위해 필요한 열이 없습니다. 다음 열을 추가해주세요: {', '.join(missing_columns)}"
        )
        return None

    filtered_info = data_df[data_df["patient_number"] == patient_number]

    if filtered_info.empty:
        st.error(
            f"CSV 파일에 환자 번호 {patient_number}에 대한 {data_type} 정보 정보를 찾을 수 없습니다."
        )
        return None

    st.success(f"{data_type} 정보가 성공적으로 업로드되었습니다.")
    data_vector = (
        filtered_info.drop(columns=["patient_number"]).values.flatten().tolist()
    )

    return data_vector
