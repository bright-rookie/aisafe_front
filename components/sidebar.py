import streamlit as st


def sidebar(bruise_vector, info_vector, patient_number):
    # Add a sidebar for the table of contents and data preview
    with st.sidebar:
        st.header("Data Review")
        st.markdown("### Basic Information")
        sex_to_str = ["남", "여"]
        if info_vector:
            st.markdown(
                f"**Patient ID**: {patient_number[0]} \n **Age**: {info_vector[0]} (Mo) \n **Sex**: {sex_to_str[info_vector[1]]} \n **Height**: {info_vector[2]} Percentile \n **Weight**: {info_vector[3]} Percentile"
            )
        st.markdown("### Bruising")
        areas = ["Head", "Arm", "Leg", "Torso", "Buttocks"]
        for i, pair in enumerate(zip(bruise_vector[::2], bruise_vector[1::2])):
            count, size = pair
            if count > 0 and size > 0:
                st.markdown(
                    f"**{count}** bruises with **{size}** cm on the **{areas[i]}**"
                )
        st.markdown("*Powered by [AISAFE](https://github.com/bright-rookie)*")
