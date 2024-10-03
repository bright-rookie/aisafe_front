import streamlit as st
from PIL import Image, ImageDraw, ImageFont

from components.ai_model import run_ai_analysis
from components.bruise_components import (
    analyze_bruise_info,
    display_bruise_info,
    get_bruise_data,
)
from components.history_components import get_history
from components.parse_basics import add_growth_info
from components.parse_xray import generate_xray_vector, process_xray_text
from components.receive_files import receive_basics, receive_labs, receive_xrays
from components.sidebar import sidebar
from components.video_components import begin_recording

# Header
st.title("AI-SAFE: 아동학대 선별 시스템")
st.subheader("Patient Information")
patient_number = st.number_input(
    "환자 번호를 입력해주세요:", value=1, min_value=1, step=1
)

# Section 1: Bruise Information
input_col, image_col = st.columns([2, 1])

with input_col:
    st.subheader("1. 멍 정보")
    bruise_data, selected_body_parts = get_bruise_data()

with image_col:
    image = Image.open("./assets/human-body.png")
    draw = ImageDraw.Draw(image)
    body_part_coords = {
        "머리": (300, 50),
        "팔": (70, 470),
        "다리": (300, 800),
        "몸통": (410, 530),
        "엉덩이": (130, 650),
    }

    try:
        font = ImageFont.truetype("./fonts/NanumGothic.ttf", 30)
    except IOError:
        font = ImageFont.load_default()  # type: ignore

    display_bruise_info(
        bruise_data,
        image,
        draw,
        body_part_coords,
        selected_body_parts,
        font,
    )

bruise_vector = analyze_bruise_info(selected_body_parts, bruise_data)

# Section 2: Video Recording
st.subheader("2. 진료 영상")

if "recording" not in st.session_state:
    st.session_state.recording = False

begin_recording()

# Section 3: History Questions
st.subheader("3. 문진 정보")
response_vector = get_history()

# Section 4: Load EMR data
info_vector = lab_vector = xray_vector = None

st.subheader("4. EMR 데이터 불러오기")
col1, col2 = st.columns(2)

with col1:
    pre_info_vector = receive_basics(patient_number)
    if pre_info_vector:
        info_vector = add_growth_info(pre_info_vector, patient_number)

with col2:
    lab_vector = receive_labs(patient_number)

# Section 5: Load X-ray Data
xray_test = receive_xrays()
xray_report = process_xray_text(xray_test, patient_number)

if xray_report:
    st.success("X-ray 데이터가 성공적으로 업로드되었습니다.")
    st.text_area("합쳐진 X-ray 판독문:", value=xray_report, height=250)
    xray_vector = generate_xray_vector(xray_report)

if st.button("X-ray 없음"):
    xray_vector = generate_xray_vector("")

# Section 5: Check Data Uploads
if st.button("EMR 데이터 업로드 확인"):
    if info_vector and lab_vector and xray_vector:
        st.session_state.emr_uploaded = True
        st.success("EMR 데이터가 성공적으로 업로드되었습니다.")
    else:
        st.error("모든 필드를 올바르게 업로드해주세요.")

# Section 6: Run AI Analysis
if st.button("AI 실행"):
    if st.session_state.emr_uploaded:
        abuse_risk_score, abuse_cause = run_ai_analysis()
        st.subheader("AI 학대 의심률")
        st.write(f"아동학대 의심률은 {abuse_risk_score}%입니다")
        for i in range(0, len(abuse_cause), 2):
            st.write(
                f"그 가능성을 판단하는데 가장 높게 기여한 {i//2+1}번째 근거는 {abuse_cause[i]}(으)로 {abuse_cause[i+1]}% 관여합니다."
            )
    else:
        st.error("EMR 업로드 확인을 먼저 수행해주십시오.")

# Add a sidebar for the table of contents and data preview
sidebar(bruise_vector, info_vector, patient_number)
