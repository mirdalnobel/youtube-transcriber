import streamlit as st
import youtube_dl
import requests
from time import sleep
import openai

# Set your OpenAI API key
openai.api_key = 'your_openai_api_key'

if 'status' not in st.session_state:
    st.session_state['status'] = 'submitted'

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'ffmpeg-location': './',
    'outtmpl': "./%(id)s.%(ext)s",
}

# OpenAI API endpoint
openai_api_endpoint = "https://api.openai.com/v1/engines/whisper-large/completions"

@st.cache
def transcribe_from_link(link, categories: bool):
    _id = link.strip()

    def get_vid(_id):
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(_id)

    # download the audio of the YouTube video locally
    meta = get_vid(_id)
    save_location = meta['id'] + ".mp3"

    print('Saved mp3 to', save_location)

    def read_file(filename):
        with open(filename, 'rb') as _file:
            while True:
                data = _file.read(5242880)  # Use a constant chunk size
                if not data:
                    break
                yield data

    # Read audio file
    audio_data = "".join(chunk.decode('latin-1') for chunk in read_file(save_location))

    # Transcribe using OpenAI API
    response = openai.Completion.create(
        engine="whisper-large",
        prompt=audio_data,
        temperature=0.5,
        max_tokens=500,
    )

    transcript = response.choices[0].text.strip()

    return transcript

def refresh_state():
    st.session_state['status'] = 'submitted'

st.title('Easily transcribe YouTube videos')

link = st.text_input('Enter your YouTube video link', 'https://youtu.be/dccdadl90vs', on_change=refresh_state)
st.video(link)

st.text("The transcription is " + st.session_state['status'])

transcript = ''
if st.button('Transcribe'):
    st.session_state['status'] = 'transcribing'
    transcript = transcribe_from_link(link, False)
    st.session_state['status'] = 'completed'

st.markdown(transcript)
