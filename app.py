import streamlit as st
import openai
import os

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
        background: linear-gradient(90deg, #10a37f 0%, #0a7d62 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #0a7d62 0%, #10a37f 100%);
    }
    .response-box {
        background: #f0f2f6;
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #10a37f;
    }
    .question-box {
        background: #e8f0ff;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #10a37f;
    }
    .header {
        text-align: center;
        color: #10a37f;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "api_key_set" not in st.session_state:
    api_key = os.getenv("OPENAI_API_KEY")
    st.session_state.api_key_set = bool(api_key)
    if api_key:
        openai.api_key = api_key

# Header
st.markdown("<h1 class='header'>🤖 AI Agent Voice Bot</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>100x Generative AI Developer Assessment</p>", unsafe_allow_html=True)

# Check if API key is available
if not st.session_state.api_key_set:
    st.error("❌ API Key not configured. Please set OPENAI_API_KEY environment variable.")
    st.info("For deployment, this is automatically configured. For local testing, set your API key.")
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

# Tab for custom question or suggested questions
tab1, tab2 = st.tabs(["📝 Ask Custom Question", "💡 Suggested Questions"])

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
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            *st.session_state.conversation_history
                        ],
                        max_tokens=500,
                        temperature=0.7
                    )
                    
                    bot_response = response.choices[0].message.content
                    
                    # Add bot response to history
                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": bot_response
                    })
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"Error getting response: {str(e)}")

with tab2:
    st.write("Select a suggested question or ask your own:")
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
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        *st.session_state.conversation_history
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                
                bot_response = response.choices[0].message.content
                
                # Add bot response to history
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": bot_response
                })
                
                st.rerun()
            except Exception as e:
                st.error(f"Error getting response: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    <p>100x Generative AI Developer Assessment - Stage 1</p>
    <p>Powered by OpenAI GPT-3.5 | Streamlit</p>
</div>
""", unsafe_allow_html=True)
