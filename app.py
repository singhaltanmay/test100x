import streamlit as st
import os
from groq import Groq
import streamlit.components.v1 as components

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Agent Voice Bot - 100x Assessment",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------- UI CSS ----------------
st.markdown("""
<style>
.main {
    max-width: 850px;
    margin: auto;
}
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 12px;
}
.user-bubble {
    background: #007AFF;
    color: white;
    padding: 12px 16px;
    border-radius: 16px 16px 4px 16px;
    align-self: flex-end;
    max-width: 75%;
    font-size: 15px;
    line-height: 1.5;
}
.bot-bubble {
    background: #F1F3F6;
    color: #222;
    padding: 12px 16px;
    border-radius: 16px 16px 16px 4px;
    align-self: flex-start;
    max-width: 75%;
    font-size: 15px;
    line-height: 1.5;
}
.stButton > button {
    width: 100%;
    height: 45px;
    font-size: 15px;
    border-radius: 10px;
    font-weight: bold;
}
.header {
    text-align: center;
    color: #FF6B35;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

api_key = os.getenv("GROQ_API_KEY")
if api_key:
    client = Groq(api_key=api_key)
else:
    client = None

# ---------------- HEADER ----------------
st.markdown("<h1 class='header'>🤖 AI Agent Voice Bot</h1>", unsafe_allow_html=True)

if client is None:
    st.error("❌ Set GROQ_API_KEY environment variable")
    st.stop()

# ---------------- SYSTEM PROMPT ----------------
SYSTEM_PROMPT = """You are a confident, thoughtful AI developer being interviewed by 100x.
Be concise, warm, and impactful in 2–3 sentences."""

# ---------------- BOT FUNCTION (UNCHANGED) ----------------
def get_bot_response(messages):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *messages
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# ---------------- TOP BAR ----------------
col1, col2 = st.columns([3,1])
with col1:
    st.subheader("Ask Me Anything")
with col2:
    if st.button("🔄 Clear"):
        st.session_state.conversation_history = []
        st.rerun()

# ---------------- CHAT DISPLAY ----------------
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
for msg in st.session_state.conversation_history:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ---------------- VOICE BUTTON COMPONENT ----------------
components.html("""
<script>
function startDictation() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("Use Chrome or Edge");
        return;
    }
    const recognition = new webkitSpeechRecognition();
    recognition.lang = "en-US";
    recognition.start();
    recognition.onresult = function(e) {
        const text = e.results[0][0].transcript;
        const input = window.parent.document.querySelector('input[type="text"]');
        if (input) {
            input.value = text;
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }
    };
}
</script>

<button onclick="startDictation()"
style="padding:10px 15px;border-radius:8px;border:none;background:#FF6B35;color:white;cursor:pointer;">
🎤 Speak
</button>
""", height=60)

# ---------------- INPUT ----------------
user_question = st.text_input(
    "Your question:",
    placeholder="Type or use 🎤...",
)

if st.button("Send"):
    if user_question.strip():
        st.session_state.conversation_history.append({
            "role": "user",
            "content": user_question
        })

        with st.spinner("Thinking..."):
            reply = get_bot_response(st.session_state.conversation_history)

        st.session_state.conversation_history.append({
            "role": "assistant",
            "content": reply
        })
        st.rerun()

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:gray;font-size:12px;'>Voice + Chat UI Enabled</p>",
    unsafe_allow_html=True
)
