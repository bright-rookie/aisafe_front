import streamlit as st


# Toggle the recording state
def toggle_recording():
    st.session_state.recording = not st.session_state.recording


def begin_recording():
    # Record button and state indicator
    col1, col2 = st.columns([1, 100])

    with col2:
        # Button toggles between '녹화 시작' and '녹화 종료'
        btn_text = "녹화 종료" if st.session_state.recording else "녹화 시작"
        if st.button(btn_text):
            toggle_recording()  # Toggle recording state

            # Show updated state immediately
            st.rerun()  # Call rerun to update UI

    with col1:
        # Show red circle if recording
        if st.session_state.recording:
            st.markdown('<span style="color: red;">●</span>', unsafe_allow_html=True)
        else:
            st.write(" ")  # Write blank to keep alignment
