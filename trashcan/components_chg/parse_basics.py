import pandas as pd  # type:ignore
import streamlit as st


def calculate_percentile(value, age_data):
    percentiles = age_data.columns[1:].astype(float)
    values = age_data.iloc[0, 1:].values.astype(float)

    if value <= values[0]:
        return f"{percentiles[0]}th 이하"
    elif value >= values[-1]:
        return f"{percentiles[-1]}th 이상"

    # linear interpolation between the two points
    for i in range(len(values) - 1):
        if values[i] <= value <= values[i + 1]:
            # get the lower and upper bounds
            lower_bound = values[i]
            upper_bound = values[i + 1]
            lower_percentile = percentiles[i]
            upper_percentile = percentiles[i + 1]

            # calculate the percentile
            percentile = lower_percentile + (
                (value - lower_bound) / (upper_bound - lower_bound)
            ) * (upper_percentile - lower_percentile)
            return round(percentile, 2)

    return None


def add_growth_info(pre_info_vector, patient_number):
    """Add growth information to basic information."""
    info_vector = pre_info_vector[:]

    sex_to_str = ["남", "여"]
    sex = int(pre_info_vector[1])
    if sex not in [0, 1]:
        st.error("성별 정보가 올바르지 않습니다.")
        return None

    try:
        height_data = pd.read_csv(f"{sex_to_str[sex]}_height.csv")
        weight_data = pd.read_csv(f"{sex_to_str[sex]}_weight.csv")
    except FileNotFoundError:
        st.error("성장 데이터 파일을 찾을 수 없습니다. \n 파일 이름을 확인해주세요.")
        return None

    if height_data is None or weight_data is None:
        st.error("성장 데이터 파일을 찾을 수 없습니다.")
        return None

    age = pre_info_vector[0]
    height_data["Age(Months)"] = height_data["Age(Months)"].astype(int)
    weight_data["Age(Months)"] = weight_data["Age(Months)"].astype(int)

    filtered_height = height_data[height_data["Age(Months)"] == age]
    filtered_weight = weight_data[weight_data["Age(Months)"] == age]

    if filtered_height.empty or filtered_weight.empty:
        st.error("해당 연령에 맞는 표준 데이터를 찾을 수 없습니다.")
        return None

    height = pre_info_vector[2]
    weight = pre_info_vector[3]

    height_percentile = calculate_percentile(height, filtered_height)
    weight_percentile = calculate_percentile(weight, filtered_weight)

    if not height_percentile or not weight_percentile:
        st.error("키 또는 몸무게에 대한 백분위수를 계산할 수 없습니다.")
        return None

    info_vector[2] = height_percentile
    info_vector[3] = weight_percentile

    st.write(f"환자 번호: {patient_number}")
    st.write(f"연령: {age} 개월")
    st.write(f"성별: {sex_to_str[sex]}")
    st.write(f"키: {height} cm ({height_percentile}th)")
    st.write(f"체중: {weight} kg ({weight_percentile}th)")

    return info_vector
