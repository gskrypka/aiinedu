import streamlit as st
from openai import OpenAI
import openai
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Set OpenAI API key

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
) 

# Initiate session states
if 'quiz_started' not in st.session_state:
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
if 'library' not in st.session_state:
    st.session_state.library = []
    

# Generate images
def generate_images(prompt):
    st.write(prompt)
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
            )
        image_url = response.data[0].url
        print(image_url)
        return image_url
    except openai.OpenAIError as e:
        print(e.http_status)
        print(e.error)
        return "Imaage not generated"

# Generate quiz questions
def generate_quiz(topic, duration, input_language, subject):
    model = ChatOpenAI(model="gpt-4o")
    #Open file quiz_session_prompt.txt
    with open("prompts/quiz_session_prompt.txt", "r") as file:
        system_prompt = file.read()
        
    # Generate prompt
    user_prompt = ChatPromptTemplate.from_template("Genetarte quiz questions for a learning session on {topic} for {duration}. Subejct: {subject}. Knowledge: {knowledge}")
    prompt = SystemMessage(content=system_prompt) + user_prompt

    parser = JsonOutputParser()

    chain = prompt | model | parser
    output = chain.invoke({"input_language": input_language, "subject": subject, "topic": topic, "duration": duration, "knowledge": st.session_state.library})
    
    # Generate images:
    k = 0
    for i in output["quiz"]:
        if i["image"] == True:
            image_url = generate_images(i["image_prompt"])
            output["quiz"][k]["image_url"] = image_url
        k += 1
    return output




# Next question
def next_question():
    st.session_state.option_disabled = False
    if st.session_state.question_index == len(st.session_state.quiz["quiz"]) - 1:
        st.session_state.end = True
    else:
        st.session_state.question_index += 1

# Setup states to start quiz
def start_quiz():
    st.session_state.quiz_loading = False
    st.session_state.quiz_started = True
    st.rerun()

# Set states to load quiz
def load_quiz():
    st.session_state.quiz_loading = True

# Disable input
def disable_options():
    st.session_state.option_disabled = True

def llm_answer_checker(question, answer):
    model = ChatOpenAI(model="gpt-4o", temperature=0.1)
    parser = JsonOutputParser()

    # Open file quiz_llm_check_prompt.txt
    with open("prompts/quiz_llm_check_prompt.txt", "r") as file:
        system_prompt = file.read()
    # Generate prompt
    user_prompt = ChatPromptTemplate.from_template("Check if the answer to the question is correct. Question: {question}, User_answer: {answer}")
    prompt = SystemMessage(content=system_prompt) + user_prompt

    chain = prompt | model | parser
    output = chain.invoke({"question": question, "answer": answer})

    return output

def main():
    # Set title
    if st.button("Back to the main page"):
        st.switch_page("main.py")
    st.title("Quiz")

    # Generate quiz questions
    # Set input text
    if not st.session_state.quiz_started and not st.session_state.quiz_loading:
        st.session_state.topic = st.text_area("Do you have any preferences for the topic")
        # Select length of training session in minutes using dropdown
        st.session_state.duration = st.radio(
        "Select duration of the session",
        ["up to 5 minutes", "10-15 minutes", "15-30 minutes"])
        if st.button("Generate session"):
            load_quiz()
            st.rerun()
    
    # Generate quiz 
    if st.session_state.quiz_loading:
        st.write("Generating quiz...")
        st.write("Please wait, it might takes few seconds...")
        st.session_state.quiz = generate_quiz(st.session_state.topic, st.session_state.duration, "en", "japanese")
        st.session_state.question_amount = len(st.session_state.quiz["quiz"])
        start_quiz()

    # Display quiz questions
    if st.session_state.quiz_started and not st.session_state.quiz_loading:
        st.write("Topic: " + st.session_state.topic + "\nDuration: " + st.session_state.duration)
        
        if not st.session_state.end:
            with st.container(border=True):

                question = st.session_state.quiz["quiz"][st.session_state.question_index]["question"]
                input_type = st.session_state.quiz["quiz"][st.session_state.question_index]["input"]

                st.markdown(f"*Question {st.session_state.question_index + 1}/{st.session_state.question_amount}*")
                st.markdown(f"**{question}**")

                if st.session_state.quiz["quiz"][st.session_state.question_index]["image"] == True:
                    st.image(st.session_state.quiz["quiz"][st.session_state.question_index]["image_url"])
                    image_description = st.session_state.quiz["quiz"][st.session_state.question_index]["image_prompt"]

                if st.session_state.question_index == st.session_state.question_amount:
                    button_text = "Check results"
                else:
                    button_text = "Next question"

                if input_type == "buttons":
                    options = st.session_state.quiz["quiz"][st.session_state.question_index]["options"]
                    selected_option = st.radio("", options, index=None, on_change=disable_options, disabled=st.session_state.option_disabled)
                    if selected_option:
                        st.session_state.answers.append(selected_option)
                        if selected_option == st.session_state.quiz["quiz"][st.session_state.question_index]['correct_answer']:
                            st.success("Correct!")
                            st.session_state.correct_answers += 1
                        else:
                            st.error("Incorrect.")
                            st.write(f"*The correct answer is: {st.session_state.quiz['quiz'][st.session_state.question_index]['correct_answer']}*")
                        # If selected option is not empty
                        st.button(button_text, on_click=next_question)

                if input_type == "text":
                    answer = st.text_input("Answer:", disabled=st.session_state.option_disabled)
                    if st.button("Submit", on_click=disable_options, disabled=st.session_state.option_disabled):
                        st.session_state.answers.append(answer)
                        with st.spinner("Checking answer..."):
                            if st.session_state.quiz["quiz"][st.session_state.question_index]["image"] == True:
                                question = question + ", Image description: " + image_description
                            
                            output = llm_answer_checker(question, answer)
                        
                        if output["correct"]:
                            st.success("Correct!")
                            st.session_state.correct_answers += 1
                        else:
                            st.error("Incorrect.")
                            st.write(f"*{output['commentary']}*")
                        st.button(button_text, on_click=next_question)

        else:
            with st.container(border=True):
                st.header("You have completed the quiz!")
                st.subheader(f"Your score is: {st.session_state.correct_answers}/{len(st.session_state.quiz['quiz'])}")
                st.write("Would you like to start a new quiz?")
                if st.button("Start new quiz"):
                    st.session_state.answers = []
                    st.session_state.correct_answers = 0
                    st.session_state.question_index = 0
                    st.session_state.quiz_started = False
                    st.session_state.topic = None
                    st.session_state.duration = None
                    st.session_state.quiz = None
                    st.session_state.end = False
                    st.session_state.question_amount = 0
                    st.rerun()
   

if __name__ == "__main__":
    main()