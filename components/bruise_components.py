import streamlit as st


def get_bruise_data() -> tuple[dict, list[str]]:
    """Create bruise dictionary based on user input."""

    if "selected_body_parts" not in st.session_state:
        st.session_state.selected_body_parts = []

    all_body_parts = ["머리", "팔", "다리", "몸통", "엉덩이"]

    cols = st.columns([3, 1])

    with cols[1]:
        if st.button("모두 선택"):
            st.session_state.selected_body_parts = all_body_parts

    with cols[0]:
        selected_body_parts = st.multiselect(
            "멍이 있는 부위들을 골라주세요",
            all_body_parts,
            default=st.session_state.selected_body_parts,
        )

    st.session_state.selected_body_parts = selected_body_parts

    st.markdown(
        "> 멍의 개수가 10개 이상인 경우 10을 기입해주세요.  \n > 멍 중 길이가 가장 긴 길이을 기입해주세요."
    )

    bruise_data = {}
    for part in selected_body_parts:
        cols = st.columns(2)
        with cols[0]:
            bruise_data[f"{part}_count"] = st.number_input(
                f"{part}: 멍의 개수",
                min_value=1,
                max_value=10,
                value=1,
                key=f"{part}_count",
            )

        with cols[1]:
            bruise_data[f"{part}_length"] = round(  # type: ignore
                st.number_input(
                    f"{part}: 멍의 장경(cm)",
                    min_value=0.0,
                    max_value=50.0,
                    value=0.0,
                    format="%.2f",
                    key=f"{part}_length",
                ),
                2,
            )

    return bruise_data, selected_body_parts


def display_bruise_info(
    bruise_data, image, draw, body_part_coords, selected_body_parts, font, padding=10
) -> None:
    """Display bruise information on human body image."""
    for part in selected_body_parts:
        count = bruise_data.get(f"{part}_count", 0)
        length = bruise_data.get(f"{part}_length", 0.0)

        if count > 0 or length > 0:
            text = f"{part}\n개수: {count}\n장경: {length}cm"
            position = body_part_coords.get(part, (0, 0))
            bbox = draw.textbbox(position, text, font=font)

            draw.rectangle(
                [
                    (bbox[0] - padding, bbox[1] - padding),  # Top left corner
                    (bbox[2] + padding, bbox[3] + padding),  # Bottom right corner
                ],
                fill="lemonchiffon",  # Background color
            )

            # Draw the text on top of the background
            draw.text(position, text, fill="crimson", font=font)

    for _ in range(4):
        st.write("")

    st.image(image, caption="멍의 위치와 크기", use_column_width=True)


def analyze_bruise_info(selected_body_parts, bruise_data) -> list[int]:
    """Analyze bruise information to detect child abuse."""

    bruise_vector = [0 for _ in range(11)]

    specific_shapes = st.radio(
        "아동학대를 의심할 만한 특정한 멍의 모양이 있나요?", ("예", "아니오")
    )

    # Consists of dict[part] = (count, length)
    body_parts_mapping = {
        "머리": (0, 1),
        "팔": (2, 3),
        "다리": (4, 5),
        "몸통": (6, 7),
        "엉덩이": (8, 9),
    }

    for part in selected_body_parts:
        count_index, length_index = body_parts_mapping[part]
        bruise_vector[count_index] = bruise_data[
            f"{part}_count"
        ]  # Set the bruise count
        bruise_vector[length_index] = bruise_data[
            f"{part}_length"
        ]  # Set the bruise length

    # 12. specific_shapes (Yes -> 0, No -> 1)

    bruise_vector[10] = 0 if specific_shapes == "예" else 1

    return bruise_vector
