import streamlit as st

def reset_quiz():
    st.session_state.answers = []
    st.session_state.correct_answers = 0
    st.session_state.question_index = 0
    st.session_state.quiz_started = False
    st.session_state.topic = None
    st.session_state.duration = None
    st.session_state.quiz = None
    st.session_state.end = False
    st.session_state.quiz_loading = False
    st.session_state.option_disabled = False
    st.session_state.question_amount = 0
    st.session_state['messages'] = []
    st.session_state.session_start = False

def sidebar():
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = ""

    if st.session_state.openai_api_key == "":
        st.error("Please provide your OpenAI API Key to use this app.")
    
    with st.sidebar:
        st.text_input(
            "Paste your OpenAI API Key (https://platform.openai.com/). Remember you need GPT-4o to use this app.",
            value=st.session_state.openai_api_key,
            type="password", key="openai_api_key_input"
            )
        if st.button("Save"):
            st.session_state.openai_api_key = st.session_state.openai_api_key_input
            st.rerun()
        with st.expander("Here is image with Japane words for testing purposes", expanded=False):
            st.image("example.jpg")