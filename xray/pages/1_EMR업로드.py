import streamlit as st
import os

from components.parse_xray import generate_xray_vector, process_xray_text
from components.receive_files import receive_basics, receive_labs, receive_xrays

if "uploaded" not in st.session_state :
    st.session_state.uploaded = False

if "info_vector" not in st.session_state :
    st.session_state.info_vector = False
if "lab_vector" not in st.session_state :
    st.session_state.lab_vector = False
if "xray_vector" not in st.session_state :
    st.session_state.xray_vector = False

if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False


st.subheader("EMR 업로드")
st.write("입력하신 환자에 대한 EMR 정보를 업로드하시겠습니까?")
col1, col2 = st.columns(2)

if st.button("EMR 업로드") :
    st.session_state.button_clicked = True


if st.session_state.button_clicked and (st.session_state.patient_number is not None):
    st.session_state.button_clicked = True
    with col1:
        st.session_state.info_vector = receive_basics(st.session_state.patient_number)
    with col2:
        st.session_state.lab_vector = receive_labs(st.session_state.patient_number)



st.write("X-ray 정보를 업로드하시겠습니까?")
if st.button("X-ray 업로드") and (st.session_state.patient_number is not None):
    xray_test = receive_xrays('./xray', str(st.session_state.patient_number))
    xray_report = process_xray_text(xray_test, st.session_state.patient_number)

    if xray_report:
        st.success("X-ray 데이터가 성공적으로 업로드되었습니다.")
        st.text_area("합쳐진 X-ray 판독문:", value=xray_report, height=250)
        st.session_state.xray_vector = generate_xray_vector(xray_report)

if st.button("X-ray 없음"):
    st.session_state.xray_vector = generate_xray_vector("")
