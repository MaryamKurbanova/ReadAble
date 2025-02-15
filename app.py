import streamlit as st
from gtts import gTTS
import os

# Injecting custom fonts (Lexend & OpenDyslexic from Google Fonts)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300&display=swap');
        @font-face {
            font-family: 'OpenDyslexic';
            src: url('https://opendyslexic.org/static/OpenDyslexic-Regular.otf') format('opentype');
        }
        .open-dyslexic { font-family: 'OpenDyslexic', sans-serif; }
        .lexend { font-family: 'Lexend', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# Dyslexia-friendly font options
font_options = {
    "Arial": "Arial, sans-serif",
    "Comic Sans": "Comic Sans MS, cursive",
    "Lexend": "Lexend, sans-serif",
    "OpenDyslexic": "open-dyslexic",
    "Verdana": "Verdana, sans-serif",
    "Serif": "Times New Roman, serif",
    "Monospace": "Courier New, monospace"
}

# Streamlit UI
st.title("Accessible Text-to-Speech & Dyslexia-Friendly Fonts")
st.write("Enter text below, convert it to speech, and customize the font for better readability.")

# User text input
text_input = st.text_area("Enter text here:")

# Font selection
selected_font = st.selectbox("Choose a font for reading:", list(font_options.keys()))

# Display text in selected font
if text_input.strip():
    st.markdown(
        f'<div style="font-family: {font_options[selected_font]}; font-size: 20px; padding: 10px;">{text_input}</div>',
        unsafe_allow_html=True
    )

# Convert text to speech
if st.button("Generate Speech"):
    if text_input.strip():
        tts = gTTS(text=text_input, lang='en')
        audio_file = "output.mp3"
        tts.save(audio_file)

        # Play audio
        st.audio(audio_file, format='audio/mp3')

        # Provide download link
        with open(audio_file, "rb") as file:
            st.download_button("Download Audio", file, file_name="speech.mp3", mime="audio/mp3")
    else:
        st.warning("Please enter some text.")
