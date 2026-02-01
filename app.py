import streamlit as st
import os
from groq import Groq
import streamlit.components.v1 as components

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

# ---------------- VOICE COMPONENT ----------------
voice_html = """
<script>
const streamlitDoc = window.parent;

function sendTextToStreamlit(text){
    streamlitDoc.postMessage({
        type: "streamlit:setComponentValue",
        value: text
    }, "*");
}

function startDictation(){
    if (!('webkitSpeechRecognition' in window)){
        alert("Use Chrome or Edge");
        return;
    }
    const rec = new webkitSpeechRecognition();
    rec.lang = "en-US";
    rec.start();

    rec.onresult = function(e){
        const text = e.results[0][0].transcript;
        sendTextToStreamlit(text);
    };
}
</script>

<button onclick="startDictation()"
style="padding:10px 16px;border-radius:8px;background:#FF6B35;color:white;border:none;cursor:pointer;">
🎤 Speak
</button>
"""

voice_result = components.html(voice_html, height=70)

# If voice returned text, store it
if voice_result:
    st.session_state.voice_text = voice_result

# ---------------- INPUT ----------------
user_question = st.text_input(
    "Your question:",
    value=st.session_state.voice_text,
    placeholder="Type or click 🎤",
)

if st.button("Send"):
    if user_question.strip():
        st.session_state.voice_text = ""  # reset
        st.session_state.conversation_history.append({"role":"user","content":user_question})

        with st.spinner("Thinking..."):
            reply = get_bot_response(st.session_state.conversation_history)

        st.session_state.conversation_history.append({"role":"assistant","content":reply})
        st.rerun()

# ---------------- FOOTER ----------------
st.markdown("<p style='text-align:center;color:gray;'>Voice Enabled</p>", unsafe_allow_html=True)
