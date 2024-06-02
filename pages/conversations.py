import streamlit as st
from st_audiorec import st_audiorec
import openai
import base64
from scripts.scripts import sidebar
from playsound import playsound

#initialize openai client
def setup_openai_client(api_key):
    return openai.OpenAI(api_key= api_key)

#transcribe audio to text
def transcribe_audio(client, audio_path):
    with open(audio_path, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(model = "whisper-1", file = audio_file)
        return transcript.text
    
#taking response from openai
def fetch_ai_response(client, input_text):
    messages = st.session_state['messages']
    response = client.chat.completions.create(model="gpt-4o-2024-05-13",messages=messages)
    return response.choices[0].message.content

#convert text to audio
def text_to_audio(client, text, audio_path):
    response = client.audio.speech.create(model="tts-1", voice= "nova", input = text)
    response.stream_to_file(audio_path)

def setup_session():
    with st.container(border=True):
        st.write("Hi. This modul allows you to train your speaking and listening skill with AI. The app will generate the converstation based on your library and the topics you have learned.")
        st.session_state.topic = st.text_input(label="If you want you can specify the topic you want to learn today.")
        if st.button("Start conversation"):
            system_prompt = f'''
                You are bot that is helping user to learn new language.
                You goal is to help user to learn new language by speaking thought conversation.
                Conversation should be adapted to the user level. 
                User words and phrases that user can understand.
                Add pauses between sentences to give user time to think. The conversation should be engaging and interesting.
                You output will be used to generate voice responses, so add pauses to make it sound natural.
                When running conversation answer user question, ask questions to keep the conversation going, give user feedback or small task. 
                Give a feedback to the user.
                User native language: {st.session_state.native_language}
                User learn language: {st.session_state.learn_language}
                User knowledge level: {st.session_state.knowledge_level}
                User name: {st.session_state.name}
                User topic: {st.session_state.topic}
                User knowledge base: {st.session_state.library}
            ''' 
            st.session_state['messages'].append({"role": "system", "content": system_prompt})
            st.session_state.session_start = True
def main():
    # Initiate sidebar
    sidebar()

    # Initiate session states
    if 'session_start' not in st.session_state:
        st.session_state.session_start = False

    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    #Show title and back button
    if st.button("Back to the main page"):
        st.switch_page("main.py")
    st.title("Learn Language By Speaking")

    # Show setup session
    if st.session_state.session_start == False:
      setup_session()

    if st.session_state.session_start == True:
        st.write(":microphone: Click on the voice recorder to interact with me. How can I assit you in learning a new language ?")
        # st.session_state.audio_bytes  = audio_recorder(
        #     text="Click on mic to start recording",
        #     pause_threshold=1.0,
        #     key=st.session_state.key_recorder,
        #     )

        recorded_audio = st_audiorec()
        #check if apo key is there
        api_key = st.session_state.openai_api_key
        if api_key:
            client = setup_openai_client(api_key)

            if recorded_audio:
                audio_file = "audio.mp3"
                with open(audio_file, "wb") as f:
                    f.write(recorded_audio)
                transcribed_text = transcribe_audio(client, audio_file)
                st.write("Trancribed Text: ",transcribed_text)

                # Update conversation history
                st.session_state['messages'].append({"role": "user", "content": transcribed_text})

                ai_response = fetch_ai_response(client, transcribed_text)
                st.session_state['messages'].append({"role": "assistant", "content": ai_response})

                # ai_response = fetch_ai_response(client, transcribed_text)
                response_audio_file = "ai_response.mp3"
                text_to_audio(client, ai_response, response_audio_file)
                
                st.audio(response_audio_file, autoplay=True)
                st.write("AI Response", ai_response)

if __name__ == "__main__":
    main()