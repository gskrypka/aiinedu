import streamlit as st

if 'library' not in st.session_state:
    st.session_state.library = []

if st.button("Back to the main page"):
    st.switch_page("app.py")
st.title("Your library")
st.write("Here you can manage your library of words and phrases.")
st.write(st.session_state.library)