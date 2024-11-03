import streamlit as st


# Map responses to values
def map_response(response):
    return {
        "예": 0,
        "아니오": 1,
        "유보": None,
        "부모": 0,
        "한부모": 1,
        "부모 외 타인": 2,
        "없음": 3,
    }.get(response, None)


def get_history():
    questions = [
        "환자/보호자가 주장하는 손상의 원인은 무엇인가요?",
        "환자가 의식이 정상인가요?",
        "현재 환자의 보호자는 누구인가요?",
        "손상 원인을 아동학대로 볼 수 있나요?",
        "문진 내용과 신체 진찰이 일치하나요?",
        "아이의 연령/발달 단계에서 일어날 수 있는 손상인가요?",
        "병원의 내원이 적절한 이유 없이 지체되었나요?",
        "환자/보호자의 진술이 일치하나요?",
        "환자의 의복, 청결, 영양상태가 눈에 띄게 불량한가요?",
        "환자와 보호자와의 관계가 적절해 보이지 않나요?",
    ]

    options = [
        ["부모", "한부모", "부모 외 타인", "없음"],
        ["예", "아니오", "유보"],
    ]
    col1, col2 = st.columns(2)
    responses = []
    with col1 :
        for i in range(5) :
            if i == 0 :
                claim = st.text_input(questions[0])
            elif i == 2 :
                responses.append(st.radio(questions[2], options[0]))
            else :
                responses.append(st.radio(questions[i], options[1]))

    with col2 :
        for i in range(5, 10) :
            responses.append(st.radio(questions[i], options[1]))

    # Create response vector
    response_vector = [map_response(x) for x in responses]

    return response_vector
