import streamlit as st

if 'bruise_data' not in st.session_state :
    st.session_state.bruise_data = {}

if "selected_body_parts" not in st.session_state:
    st.session_state.selected_body_parts = []

if 'specific_shapes' not in st.session_state :
    st.session_state.specific_shapes = None

def get_bruise_data() -> tuple[dict, list[str]]:
    """Create bruise dictionary based on user input."""

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
        "> 멍의 개수가 10개 이상인 경우 10을 기입해주세요.  \n > 멍 중 길이가 가장 긴 장반경을 기입해주세요."
    )

    # 멍 데이터 입력
    for part in st.session_state.selected_body_parts:
        cols = st.columns(2)

        # 멍의 개수를 세션 스테이트에 저장
        count_key = f"{part}_count"
        length_key = f"{part}_length"

        if count_key not in st.session_state.bruise_data:
            st.session_state.bruise_data[count_key] = 1

        if length_key not in st.session_state.bruise_data:
            st.session_state.bruise_data[length_key] = 0.0

        # 멍 개수 입력 필드
        with cols[0]:
            st.session_state.bruise_data[count_key] = st.number_input(
                f"{part}: 멍의 개수",
                min_value=1,
                max_value=10,
                value=st.session_state.bruise_data[count_key],  # 세션에서 가져온 기본값
                key=count_key,
            )

        # 멍 길이 입력 필드
        with cols[1]:
            st.session_state.bruise_data[length_key] = round(  # type: ignore
                st.number_input(
                    f"{part}: 멍의 장반경(cm)",
                    min_value=0.0,
                    max_value=50.0,
                    value=st.session_state.bruise_data[length_key],  # 세션에서 가져온 기본값
                    format="%.2f",
                    key=length_key,
                ),
                2,
            )

    return st.session_state.bruise_data, st.session_state.selected_body_parts


def display_bruise_info(
    bruise_data, image, draw, body_part_coords, selected_body_parts, font, padding=10
) -> None:
    """Display bruise information on human body image."""
    for part in selected_body_parts:
        count = bruise_data.get(f"{part}_count", 0)
        length = bruise_data.get(f"{part}_length", 0.0)

        if count > 0 or length > 0:
            text = f"{part}\n개수: {count}\n장반경: {length}cm"
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

    st.session_state.specific_shapes = st.radio(
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

    bruise_vector[10] = 0 if st.session_state.specific_shapes == "예" else 1

    return bruise_vector
