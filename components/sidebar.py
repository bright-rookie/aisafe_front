import streamlit as st


def sidebar(bruise_vector, info_vector, patient_number):
    # Add a sidebar for the table of contents and data preview
    with st.sidebar:
        st.header("Navigation")
        st.markdown("[1. EMR 업로드](#cb224b0a)")
        st.markdown("[2. 멍 정보](#28468c68)")
        st.markdown("[3. 진료 영상](#56764aab)")
        st.markdown("[4. 문진 정보](#b327ee4d)")


        st.header("Data Review")
        st.markdown("- **환자 기본 정보**")
        sex_to_str = ["남", "여"]
        if info_vector is not None:
            st.markdown(
                f"""**환자 번호**: {patient_number} <br>
                **나이**: {info_vector[0]} (개월) <br>
                **성별**: {sex_to_str[int(info_vector[1])]} <br>
                **키**: {info_vector[2]} cm <br>
                **몸무게**: {info_vector[3]} kg""",
                unsafe_allow_html=True
)

        st.markdown("- **멍 정보**")
        areas = ["머리", "팔", "다리", "몸통", "엉덩이"]
        for i, pair in enumerate(zip(bruise_vector[::2], bruise_vector[1::2])):
            count, size = pair
            if count > 0 and size > 0:
                st.markdown(
                    f"**{areas[i]}**에 최대 길이 **{size}cm** 멍이 **{count}**개 있습니다."
                    )
        st.markdown("*Powered by [AISAFE](https://github.com/bright-rookie)*")
