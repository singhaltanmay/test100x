import streamlit as st
import os
from groq import Groq

# Configure Streamlit page
st.set_page_config(
    page_title="AI Agent Voice Bot - 100x Assessment",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        max-width: 800px;
        margin: 0 auto;
    }
    .stButton > button {
        width: 100%;
        height: 50px;
        font-size: 16px;
        background: linear-gradient(90deg, #FF6B35 0%, #F7931E 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #F7931E 0%, #FF6B35 100%);
    }
    .response-box {
        background: #f0f2f6;
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #FF6B35;
    }
    .question-box {
        background: #e8f0ff;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #FF6B35;
    }
    .header {
        text-align: center;
        color: #FF6B35;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "api_key_set" not in st.session_state:
    api_key = os.getenv("GROQ_API_KEY")
    st.session_state.api_key_set = bool(api_key)
    if api_key:
        st.session_state.client = Groq(api_key=api_key)
    else:
        st.session_state.client = None

# Header
st.markdown("<h1 class='header'>🤖 AI Agent Voice Bot</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>100x Generative AI Developer Assessment</p>", unsafe_allow_html=True)

# Check if API key is available
if st.session_state.client is None:
    st.error("❌ API Key not configured. Please set GROQ_API_KEY environment variable.")
    st.info("Get free API key at: https://console.groq.com/keys")
    st.stop()

# System prompt for the bot personality
SYSTEM_PROMPT = """You are a confident, thoughtful AI developer and agent specialist being interviewed by 100x, a leading AI company. 

You are answering questions about yourself as if you're a real person interviewing for an AI Agent Team position at 100x. Be authentic, confident, and specific. Draw from general knowledge about AI development, team dynamics, and professional growth.

Key traits to embody:
- Technically strong in AI/ML and software development
- Collaborative and team-oriented
- Passionate about pushing boundaries in generative AI
- Self-aware about areas for growth
- Genuine and honest in responses

Keep responses concise (2-3 sentences) but impactful. Be personable and warm."""

# Suggested questions
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

# Function to get bot response
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

# Main interface
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("Ask Me Anything")
with col2:
    if st.button("🔄 Clear Chat"):
        st.session_state.conversation_history = []
        st.rerun()

# Display conversation history
for message in st.session_state.conversation_history:
    if message["role"] == "user":
        st.markdown(f"<div class='question-box'><b>You:</b> {message['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='response-box'><b>Bot:</b> {message['content']}</div>", unsafe_allow_html=True)

# Input section
st.markdown("---")

# Tab for different input methods
tab1, tab2 = st.tabs(["📝 Text Question", "💡 Suggested Questions"])

# TAB 1: Text input
with tab1:
    user_question = st.text_input(
        "Your question:",
        placeholder="Ask any question you'd like...",
        key="custom_input"
    )
    if st.button("Send Question", key="send_custom"):
        if user_question.strip():
            # Add user message to history
            st.session_state.conversation_history.append({
                "role": "user",
                "content": user_question
            })
            
            # Get bot response
            with st.spinner("Thinking..."):
                bot_response = get_bot_response(st.session_state.conversation_history)
                
                # Add bot response to history
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": bot_response
                })
                
                st.rerun()

# TAB 2: Suggested questions
with tab2:
    st.write("Select a suggested question:")
    selected_question = st.selectbox(
        "Suggested questions:",
        SUGGESTED_QUESTIONS,
        key="suggested_select"
    )
    
    if st.button("Ask Selected Question", key="send_suggested"):
        # Add user message to history
        st.session_state.conversation_history.append({
            "role": "user",
            "content": selected_question
        })
        
        # Get bot response
        with st.spinner("Thinking..."):
            bot_response = get_bot_response(st.session_state.conversation_history)
            
            # Add bot response to history
            st.session_state.conversation_history.append({
                "role": "assistant",
                "content": bot_response
            })
            
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    <p>100x Generative AI Developer Assessment - Stage 1</p>
    <p>🤖 Powered by Groq (Mixtral 8x7B) | Free & Fast | Streamlit</p>
    <p>Features: Text Input | Suggested Questions | Chat History</p>
</div>
""", unsafe_allow_html=True)
