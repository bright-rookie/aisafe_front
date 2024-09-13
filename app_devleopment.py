# app.py
import streamlit as st
from development import calculate_percentile

# Streamlit 앱 제목
st.title("체중 및 신장 백분위 계산기")

# 성별, 개월 수, 체중, 신장 입력 받기
gender = st.selectbox("성별을 선택하세요:", ("male", "female"))
age = st.number_input("개월 수를 입력하세요:", min_value=0, max_value=216, value=12, step=1)
weight = st.number_input("체중을 입력하세요 (kg):", min_value=0.0, max_value=100.0, value=10.0, step=0.1)
height = st.number_input("신장을 입력하세요 (cm):", min_value=0.0, max_value=250.0, value=75.0, step=0.1)

# 버튼을 눌렀을 때 계산 수행
if st.button("계산하기"):
    # 체중과 신장의 백분위 계산
    weight_percentile = calculate_percentile(age, weight, gender, 'weight')
    height_percentile = calculate_percentile(age, height, gender, 'height')

    # 결과 출력
    st.subheader("결과")
    st.write(f"체중 백분위: {weight_percentile}")
    st.write(f"신장 백분위: {height_percentile}")
