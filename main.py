import time
from itertools import islice

import plotly.express as px
import streamlit as st
from aisafe_xgboost import video_back
from PIL import Image, ImageDraw, ImageFont

from components.ai_model import run_ai_analysis
from components.bruise_components import (
    analyze_bruise_info,
    display_bruise_info,
    get_bruise_data,
)
from components.history_components import get_history
from components.parse_xray import generate_xray_vector, process_xray_text
from components.receive_files import receive_basics, receive_labs, receive_xrays
from components.sidebar import sidebar
from components.video_components import audio_save, record_video, video_dissembly

# Defaults
info_uploaded = False
lab_uploaded = False

if "info_vector" not in st.session_state:
    st.session_state.info_vector = None
if "raw_info_vector" not in st.session_state:
    st.session_state.raw_info_vector = None
if "lab_vector" not in st.session_state:
    st.session_state.lab_vector = None
if "xray_vector" not in st.session_state:
    st.session_state.xray_vector = None
if "xray_uploaded" not in st.session_state:
    st.session_state.xray_uploaded = False
if "button_clicked1" not in st.session_state:
    st.session_state.button_clicked1 = False
if "button_clicked2" not in st.session_state:
    st.session_state.button_clicked2 = False


# Header
st.title("AI-SAFE: 아동학대 선별 시스템")
st.subheader("Patient Information")
patient_number = st.number_input(
    "환자 번호를 입력해주세요:", value=1, min_value=1, step=1
)

# Section 1: EMR Information
st.subheader("1. EMR 업로드")
st.write("입력하신 환자에 대한 EMR 정보를 업로드하시겠습니까?")

if st.button("EMR 업로드"):
    st.session_state.button_clicked1 = True

col1, col2 = st.columns(2)

if st.session_state.button_clicked1 and (patient_number is not None):
    st.session_state.button_clicked1 = True
    with col1:
        (
            st.session_state.info_vector,
            st.session_state.raw_info_vector,
        ) = receive_basics(patient_number)
    with col2:
        st.session_state.lab_vector = receive_labs(patient_number)


# Section 2: X-ray Information
st.write("X-ray 정보를 업로드하시겠습니까?")
if st.button("X-ray 업로드"):
    st.session_state.button_clicked2 = True

if st.session_state.button_clicked2 and (patient_number is not None):
    xray_test = receive_xrays("./example_files/xray", str(patient_number))
    xray_report = process_xray_text(xray_test, patient_number)

    if xray_report:
        st.success("X-ray 데이터가 성공적으로 업로드되었습니다.")
        st.text_area("합쳐진 X-ray 판독문:", value=xray_report, height=250)
        st.session_state.xray_vector = generate_xray_vector(xray_report)
    else:
        st.success("해당 환자의 X-ray가 없습니다.")
        st.session_state.xray_vector = generate_xray_vector("")


# Section 3: Bruise Information
input_col, image_col = st.columns([2, 1])

with input_col:
    st.subheader("2. 멍 정보")
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

st.session_state.bruise_vector = analyze_bruise_info(selected_body_parts, bruise_data)

# Section 3: Video Recording
st.subheader("3. 진료 영상")

if "video_recorded" not in st.session_state:
    st.session_state.video_recorded = False

if "video_uploaded" not in st.session_state:
    st.session_state.video_uploaded = False

if "audio_uploaded" not in st.session_state:
    st.session_state.audio_uploaded = False

if "video_address" not in st.session_state:
    st.session_state.video_address = None

if "audio_address" not in st.session_state:
    st.session_state.audio_address = None

st.markdown(
    "> 녹화를 진행하거나 이미 촬영한 영상이나 음성 파일을 업로드해주세요. <br> 영상이 없다면 '영상 없음' 버튼을 눌러주세요.",
    unsafe_allow_html=True,
)


# Button 1: Start Video Recording using OpenCV
if st.button("녹화 시작") and not st.session_state.video_recorded:
    st.info("녹화는 1분 동안 진행되며, 중간에 중단을 원할시 Q 키를 눌러주세요")
    st.session_state.video_address, st.session_state.audio_address = record_video()
    st.session_state.video_recorded = True  # 녹화 상태 저장
    st.success("영상이 성공적으로 촬영되었습니다.")

# Button 2: No Video Option
if st.button("영상 없음"):
    st.session_state.video_address = None
    st.session_state.audio_address = None
    st.session_state.video_uploaded = True

# Button 3: Upload Video File
uploaded_video = st.file_uploader("비디오 파일 업로드 (MP4)", type=["mp4"])
if uploaded_video and not st.session_state.video_uploaded:
    st.session_state.video_address, st.session_state.audio_address = video_dissembly(
        uploaded_video
    )
    st.session_state.video_uploaded = True  # 업로드 상태 저장
    st.success("비디오 파일이 성공적으로 업로드 되었습니다.")


# Button 4: Upload Audio File
uploaded_audio = st.file_uploader("오디오 파일 업로드 (MP3)", type=["mp3"])
if uploaded_audio and not st.session_state.audio_uploaded:
    st.session_state.video_address, st.session_state.audio_address = audio_save(
        uploaded_audio
    )
    st.session_state.audio_uploaded = True  # 업로드 상태 저장
    st.success("오디오 파일이 성공적으로 업로드 되었습니다.")


# Proceed to next step
if (
    st.session_state.video_recorded
    or st.session_state.video_uploaded
    or st.session_state.audio_uploaded
):
    st.info("문진을 진행해주세요")
else:
    st.warning("녹화를 진행하거나 파일을 업로드해주세요.")


# Section 4: History Questions
st.subheader("4. 문진 정보")
st.session_state.response_vector = get_history()

# Section 5: Run AI Analysis
if st.button("AI 실행"):
    with st.spinner("AI 분석 중입니다..."):
        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.05)  # AI 분석 작업 시뮬레이션
            progress.progress(i + 1)
    st.session_state.video_vector = video_back(
        st.session_state.video_address, st.session_state.audio_address
    )
    abuse_risk_score, abuse_cause = run_ai_analysis(
        st.session_state.info_vector,
        st.session_state.bruise_vector,
        st.session_state.response_vector,
        st.session_state.lab_vector,
        st.session_state.xray_vector,
        st.session_state.video_vector,
    )
    st.subheader("AI 학대 의심률")
    st.write(f"아동학대 의심률은 {abuse_risk_score*100:.2f}%입니다")
    categories = []
    values = []
    for idx, (cause, percent) in enumerate(islice(abuse_cause, 5), start=1):
        rank = (
            ["가장 가능성이 높은", "두번째", "세번째", "네번째", "다섯번째"][idx - 1]

        )
        st.write(f"{rank} 근거는 {cause}(으)로 {percent * 100 : .2f}% 관여합니다.")
        categories.append(cause)
        values.append(f"{percent * 100 : .2f}")

    # 바 그래프 생성
    fig = px.bar(
        x=values[::-1],
        y=categories[::-1],
        title="의심률 관여 비중",
        labels={"x": "퍼센트", "y": "항목"},
        orientation="h",
        text=values[::-1],
    )

    # Streamlit에서 출력
    st.plotly_chart(fig)

# Add a sidebar for the table of contents and data preview
sidebar(
    st.session_state.bruise_vector, st.session_state.raw_info_vector, patient_number
)
