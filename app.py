import streamlit as st
from scripts.scripts import reset_quiz, sidebar

# Introduction screen
def show_introduction():
    st.title("Anki Cards on Steroids: Revolutionize Your Study Routine with Custom Exercises")
    st.write("""
    Imagine transforming your study notes into a dynamic learning experience that goes beyond traditional flashcards. 
    Welcome to the world of Anki cards on steroids—a cutting-edge approach that takes your Anki cards to the next level. 
    With this innovative tool, you can scan your notes to generate custom exercises tailored to your learning needs. 
    Whether you’re looking to practice conversations, improve your listening skills, or engage in interactive exercises, 
    this method allows you to personalize your study sessions like never before. Say goodbye to monotonous repetition 
    and hello to a more engaging, effective way to master new information. Dive in and discover how you can supercharge 
    your learning with Anki cards on steroids!
    """)
    if st.button("Get Started"):
        st.session_state.page = "user_input"
        st.rerun()

# User input screen
def user_input():
    st.title("Tell Us About Yourself")
    
    native_language = st.selectbox("What's your native language?", ["English", "Japanese", "Spanish"])
    name = st.text_input("Name")
    learn_language = st.selectbox("What do you want to learn?", ["Spanish", "Japanese", ])
    knowledge_level = st.selectbox("Knowledge level", ["Beginner", "Intermediate", "Expert"])

    if st.button("Next"):
        st.session_state.native_language = native_language
        st.session_state.name = name
        st.session_state.learn_language = learn_language
        st.session_state.knowledge_level = knowledge_level
        st.session_state.page = "confirmation"
        st.rerun()

# Confirmation screen
def confirmation():
    st.title("Confirmation")
    st.write(f"Name: {st.session_state.name}")
    st.write(f"Native Language: {st.session_state.native_language}")
    st.write(f"Language to Learn: {st.session_state.learn_language}")
    st.write(f"Knowledge Level: {st.session_state.knowledge_level}")
    if st.button("Next"):
        st.session_state.page = "main"
        st.rerun()

def main_page():
    st.title("Anki cards on steroids")

    # Manage you library
    st.header("Manage your library")
    col1, col2, col3, col4 = st.columns(4)
    with col1: 
        st.write("Scan images and add words and phrases to your library.")

    with col2:
        st.write("Add topics and we will automatically generate words and phrases for you to learn.")

    with col3:
        st.write("Upload words or phrases you want to learn.")

    with col4:
        st.write("Check your library")
    

    col11, col12, col13, col14 = st.columns(4)

    with col11: 
        if st.button("Add from images"):
            st.switch_page("pages/add_images.py")

    with col12:
        st.button("Add topics")

    with col13:
        st.button("Add words and phrases")

    with col14:
        if st.button("Check library"):
            st.switch_page("pages/library.py")


    st.header("Exercises and quizes")
    st.write("Select a type of exercises and train your knowledge")


    with st.container(border=True):
        st.markdown("#### Vocabulary and grammatics")
        st.write("Learn words and phrases, practice grammar")
        if st.button("Take a test"):
            st.switch_page("pages/quiz.py")
        
    with st.container(border=True):
        st.markdown("#### Listening and speaking")
        st.write("Improve your listening and speaking skills")
        if st.button("Start conversation"):
            st.switch_page("pages/conversations.py")

# Main function to control the app flow
def main():
    reset_quiz()
    sidebar()
    if 'page' not in st.session_state:
        st.session_state.page = "introduction"
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = ""

    if st.session_state.page == "introduction":
        show_introduction()
    elif st.session_state.page == "user_input":
        user_input()
    elif st.session_state.page == "confirmation":
        confirmation()
    elif st.session_state.page == "main":
        main_page()


if __name__ == "__main__":
    main()
