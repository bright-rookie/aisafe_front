import streamlit as st
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
from components.video_components import record_video, video_dissembly

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

video_recorded = False
video_uploaded = False
audio_uploaded = False

st.markdown("녹화를 진행하거나 이미 촬영한 영상이나 음성 파일을 업로드해주세요.")

# Button 1: Start Video Recording using OpenCV
if st.button("녹화 시작"):
    # Using OpenCV to start webcam recording
    st.info("녹화는 1분 동안 진행되며, 중간에 중단을 원할시 Q 키를 눌러주세요")
    video_address, audio_address = record_video()
    video_recorded = True
    st.success("영상이 성공적으로 촬영되었습니다.")

# Button 2: Upload Video File
uploaded_video = st.file_uploader("비디오 파일 업로드 (MP4)", type=['mp4'])
if uploaded_video:
    video_address, audio_address = video_dissembly(uploaded_video)
    video_uploaded = True
    st.success("비디오 파일이 성공적으로 업로드 되었습니다.")


# Button 3: Upload Audio File
uploaded_audio = st.file_uploader("오디오 파일 업로드 (MP3, M4A)", type=['mp3', 'm4a'])
if uploaded_audio:
    video_address = None
    audio_address = uploaded_audio.name
    audio_uploaded = True
    st.success("오디오 파일이 성공적으로 업로드 되었습니다.")


# Proceed to next step
if video_recorded or video_uploaded or audio_uploaded:
    st.info("문진을 진행해주세요")
else:
    st.warning("녹화를 진행하거나 비디오 또는 오디오 파일을 업로드해주세요.")



# Section 3: History Questions
st.subheader("3. 문진 정보")
response_vector = get_history()

# Section 4: Load EMR data
info_vector = lab_vector = xray_vector = None

st.subheader("4. EMR 데이터 불러오기")
col1, col2 = st.columns(2)

with col1:
    info_vector = receive_basics(patient_number)

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
        abuse_risk_score, abuse_cause = run_ai_analysis(info_vector, bruise_vector, response_vector, lab_vector, xray_vector, video_vector)
        st.subheader("AI 학대 의심률")
        st.write(f"아동학대 의심률은 {abuse_risk_score}%입니다")
        for idx, (cause, percent) in enumerate(islice(abuse_cause, 3), start = 1):
            rank = ["가장 가능성이 높은", "두번째", "세번째"][idx - 1] if idx <= 3 else f"{idx}번째"
            st.write(f"{rank} 근거는 {cause}(으)로 {percent*100}% 관여합니다.")
    else:
        st.error("EMR 업로드 확인을 먼저 수행해주십시오.")

# Add a sidebar for the table of contents and data preview
sidebar(bruise_vector, info_vector, patient_number)
