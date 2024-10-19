import streamlit as st
from PIL import Image, ImageDraw, ImageFont

from components.bruise_components import (
    analyze_bruise_info,
    display_bruise_info,
    get_bruise_data,
)

if 'bruise_vector' not in st.session_state:
    st.session_state.bruise_vector = None

if 'bruise_data' not in st.session_state :
    st.session_state.bruise_data = None

if 'selected_body_parts' not in st.session_state:
    st.session_state.selected_body_parts = None

# Section 1: Bruise Information
input_col, image_col = st.columns([2, 1])

with input_col:
    st.subheader("1. 멍 정보")
    st.session_state.bruise_data, st.session_state.selected_body_parts = get_bruise_data()

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
        st.session_state.bruise_data,
        image,
        draw,
        body_part_coords,
        st.session_state.selected_body_parts,
        font,
    )

st.session_state.bruise_vector = analyze_bruise_info(st.session_state.selected_body_parts, st.session_state.bruise_data)
