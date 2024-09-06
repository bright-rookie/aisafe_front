import streamlit as st

# Title
st.title("AI-SAFE: Child Abuse Detection System")

# Section 1: Injury Information
st.subheader("1. Injury Information")
# Define the list of body parts
all_body_parts = ["Head", "Arms", "Legs", "Torso", "Buttocks"]

# Check if 'selected_body_parts' is in session state, if not initialize it
if 'selected_body_parts' not in st.session_state:
    st.session_state.selected_body_parts = []

# Create a row with the multiselect and the 'Select All' button on the same line
cols = st.columns([3, 1])  # First column wider for the multiselect, second for the button

# Place the multiselect in the first column
with cols[0]:
    selected_body_parts = st.multiselect(
        "Select body parts with bruises:",
        all_body_parts,
        default=st.session_state.selected_body_parts
    )

# Place the 'Select All' button in the second column
with cols[1]:
    if st.button('Select All'):
        st.session_state.selected_body_parts = all_body_parts
        selected_body_parts = all_body_parts

# Update the session state to store the selected body parts
st.session_state.selected_body_parts = selected_body_parts


# Dictionary to store user inputs for each body part
bruise_data = {}

# For each selected body part, show input fields for bruise count and max length on the same row
for part in selected_body_parts:
    cols = st.columns(2)
    with cols[0]:
        bruise_data[f'{part}_count'] = st.number_input(f'{part}: Bruise Count', min_value=0, max_value=10, value=0, key=f'{part}_count')
    with cols[1]:
        bruise_data[f'{part}_length'] = st.number_input(f'{part}: Max Bruise Length (cm)', min_value=0.0, max_value=50.0, value=0.0, key=f'{part}_length')

# Specific injury shapes
specific_shapes = st.radio(
    'Are there any specific injury shapes present?',
    ('Yes', 'No')
)

# Section 2: Medical History Recording
st.subheader("2. Medical History Recording")

st.button('Start Recording')

# Injury cause provided by patient/guardian
injury_cause = st.text_input(
    "What is the cause of the injury according to the patient/guardian?"
)

# Section 3: AI Evaluation Questions
st.subheader("3. AI Evaluation Questions")

# Is the cause likely due to child abuse?
abuse_likely = st.radio(
    'Is the provided cause likely due to child abuse?',
    ('Yes', 'No', 'Uncertain')
)

# Does the injury match the explanation provided?
match_explanation = st.radio(
    'Does the injury match the explanation provided?',
    ('Yes', 'No', 'Uncertain')
)

# Could the injury occur in the child’s developmental stage?
developmental_stage = st.radio(
    'Could the injury occur at the child’s developmental stage?',
    ('Yes', 'No', 'Uncertain')
)

# Was treatment delayed without a reasonable excuse?
treatment_delayed = st.radio(
    'Was treatment delayed without a reasonable excuse?',
    ('Yes', 'No', 'Uncertain')
)

# Is the child’s clothing, cleanliness, or nutrition noticeably poor?
poor_condition = st.radio(
    'Is the child’s clothing, cleanliness, or nutrition noticeably poor?',
    ('Yes', 'No', 'Uncertain')
)

# Does the relationship between the child and guardian seem inappropriate?
inappropriate_relationship = st.radio(
    'Does the relationship between the child and guardian seem inappropriate?',
    ('Yes', 'No', 'Uncertain')
)

# Display total number of bruises
total_bruises = sum([bruise_data.get(f'{part}_count', 0) for part in all_body_parts])
st.write(f"Total number of bruises: {total_bruises}")

# Display maximum bruise lengths for each body part
for part in all_body_parts:
    if part in selected_body_parts:
        st.write(f"{part}: {bruise_data.get(f'{part}_length', 0)} cm")

# Mock result (AI decision score)
if st.button('Run AI Detection'):
    # This is a mock score, in reality, you'd connect this to your AI model
    abuse_risk_score = 63  # Replace this with real AI output
    st.write(f"Abuse Detection Risk: {abuse_risk_score}%")

# 'Run AI Detection' 버튼 눌렀을 때 '판독문 업로드 완료'등 진행 상황 문구 출력
# 결과를 내게 만든 특성별 gradient순으로 나열, 판단의 근거 제시