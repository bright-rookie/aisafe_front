from PIL import Image, ImageDraw, ImageFont
import streamlit as st

# Title
st.title("AI-SAFE: 아동학대 선별 시스템")


output_vector = [0] * 12  # Initialize a 1x12 vector with zeros

# Section 0: Patient Number Input
st.subheader("Patient Information")

# Input field for patient number
patient_number = st.number_input("환자 번호를 입력해주세요:", min_value=1, step=1)

# Ensure patient number is stored in the output vector at index 0
output_vector[0] = patient_number

# Create two columns: one for the input form and one for the image
input_col, image_col = st.columns([2, 1])  # Adjust the width ratio of columns

with input_col:
    # Section 1: Injury Information
    st.subheader("1. 멍 정보")

    # Define the list of body parts
    all_body_parts = ["머리", "팔", "다리", "몸통", "엉덩이"]

    # Check if 'selected_body_parts' is in session state, if not initialize it
    if 'selected_body_parts' not in st.session_state:
        st.session_state.selected_body_parts = []

    # Create a row with the multiselect and the 'Select All' button on the same line
    cols = st.columns([3, 1])  # First column wider for the multiselect, second for the button

    # Place the 'Select All' button in the second column
    with cols[1]:
        if st.button('모두 선택'):
            st.session_state.selected_body_parts = all_body_parts
            selected_body_parts = all_body_parts

    # Place the multiselect in the first column
    with cols[0]:
        selected_body_parts = st.multiselect(
            "멍이 있는 부위들을 골라주세요:",
            all_body_parts,
            default=st.session_state.selected_body_parts
        )

    # Update the session state to store the selected body parts
    st.session_state.selected_body_parts = selected_body_parts

    # Dictionary to store user inputs for each body part
    bruise_data = {}

    # For each selected body part, show input fields for bruise count and max length on the same row
    for part in selected_body_parts:
        cols = st.columns(2)
        with cols[0]:
            bruise_data[f'{part}_count'] = st.number_input(f'{part}: 멍의 개수', min_value=0, max_value=10, value=0, key=f'{part}_count')
        with cols[1]:
            bruise_data[f'{part}_length'] = st.number_input(f'{part}: 멍의 장반경(cm)', min_value=0.0, max_value=50.0, value=0.0, key=f'{part}_length')

with image_col:
    # Load the human body pictogram
    image = Image.open("human-body.PNG")  # Use your pictogram image file
    draw = ImageDraw.Draw(image)

    # Dictionary with approximate coordinates for each body part on the pictogram
    body_part_positions = {
        "머리": (300, 50),
        "팔": (110, 450),
        "다리": (300, 850),
        "몸통": (450, 550),
        "엉덩이": (700, 700)
    }

    # Font settings for displaying bruise info (adjust path to your system font if needed)
    try:
        font = ImageFont.truetype("NanumGothic.ttf", 40)
    except IOError:
        font = ImageFont.load_default()

    # Padding for text background
    padding = 10

    # Draw bruise info on the image for each selected body part
    for part in selected_body_parts:
        count = bruise_data.get(f'{part}_count', 0)
        length = bruise_data.get(f'{part}_length', 0)
        
        # If there is any bruise data for this part, display it on the image
        if count > 0 or length > 0:
            text = f'{part}\n개수: {count}\n장반경: {length}cm'
            position = body_part_positions.get(part, (0, 0))  # Default to (0, 0) if not found
            
            # Calculate the bounding box of the text for the background
            bbox = draw.textbbox(position, text, font=font)
            
            # Draw the background rectangle with padding
            draw.rectangle(
                [
                    (bbox[0] - padding, bbox[1] - padding),  # Top left corner
                    (bbox[2] + padding, bbox[3] + padding)  # Bottom right corner
                ],
                fill="yellow"  # Background color
            )
            
            # Draw the text on top of the background
            draw.text(position, text, fill="red", font=font)

    # Display the image with a 2x larger width and height
    st.image(image, caption="", width=600)  # Adjust the width as needed (for 2x, increase it proportionally)



# Specific injury shapes
specific_shapes = st.radio(
    '아동학대를 의심할 만한 특정한 멍의 모양이 있나요?',
    ('Yes', 'No')
)

# Mapping for each body part (head, arms, legs, torso, buttocks) to their respective index in the vector
body_parts_mapping = {
    "머리": (1, 2),      # head_count, head_length
    "팔": (3, 4),        # arms_count, arms_length
    "다리": (5, 6),      # legs_count, legs_length
    "몸통": (7, 8),      # torso_count, torso_length
    "엉덩이": (9, 10)    # buttocks_count, buttocks_length
}

# Populate the vector based on selected body parts and bruise data
for part in selected_body_parts:
    count_index, length_index = body_parts_mapping[part]
    output_vector[count_index] = bruise_data[f'{part}_count']  # Set the bruise count
    output_vector[length_index] = bruise_data[f'{part}_length']  # Set the bruise length

# 12. specific_shapes (Yes -> 0, No -> 1)
output_vector[11] = 0 if specific_shapes == 'Yes' else 1


# Section 2: Medical History Recording
st.subheader("2. 진료 영상")

st.button('녹화 시작')

# Section 3: AI Evaluation Questions
st.subheader("3. 문진 정보")

# Create columns for questions in pairs (same row for each pair of questions)
for _ in range(4):  # Loop through 4 times, each loop for one row with two questions
    col1, col2 = st.columns(2)

    with col1:
        # 왼쪽 열에 첫 4개 질문
        if _ == 0:
            # Injury cause provided by patient/guardian
            injury_cause = st.text_input(
                "환자/보호자가 주장하는 손상의 원인은 무엇인가요?"
            )

        if _ == 1:
            abuse_likely = st.radio(
                '환자/보호자가 제시한 손상 원인을 아동학대의 원인으로 볼 수 있나요?',
                ('예', '아니요', '유보')
            )
        elif _ == 2:
            match_explanation = st.radio(
                '문진 내용과 신체 진찰에서 알게 된 내용이 일치하나요?',
                ('예', '아니요', '유보')
            )
        elif _ == 3:
            developmental_stage = st.radio(
                '아이의 연령/발달 단계에서 일어날 수 있는 손상인가요?',
                ('예', '아니요', '유보')
            )

    with col2:
        # 오른쪽 열에 나머지 4개 질문
        if _ == 0:
            treatment_delayed = st.radio(
                '병원의 내원이 적절한 이유 없이 지체되었나요?',
                ('예', '아니요', '유보')
            )
        elif _ == 1:
            consistent_history = st.radio(
                '환자/보호자의 진술이 일치하나요?',
                ('예', '아니요', '유보')
            )
        elif _ == 2:
            poor_condition = st.radio(
                '환자의 의복, 청결, 영양상태가 눈에 띄게 불량한가요?',
                ('예', '아니요', '유보')
            )
        elif _ == 3:
            inappropriate_relationship = st.radio(
                '환자와 보호자와의 관계가 적절해 보이지 않나요?',
                ('예', '아니요', '유보')
            )

# Function to map responses
def map_response(response):
    if response == '예':
        return 1
    elif response == '아니요':
        return 0
    else:
        return None

# Create a 1D vector with the mapped values
items_mapped = [
    map_response(abuse_likely),
    map_response(match_explanation),
    map_response(developmental_stage),
    map_response(treatment_delayed),
    map_response(consistent_history),
    map_response(poor_condition),
    map_response(inappropriate_relationship)
]


# Display total number of bruises
total_bruises = sum([bruise_data.get(f'{part}_count', 0) for part in all_body_parts])
st.write(f"총 멍의 개수: {total_bruises}")

# Display maximum bruise lengths for each body part
for part in all_body_parts:
    if part in selected_body_parts:
        st.write(f"{part}: {bruise_data.get(f'{part}_length', 0)} cm")


# Mock result (AI decision score)
if st.button('AI 실행'):
    # This is a mock score, in reality, you'd connect this to your AI model
    st.subheader("AI 학대 의심률")
    abuse_risk_score = 63  # Replace this with real AI output
    abuse_cause = ["멍", 43, "진술", 13, "검사결과", 5, "동영상", 2]# Replace this with real AI output
    st.write(f"아동학대 의심률은 {abuse_risk_score}%입니다")
    st.write(f"가장 가능성이 높은 근거는 {abuse_cause[0]}(으)로 {abuse_cause[1]}% 관여합니다.")
    st.write(f"두번째 근거는 {abuse_cause[2]}(으)로 {abuse_cause[3]}% 관여합니다.")
    st.write(f"세번째 근거는 {abuse_cause[4]}(으)로 {abuse_cause[5]}% 관여합니다.")