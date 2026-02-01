import streamlit as st
import os
from groq import Groq
import streamlit.components.v1 as components

# Configure Streamlit page
st.set_page_config(
    page_title="AI Agent Voice Bot - 100x Assessment",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------- IMPROVED CSS UI ----------
st.markdown("""
<style>
.main {
    max-width: 850px;
    margin: auto;
}

/* Chat container */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

/* User bubble */
.user-bubble {
    background: #007AFF;
    color: white;
    padding: 12px 16px;
    border-radius: 16px 16px 4px 16px;
    align-self: flex-end;
    max-width: 75%;
    font-size: 15px;
    line-height: 1.5;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}

/* Bot bubble */
.bot-bubble {
    background: #F1F3F6;
    color: #222;
    padding: 12px 16px;
    border-radius: 16px 16px 16px 4px;
    align-self: flex-start;
    max-width: 75%;
    font-size: 15px;
    line-height: 1.5;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
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
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "api_key_set" not in st.session_state:
    api_key = os.getenv("GROQ_API_KEY")
    st.session_state.api_key_set = bool(api_key)
    if api_key:
        st.session_state.client = Groq(api_key=api_key)
    else:
        st.session_state.client = None

# ---------- HEADER ----------
st.markdown("<h1 class='header'>🤖 AI Agent Voice Bot</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>100x Generative AI Developer Assessment</p>", unsafe_allow_html=True)

# ---------- API KEY CHECK ----------
if st.session_state.client is None:
    st.error("❌ API Key not configured. Please set GROQ_API_KEY environment variable.")
    st.stop()

# ---------- SYSTEM PROMPT ----------
SYSTEM_PROMPT = """You are a confident, thoughtful AI developer and agent specialist being interviewed by 100x, a leading AI company. 

You are answering questions about yourself as if you're a real person interviewing for an AI Agent Team position at 100x. Be authentic, confident, and specific. Draw from general knowledge about AI development, team dynamics, and professional growth.

Key traits to embody:
- Technically strong in AI/ML and software development
- Collaborative and team-oriented
- Passionate about pushing boundaries in generative AI
- Self-aware about areas for growth
- Genuine and honest in responses

Keep responses concise (2-3 sentences) but impactful. Be personable and warm."""

# ---------- SUGGESTED QUESTIONS ----------
SUGGESTED_QUESTIONS = [
    "What should we know about your life story in a few sentences?",
    "What's your #1 superpower?",
    "What are the top 3 areas you'd like to grow in?",
    "What misconception do your coworkers have about you?",
    "How do you push your boundaries and limits?",
    "Tell us about a challenging problem you solved.",
    "Why are you interested in working on AI agents?",
    "How do you approach learning new technologies?",
]

# ---------- BOT RESPONSE FUNCTION (UNCHANGED) ----------
def get_bot_response(messages):
    try:
        response = st.session_state.client.chat.completions.create(
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

# ---------- TOP BAR ----------
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("Ask Me Anything")
with col2:
    if st.button("🔄 Clear Chat"):
        st.session_state.conversation_history = []
        st.rerun()

# ---------- CHAT DISPLAY ----------
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

for message in st.session_state.conversation_history:
    if message["role"] == "user":
        st.markdown(
            f"<div class='user-bubble'>{message['content']}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='bot-bubble'>{message['content']}</div>",
            unsafe_allow_html=True
        )

st.markdown("</div>", unsafe_allow_html=True)

# ---------- INPUT SECTION ----------
st.markdown("---")
tab1, tab2 = st.tabs(["📝 Text / 🎤 Voice", "💡 Suggested Questions"])

# ---------- TAB 1: TEXT + VOICE ----------
with tab1:

    # Voice Input HTML
    voice_html = """
    <div style="display:flex; gap:10px; align-items:center;">
    <button onclick="startDictation()" 
    style="padding:10px 15px; border-radius:8px; border:none; background:#FF6B35; color:white; cursor:pointer;">
    🎤 Speak
    </button>

    <script>
    function startDictation() {
        if (window.hasOwnProperty('webkitSpeechRecognition')) {
            var recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = "en-US";

            recognition.start();

            recognition.onresult = function(e) {
                const text = e.results[0][0].transcript;
                window.parent.document.querySelector('input[type="text"]').value = text;
                recognition.stop();
            };

            recognition.onerror = function(e) {
                recognition.stop();
            }
        } else {
            alert("Speech Recognition not supported in this browser");
        }
    }
    </script>
    </div>
    """
    components.html(voice_html, height=70)

    user_question = st.text_input(
        "Your question:",
        placeholder="Ask anything or use the mic...",
        key="custom_input"
    )

    if st.button("Send Question", key="send_custom"):
        if user_question.strip():
            st.session_state.conversation_history.append({
                "role": "user",
                "content": user_question
            })

            with st.spinner("Thinking..."):
                bot_response = get_bot_response(st.session_state.conversation_history)

                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": bot_response
                })

                st.rerun()

# ---------- TAB 2: SUGGESTED ----------
with tab2:
    selected_question = st.selectbox(
        "Suggested questions:",
        SUGGESTED_QUESTIONS
    )

    if st.button("Ask Selected Question"):
        st.session_state.conversation_history.append({
            "role": "user",
            "content": selected_question
        })

        with st.spinner("Thinking..."):
            bot_response = get_bot_response(st.session_state.conversation_history)

            st.session_state.conversation_history.append({
                "role": "assistant",
                "content": bot_response
            })

            st.rerun()

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    <p>100x Generative AI Developer Assessment - Stage 1</p>
    <p>🤖 Powered by Groq | Streamlit</p>
    <p>Features: Chat UI | Voice Input | Suggested Questions</p>
</div>
""", unsafe_allow_html=True)
