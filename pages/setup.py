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
if 'topics' not in st.session_state:
    st.session_state.topics = []
if 'words' not in st.session_state:
    st.session_state.words = []

def get_image_base64(image_raw):
    buffered = BytesIO()
    image_raw.save(buffered, format=image_raw.format)
    img_byte = buffered.getvalue()

    return base64.b64encode(img_byte).decode("utf-8")

# Streamlit UI
st.title("Add to the library")

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

@st.experimental_dialog("Add topics")
def add_topic():
    st.text_area("Text", key="topic_input")
    if st.button("Add topics", key="add_topics"):
        st.session_state.topics.append(st.session_state.topic_input)
        st.rerun()

@st.experimental_dialog("Add words and phrases")
def add_words():
    st.text_area("Text", key="words_input")
    if st.button("Add words and phrases", key="add_words"):  
        st.session_state.words.append(st.session_state.words_input)
        st.rerun()

st.write("Add images or scan documents. All the data from the images will be added to the library.")
if st.button("Upload images"):
    upload_images()
if st.button("Scan document"):
    scan()
st.write("Add topics and we will automatically generate words and phrases for you to learn.")
if st.button("Add topics"):
    add_topic()
st.write("Upload words or phrases you want to learn.")
if st.button("Add words and phrases"):
    add_words()


# Image list
st.subheader("Materials to be added to the library:")
col1, col2, col3 = st.columns([0.2,0.3,0.5])

# Combine all the topics in a single string
topics_string = ""
for i in st.session_state.topics:
    topics_string = topics_string + "\n* " + i

# Combine all the words in a single string
words_string = ""
for i in st.session_state.words:
    words_string = words_string + "\n* " + i    

with col1:
    st.write("Images:")
    for i in st.session_state.image_list:
        st.image(i)

with col2:
    st.write("Topics:")
    st.write(topics_string)

with col3:
    st.write("Words and phrases:")
    st.write(words_string)


if st.button("Submit"):
    if st.session_state.image_list:
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
        if st.session_state.image_list:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=st.session_state.messages,
                )
            except openai.OpenAIError as e:
                st.write(e)
                st.write("Error in generating response")



#if st.button("Add"):
 #   for i in images:
  #      st.session_state.image_list.append(i)      
   #     raw_img = Image.open(i)
    #   img = get_image_base64(raw_img)
     #   img_type = i.type
     #   st.session_state.messages.append(
      #                          {
       #                             "role": "user",
        #                            "content": [
         #                               {
          #                                  "type": "image_url",
           #                                 "image_url": {
            #                                    "url": f"data:{img_type};base64,{img}"
             #                               },
              #                          }
               #                     ],
                #                }
                 #           )