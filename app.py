import streamlit as st
import os
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
from pydub import AudioSegment
import io
import tempfile

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Agent Voice Bot", page_icon="🤖", layout="centered")

# ---------------- CSS ----------------
st.markdown("""
<style>
.chat-container {display:flex;flex-direction:column;gap:12px;}
.user-bubble {background:#007AFF;color:white;padding:12px 16px;border-radius:16px 16px 4px 16px;align-self:flex-end;max-width:75%;}
.bot-bubble {background:#F1F3F6;color:#222;padding:12px 16px;border-radius:16px 16px 16px 4px;align-self:flex-start;max-width:75%;}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

# ---------------- API ----------------
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("Set GROQ_API_KEY")
    st.stop()

client = Groq(api_key=api_key)

SYSTEM_PROMPT = "You are a confident AI developer being interviewed."

def get_bot_response(messages):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"system","content":SYSTEM_PROMPT}, *messages],
        max_tokens=300
    )
    return response.choices[0].message.content

# ---------------- SPEECH TO TEXT ----------------
def speech_to_text(audio_bytes):
    r = sr.Recognizer()

    # Convert WebM/OGG → WAV in memory
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
    wav_io = io.BytesIO()
    audio.export(wav_io, format="wav")
    wav_io.seek(0)

    # SpeechRecognition reads WAV
    with sr.AudioFile(wav_io) as source:
        audio_data = r.record(source)

    try:
        return r.recognize_google(audio_data)
    except Exception:
        return ""


# ---------------- HEADER ----------------
st.title("🤖 AI Agent Voice Bot")

# ---------------- CHAT ----------------
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
for m in st.session_state.conversation_history:
    if m["role"] == "user":
        st.markdown(f"<div class='user-bubble'>{m['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-bubble'>{m['content']}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ---------------- MIC RECORDER ----------------
audio = mic_recorder(start_prompt="🎤 Speak", stop_prompt="⏹ Stop")

if audio:
    text = speech_to_text(audio["bytes"])
    if text:
        st.session_state.voice_text = text
        st.success(f"Recognized: {text}")

# ---------------- INPUT ----------------
user_question = st.text_input(
    "Your question:",
    value=st.session_state.voice_text,
    placeholder="Type or use mic..."
)

if st.button("Send"):
    if user_question.strip():
        st.session_state.voice_text = ""
        st.session_state.conversation_history.append({"role":"user","content":user_question})

        with st.spinner("Thinking..."):
            reply = get_bot_response(st.session_state.conversation_history)

        st.session_state.conversation_history.append({"role":"assistant","content":reply})
        st.rerun()

# ---------------- FOOTER ----------------
st.markdown("<p style='text-align:center;color:gray;'>Voice Enabled via streamlit_mic_recorder</p>", unsafe_allow_html=True)
