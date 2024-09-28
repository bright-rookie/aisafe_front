from PIL import Image, ImageDraw, ImageFont
import streamlit as st
import pandas as pd
import numpy as np
import time
import re
import os

# Title
st.title("AI-SAFE: 아동학대 선별 시스템")

# Section 0: Patient Number Input
st.subheader("Patient Information")

# Input field for patient number
patient_number = st.number_input("환자 번호를 입력해주세요:", value = 1, min_value = 1 , step=1)

# Vectore creation
bruise_vector = [0] * 11  # Initialize a 1x12 vector with zeros


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
    ('예', '아니오')
)

# Mapping for each body part (head, arms, legs, torso, buttocks) to their respective index in the vector
body_parts_mapping = {
    "머리": (0, 1),      # head_count, head_length
    "팔": (2, 3),        # arms_count, arms_length
    "다리": (4, 5),      # legs_count, legs_length
    "몸통": (6, 7),      # torso_count, torso_length
    "엉덩이": (8, 9)    # buttocks_count, buttocks_length
}

# Populate the vector based on selected body parts and bruise data
for part in selected_body_parts:
    count_index, length_index = body_parts_mapping[part]
    bruise_vector[count_index] = bruise_data[f'{part}_count']  # Set the bruise count
    bruise_vector[length_index] = bruise_data[f'{part}_length']  # Set the bruise length

# 12. specific_shapes (Yes -> 0, No -> 1)
bruise_vector[10] = 0 if specific_shapes == 'Yes' else 1

# Section 2: Medical History Recording
st.subheader("2. 진료 영상")

# Check if 'recording' is in the session state, if not initialize it
if 'recording' not in st.session_state:
    st.session_state.recording = False

# Toggle the recording state
def toggle_recording():
    st.session_state.recording = not st.session_state.recording

# Record button and state indicator
col1, col2 = st.columns([1, 4])

with col1:
    # Show red circle if recording
    if st.session_state.recording:
        st.markdown('<span style="color: red;">●</span>', unsafe_allow_html=True)
    else:
        st.write(" ")  # Write blank to keep alignment

with col2:
    # Button toggles between '녹화 시작' and '녹화 종료'
    btn_text = "녹화 종료" if st.session_state.recording else "녹화 시작"
    if st.button(btn_text):
        toggle_recording()

# Section 3: AI Evaluation Questions
st.subheader("3. 문진 정보")

# Create columns for questions in pairs (same row for each pair of questions)
for _ in range(5):  # Loop through 4 times, each loop for one row with two questions
    col1, col2 = st.columns(2)

    with col1:
        # 왼쪽 열에 첫 5개 질문
        if _ == 0:
            # Injury cause provided by patient/guardian
            injury_cause = st.text_input(
                "환자/보호자가 주장하는 손상의 원인은 무엇인가요?"
            )
        elif _ == 1:
            consciousness_state = st.radio(
                '환자가 의식이 있는 상태인가요?',
                ('예', '아니오')
            )            
        elif _ == 2:
            guardian_status = st.radio(
                '현재 환자의 보호자는 누구인가요?',
                ('부모', '한부모', '부모 외 타인', '없음')
            )                      
        elif _ == 3:
            abuse_likely = st.radio(
                '환자/보호자가 제시한 손상 원인을 아동학대의 원인으로 볼 수 있나요?',
                ('예', '아니오', '유보')
            )  
        elif _ == 4:
            match_explanation = st.radio(
                '문진 내용과 신체 진찰에서 알게 된 내용이 일치하나요?',
                ('예', '아니오', '유보')
            )


    with col2:
        # 오른쪽 열에 나머지 5개 질문
        if _ == 0:
            developmental_stage = st.radio(
                '아이의 연령/발달 단계에서 일어날 수 있는 손상인가요?',
                ('예', '아니오', '유보')
            )
        elif _ == 1:
            treatment_delayed = st.radio(
                '병원의 내원이 적절한 이유 없이 지체되었나요?',
                ('예', '아니오', '유보')
            )
        elif _ == 2:
            consistent_history = st.radio(
                '환자/보호자의 진술이 일치하나요?',
                ('예', '아니오', '유보')
            )            
        elif _ == 3:
            poor_condition = st.radio(
                '환자의 의복, 청결, 영양상태가 눈에 띄게 불량한가요?',
                ('예', '아니오', '유보')
            )
        elif _ == 4:
            inappropriate_relationship = st.radio(
                '환자와 보호자와의 관계가 적절해 보이지 않나요?',
                ('예', '아니오', '유보')
            )

# Function to map responses
def map_response(response):
    if response == '예':
        return 1
    elif response == '아니오':
        return 0
    elif response == '유보':
        return None
    elif response == '부모':
        return 0
    elif response == '한부모':
        return 1
    elif response == '부모 외 타인':
        return 2
    elif response == '없음':
        return 3
    else: 
        return None

# Create a 1D vector with the mapped values
response_vector = [
    map_response(consciousness_state),
    map_response(guardian_status),
    map_response(abuse_likely),
    map_response(match_explanation),
    map_response(developmental_stage),
    map_response(treatment_delayed),
    map_response(consistent_history),
    map_response(poor_condition),
    map_response(inappropriate_relationship)
]

# Section 4: Load EMR data
st.subheader("4. 기존 데이터 불러오기")
col1, col2 = st.columns(2)

# Placeholder to store upload success message
info_uploaded = False
xray_uploaded = False
lab_uploaded = False
if 'emr_uploaded' not in st.session_state:
    st.session_state.emr_uploaded = False

# 1) Basic Information via CSV Upload
with col1:
    st.markdown("**기본 정보**")
    basic_info_file = st.file_uploader("기본 정보를 업로드하세요 (CSV)", type=["csv"])

    if basic_info_file is not None:
        try:
            # Read CSV
            basic_info_df = pd.read_csv(basic_info_file)
            
            # 필요한 컬럼들
            required_columns = ['patient_number', 'age_months', 'sex', 'height_cm', 'weight_kg']

            # 필수 컬럼들이 존재하는지 확인
            if set(required_columns).issubset(basic_info_df.columns):
                patient_number = 1  # 예를 들어 첫 번째 환자만 필터링한다고 가정
                filtered_df = basic_info_df[basic_info_df['patient_number'] == patient_number]
                
                if not filtered_df.empty:
                    st.success("기본 정보가 성공적으로 업로드되었습니다!")
                    info_vector = filtered_df.drop(columns=['patient_number']).values.flatten()

                    # 환자의 기본 정보 추출
                    patient_age = info_vector[0]
                    patient_sex = int(info_vector[1])
                    if patient_sex == 0: patient_sex1 = "남"
                    elif patient_sex == 1: patient_sex2 = "여"
                    patient_height = info_vector[2]
                    patient_weight = info_vector[3]
                    
                    info_uploaded = True
                else:
                    st.error("CSV 파일에 필요한 기본 정보가 포함되어 있지 않습니다. (연령, 성별, 키, 체중)")
            else:
                st.error("CSV 파일에 필요한 기본 컬럼이 포함되어 있지 않습니다.")

        except Exception as e:
            st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {e}")

    # 2. 표준 성장 데이터 로드 함수
    def load_growth_data(sex, data_type):
        # 성별과 데이터 타입에 따라 파일 선택
        if sex == 0 and data_type == 'height':
            file_path = 'csv/height_male.csv'
        elif sex == 1 and data_type == 'height':
            file_path = 'csv/height_female.csv'
        elif sex == 0 and data_type == 'weight':
            file_path = 'csv/weight_male.csv'
        elif sex == 1 and data_type == 'weight':
            file_path = 'csv/weight_female.csv'
        else:
            return None

        # 해당 CSV 파일 로드
        return pd.read_csv(file_path)

    # 3. 환자의 값을 퍼센타일 구간에 맞추어 선형 보간법으로 계산하는 함수
    def calculate_percentile(value, age_data):
        percentiles = age_data.columns[1:].astype(float)  # 퍼센타일 구간 (1%, 3%, 5%, ...)
        
        # 퍼센타일 값에 해당하는 데이터 (height 또는 weight)
        values = age_data.iloc[0, 1:].values.astype(float)
        
        # 만약 주어진 값이 값의 최소값보다 작으면 1% 미만
        if value <= values[0]:
            return f"{percentiles[0]}th 이하"

        # 만약 주어진 값이 값의 최대값보다 크면 최대 퍼센타일 이상
        if value >= values[-1]:
            return f"{percentiles[-1]}th 이상"

        # 두 값 사이에서 선형 보간법 적용
        for i in range(len(values) - 1):
            if values[i] <= value <= values[i+1]:
                # 선형 보간법 공식 적용
                lower_bound = values[i]
                upper_bound = values[i+1]
                lower_percentile = percentiles[i]
                upper_percentile = percentiles[i+1]
                
                # 선형 보간 계산
                percentile = lower_percentile + ((value - lower_bound) / (upper_bound - lower_bound)) * (upper_percentile - lower_percentile)
                return f"{percentile:.2f}th"

        return None

    # 4. 환자의 키/체중 퍼센타일을 계산하는 함수
    def get_percentiles(patient_age, patient_sex, patient_height, patient_weight):
        # 표준 데이터 로드
        height_data = load_growth_data(patient_sex, 'height')
        weight_data = load_growth_data(patient_sex, 'weight')

        if height_data is None or weight_data is None:
            st.error("성장 데이터 파일을 찾을 수 없습니다.")
            return None, None

        # 연령에 따른 데이터 필터링 (데이터 타입을 명시적으로 정수로 변환하여 비교)
        height_data['Age(Months)'] = height_data['Age(Months)'].astype(int)
        weight_data['Age(Months)'] = weight_data['Age(Months)'].astype(int)
        patient_age = int(patient_age)  # 데이터 타입 일치
        
        # 필터링 후 데이터 확인
        filtered_height = height_data[height_data['Age(Months)'] == patient_age]
        filtered_weight = weight_data[weight_data['Age(Months)'] == patient_age]

        if filtered_height.empty or filtered_weight.empty:
            st.error("해당 연령에 맞는 표준 데이터를 찾을 수 없습니다.")
            return None, None

        # 환자의 키와 체중 퍼센타일 계산
        height_percentile = calculate_percentile(patient_height, filtered_height)
        weight_percentile = calculate_percentile(patient_weight, filtered_weight)

        return height_percentile, weight_percentile

    # 5. 퍼센타일 출력
    if info_uploaded:
        height_percentile, weight_percentile = get_percentiles(patient_age, patient_sex, patient_height, patient_weight)

        if height_percentile is not None and weight_percentile is not None:
            # 키와 체중 옆에 퍼센타일을 괄호로 표시
            st.write(f"환자 번호: {patient_number}")
            st.write(f"연령: {patient_age} 개월")
            st.write(f"성별: {'남' if patient_sex == 0 else '여'}")
            st.write(f"키: {patient_height} cm ({height_percentile})")
            st.write(f"체중: {patient_weight} kg ({weight_percentile})")

# 2) Lab Data Upload
with col2:
    st.markdown("**Lab 데이터**")
    lab_data = st.file_uploader("Lab 데이터를 업로드하세요 (CSV)", type=["csv"])

    if lab_data is not None:
        try:
            # Read the CSV file
            lab_data_df = pd.read_csv(lab_data)
            
            # Ensure the necessary columns are present
            required_columns = ['patient_number', 'CBC_RBC', 'CBC_WBC', 'CBC_Platelet', 'Hb', 'PT_INR', 'aPTT', 
                                'AST', 'ALT', 'ALP', 'Na', 'K', 'Cl', 'Calcium', 'Phosphorus', '25hydroxyvitaminD', 
                                'Serum_albumin', 'Pre_albumin', 'Transferrin', 'Glucose']
            
            if set(required_columns).issubset(lab_data_df.columns):
                # Filter the data by patient number
                patient_data = lab_data_df[lab_data_df['patient_number'] == patient_number]
                
                if not patient_data.empty:
                    # Drop the 'patient_number' column and convert the rest to a 1x20 vector
                    lab_vector = patient_data.drop(columns=['patient_number']).values.flatten()
                    lab_uploaded = True
                    st.success("Lab 데이터가 성공적으로 업로드 되었습니다!")
                else:
                    st.warning(f"환자 번호 {patient_number}에 해당하는 데이터가 없습니다.")
            else:
                st.error("CSV 파일에 필요한 컬럼들이 포함되어 있지 않습니다.")
        
        except Exception as e:
            st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {e}")


# 3) X-ray Report Upload

# Function to process uploaded files

def process_xray_text(files, input_patient_number):
    body_parts = ['skull', 'arms', 'legs', 'torso', 'pelvis']
    xray_data = {part: 'NULL' for part in body_parts}  # Default to 'NULL' for all parts
    
    for file in files:
        # Extract patient number and part name from the filename
        filename = file.name
        file_patient_number = filename.split('_')[0]  # First part is patient number
        part_name = filename.split('_')[1].replace('.txt', '')  # Second part is body part name

        # Check if the patient number matches the input patient number
        if str(file_patient_number) != str(input_patient_number):
            st.error(f"파일 {filename}의 환자 번호가 현재 진료 중인 환자 번호와 일치하지 않습니다.")
            return None
        
        # Check if the part name is valid
        if part_name in body_parts:
            # Read file content
            file_content = file.read().decode("utf-8")
            xray_data[part_name] = file_content if file_content.strip() else 'NULL'
        else:
            st.error(f"파일 {filename}에 부위 이름이 잘못되었습니다: {part_name}")
            return None
    
    # Format the combined content
    xray_report_text = f"patient_number: {input_patient_number}\n"
    for part in body_parts:
        xray_report_text += f"{part}: {xray_data[part]}\n"

    return xray_report_text

def get_fracture_count(text):
    if text == "NULL":
        return 0

    # Check for explicit no fracture statements
    no_fracture_patterns = ["no evidence of", "no fracture"]
    for pattern in no_fracture_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return 0

    # Check for multiple fractures
    multiple_patterns = ["multiple", "various", "several", "healing", "healed", "callus", "prior"]
    for pattern in multiple_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return 2

    # Check for single fractures
    single_pattern = ["fracture"]
    for pattern in single_pattern:
        if re.search(pattern, text, re.IGNORECASE):
            return 1


def check_specific_fracture(text, fracture_type):
    if text == "NULL":
        return 0
    if re.search(fracture_type, text, re.IGNORECASE):
        return 1
    return 0


def parse_report(text):
    if not text:
        return {"skull": "", "torso": "", "arms": "", "legs": "", "pelvis": ""}  # 기본 빈 값

    report_sections = {
        "skull": "",
        "torso": "",
        "arms": "",
        "legs": "",
        "pelvis": ""
    }

    # Use regular expressions to extract sections
    for section in report_sections:
        pattern = f"{section}:\\s*(.*?)(?=\\n\\w+:|$)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            report_sections[section] = match.group(1).strip()

    return report_sections

def generate_xray_vector(text):
    report = parse_report(text)

    skull = 0
    ribs = 0
    radius_ulna = 0
    humerus = 0
    tibia_fibula = 0
    femur = 0
    spiral_fx = 0
    metaphyseal_fx = 0

    skull = get_fracture_count(report.get("skull", "NULL"))
    ribs = get_fracture_count(report.get("torso", "NULL"))
    pelvis = get_fracture_count(report.get("pelvis", "NULL"))

    if "radius" in report.get("arms", "").lower() or "ulna" in report.get("arms", "").lower():
        radius_ulna = get_fracture_count(report.get("arms", ""))
    if "humerus" in report.get("arms", "").lower():
        humerus = get_fracture_count(report.get("arms", ""))
    
    # Separate femur and tibia_fibula based on their specific mentions
    if "tibia" in report.get("legs", "").lower() or "fibula" in report.get("legs", "").lower():
        tibia_fibula = get_fracture_count(report.get("legs", ""))
    if "femur" in report.get("legs", "").lower():
        femur = get_fracture_count(report.get("legs", ""))
    
    # Check for specific fracture types
    spiral_fx = check_specific_fracture(report.get("arms", "") + report.get("legs", ""), "spiral fracture")
    metaphyseal_fx = check_specific_fracture(report.get("arms", "") + report.get("legs", ""), "metaphyseal fracture")
    
    return [skull, ribs, humerus, radius_ulna, femur, tibia_fibula, pelvis, spiral_fx, metaphyseal_fx]

# X-ray reports upload
st.markdown("**X-ray 판독문**")
xray_text = st.file_uploader("X-ray 판독문을 업로드하세요 (TXT)", type=["txt"], accept_multiple_files=True)

xray_report = None  # xray_report 변수를 미리 None으로 정의

if xray_text:
    # Process the uploaded reports
    xray_report = process_xray_text(xray_text, patient_number)
    
    if xray_report:
        # Display the combined report
        st.success("X-ray 판독문이 성공적으로 업로드 되었습니다!")
        st.text_area("합쳐진 X-ray 판독문:", value=xray_report, height=100)
        xray_uploaded = True
    else:
        st.error("X-ray 판독문 처리에 실패했습니다.")

# X-ray vector 생성은 xray_report가 None이 아니고 문자열일 때만 실행
if xray_report and isinstance(xray_report, str):
    xray_vectors = generate_xray_vector(xray_report)
    st.text_area("X-ray vector를 확인하세요", value=xray_vectors, height=100)

# Submit button to confirm uploads
if st.button("EMR 데이터 업로드 확인"):
    if info_uploaded and xray_uploaded and lab_uploaded:
        st.session_state.emr_uploaded = True
        st.success("EMR 데이터가 성공적으로 업로드되었습니다!")
        
    else:
        st.error("모든 필드를 올바르게 업로드해주세요.")

# Mock result (AI decision score)
if st.button('AI 실행'):
    if st.session_state.emr_uploaded:
        # This is a mock score, in reality, you'd connect this to your AI model
        with st.spinner('AI 분석 중입니다...'):
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.05)  # AI 분석 작업 시뮬레이션
                progress.progress(i + 1)
        st.subheader("AI 학대 의심률")
        abuse_risk_score = 63  # Replace this with real AI output
        abuse_cause = ["멍", 43, "진술", 13, "검사결과", 5, "동영상", 2]# Replace this with real AI output
        st.write(f"아동학대 의심률은 {abuse_risk_score}%입니다")
        st.write(f"가장 가능성이 높은 근거는 {abuse_cause[0]}(으)로 {abuse_cause[1]}% 관여합니다.")
        st.write(f"두번째 근거는 {abuse_cause[2]}(으)로 {abuse_cause[3]}% 관여합니다.")
        st.write(f"세번째 근거는 {abuse_cause[4]}(으)로 {abuse_cause[5]}% 관여합니다.")
    else:
        st.error("EMR 업로드 확인을 먼저 수행해주십시오.")

# 'Run AI Detection' 버튼 눌렀을 때 '판독문 업로드 완료'등 진행 상황 문구 출력
# 결과를 내게 만든 특성별 gradient순으로 나열, 판단의 근거 제시