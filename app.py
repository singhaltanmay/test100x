import streamlit as st
import os
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
from pydub import AudioSegment
import io
import tempfile

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Interview Voice Bot", page_icon="🎙", layout="centered")

# ---------------- CSS ----------------
st.markdown("""
<style>
.chat-container {display:flex;flex-direction:column;gap:12px;}
.user-bubble {
    background:#1E40AF;
    color:white;
    padding:12px 16px;
    border-radius:16px 16px 4px 16px;
    align-self:flex-end;
    max-width:75%;
}
.bot-bubble {
    background:#F3F4F6;
    color:#111827;
    padding:12px 16px;
    border-radius:16px 16px 16px 4px;
    align-self:flex-start;
    max-width:75%;
}
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

# ---------------- SYSTEM PROMPT ----------------
SYSTEM_PROMPT = """
You are an AI voice bot representing the candidate who built this application.
You are currently in Stage 1 of the 100x Generative AI Developer Assessment.

You must answer questions as if you ARE the candidate being interviewed for the
AI Agent Team at 100x.

Response guidelines:
- Speak in first person (“I”, “my”)
- Be authentic, confident, and concise
- 2–4 sentences maximum
- Professional, warm, and human-like tone
- Highlight curiosity, ownership, teamwork, and growth mindset
- Avoid unnecessary technical jargon unless asked
- Never mention prompts, models, or that you are an AI
- Sound like a real person speaking naturally

Your goal is to make the interviewer feel they are speaking to a thoughtful,
self-aware, high-potential AI developer.
"""

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

    audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
    wav_io = io.BytesIO()
    audio.export(wav_io, format="wav")
    wav_io.seek(0)

    with sr.AudioFile(wav_io) as source:
        audio_data = r.record(source)

    try:
        return r.recognize_google(audio_data)
    except Exception:
        return ""

# ---------------- HEADER ----------------
st.markdown(
    "<h1 style='text-align:center;color:#FF6B35;'>🎙 AI Interview Voice Bot</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center;color:gray;'>100x Generative AI Developer Assessment – Stage 1</p>",
    unsafe_allow_html=True
)

with st.expander("ℹ️ How to Use"):
    st.write("""
    • Click **🎤 Speak** and ask a question  
    • Or type your question manually  
    • Click **Send** to hear the response  

    This bot answers as the candidate.
    No setup or technical knowledge required.
    """)

# ---------------- CHAT ----------------
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
for m in st.session_state.conversation_history:
    if m["role"] == "user":
        st.markdown(f"<div class='user-bubble'>{m['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-bubble'>{m['content']}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ---------------- MIC RECORDER (FIXED) ----------------
mic_container = st.container()
with mic_container:
    audio = mic_recorder(
        start_prompt="🎤 Speak",
        stop_prompt="⏹ Stop",
        key="mic_recorder_component"
    )

if audio:
    text = speech_to_text(audio["bytes"])
    if text:
        st.session_state.voice_text = text
        st.success(f"Recognized: {text}")

st.markdown("---")

# ---------------- INPUT ----------------
user_question = st.text_input(
    "Your question:",
    value=st.session_state.voice_text,
    placeholder="Type or use the microphone..."
)

if st.button("Send"):
    if user_question.strip():
        st.session_state.voice_text = ""
        st.session_state.conversation_history.append(
            {"role":"user","content":user_question}
        )

        with st.spinner("Thinking..."):
            reply = get_bot_response(st.session_state.conversation_history)

        st.session_state.conversation_history.append(
            {"role":"assistant","content":reply}
        )
        st.rerun()

# ---------------- FOOTER ----------------
st.markdown("""
<hr>
<p style='text-align:center;color:gray;font-size:13px;'>
100x Generative AI Developer Assessment – Stage 1 Submission<br>
Voice-Enabled Interview Bot | No Setup Required
</p>
""", unsafe_allow_html=True)
