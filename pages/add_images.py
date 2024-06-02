import streamlit as st
from openai import OpenAI
import openai
from dotenv import load_dotenv
import os
import base64
from PIL import Image
from io import BytesIO


# Set OpenAI API key
load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
) 

# Initiate session states
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'image_list' not in st.session_state:
    st.session_state.image_list = []
if 'words_from_images' not in st.session_state:
    st.session_state.words_from_images = []
if 'library' not in st.session_state:
    st.session_state.library = []
if 'image_submit_disabled' not in st.session_state:
    st.session_state.image_submit_disabled = False

def get_image_base64(image_raw):
    buffered = BytesIO()
    image_raw.save(buffered, format=image_raw.format)
    img_byte = buffered.getvalue()

    return base64.b64encode(img_byte).decode("utf-8")

def transcribe():
    if st.session_state.image_list:
                st.session_state.image_submit_disabled = True
                image_prompt = "You are helping student to make material from learning. You goal is to transcribe all the topics, words, phrases from the image relevant to the process of learning."
                for i in st.session_state.image_list:
                    raw_img = Image.open(i)
                    img = get_image_base64(raw_img)
                    img_type = i.type
                    st.session_state.messages.append(
                                            {
                                                "role": "user",
                                                "content": [
                                                    {"type": "text", "text": image_prompt},
                                                    {
                                                        "type": "image_url",
                                                        "image_url": {
                                                            "url": f"data:{img_type};base64,{img}"
                                                        },
                                                    }
                                                ],
                                            }
                                        )
                with st.spinner(text="Processing images..."):
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=st.session_state.messages,
                        )
                        st.session_state.words_from_images.append(response.choices[0].message.content)
                    except openai.OpenAIError as e:
                        st.write(e)
                        st.write("Error in generating response")
                st.session_state.image_submit_disabled = False
                st.rerun()

def disable_submit():
    st.session_state.image_submit_disabled = True

def add_to_library():
    for i in st.session_state.words_from_images:
        st.session_state.library.append(i)
    st.session_state.words_from_images = []
    st.session_state.image_list = []
    st.session_state.messages = []
    st.toast("Added to library", icon="✅")

@st.experimental_dialog("Upload images")
def upload_images():
    st.file_uploader("Upload your image", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="image_uploader")
    if st.session_state.image_uploader:
            if st.button("Add"):
                for i in st.session_state.image_uploader:
                    st.session_state.image_list.append(i)
                st.rerun()


@st.experimental_dialog("Scan document")
def scan():
    st.camera_input(label="Use your camera to take a picture", key="camera_input")
    if st.session_state.camera_input:
       if st.button("Add image"):  
           st.session_state.image_list.append(st.session_state.camera_input)
           st.rerun()


# Streamlit UI
if st.button("Back to the main page"):
    st.switch_page("main.py")
st.title("Add words and phrases to the library from images")

st.write("Add images or scan documents. All the data from the images will be added to the library.")
if st.button("Upload images", disabled=st.session_state.image_submit_disabled):
    upload_images()
if st.button("Scan document", disabled=st.session_state.image_submit_disabled):
    scan()

# Image list
if st.session_state.image_list:
    with st.container(border=True):
        st.subheader("Images to process")
        if st.button("Clear images", disabled=st.session_state.image_submit_disabled):
            st.session_state.image_list = []
        col1, col2, col3 = st.columns([0.2,0.3,0.5])

        with col1:
            st.write("Images:")
            for i in st.session_state.image_list:
                st.image(i)

        if st.button("Submit", disabled=st.session_state.image_submit_disabled, on_click=disable_submit):
            transcribe()
            


if st.session_state.words_from_images:
    st.subheader("Words and phrases from the images")
    for i in st.session_state.words_from_images:
        st.write(i)
    st.button("Add to the library", on_click=add_to_library)