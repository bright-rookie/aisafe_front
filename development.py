import pandas as pd
import numpy as np

# CSV 파일 불러오기
weight_male_df = pd.read_csv('csv/weight_male.csv')
weight_female_df = pd.read_csv('csv/weight_female.csv')
height_female_df = pd.read_csv('csv/height_female.csv')
height_male_df = pd.read_csv('csv/height_male.csv')

# 백분위 계산 함수
def calculate_percentile(age_months, value, gender, data_type):
    if data_type == 'weight':
        if gender == 'female':
            data_row = weight_female_df[weight_female_df['Age(Months)'] == age_months]
        elif gender == 'male':
            data_row = weight_male_df[weight_male_df['Age(Months)'] == age_months]
        else:
            return "잘못된 성별입니다."
    elif data_type == 'height':
        if gender == 'female':
            data_row = height_female_df[height_female_df['Age(Months)'] == age_months]
        elif gender == 'male':
            data_row = height_male_df[height_male_df['Age(Months)'] == age_months]
        else:
            return "잘못된 성별입니다."

    if data_row.empty:
        return "해당 개월 수에 대한 데이터가 없습니다."

    # 백분위 및 값들을 숫자(float)로 변환
    percentiles = [float(p) for p in data_row.columns[1:]]
    values = data_row.values[0][1:].astype(float)

    if value < values[0]:
        return f"{percentiles[0]} 백분위 (최소 값)"
    elif value > values[-1]:
        return f"{percentiles[-1]} 백분위 (최대 값)"
    else:
        for i in range(len(values) - 1):
            if values[i] <= value <= values[i + 1]:
                lower_percentile = percentiles[i]
                upper_percentile = percentiles[i + 1]
                lower_value = values[i]
                upper_value = values[i + 1]
                # 선형 보간법으로 백분위 계산
                calculated_percentile = np.interp(value, [lower_value, upper_value], [lower_percentile, upper_percentile])
                calculated_percentile = round(calculated_percentile, 1) 
                return f"입력된 값은 {calculated_percentile} 백분위에 근사합니다."