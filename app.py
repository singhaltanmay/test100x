import streamlit as st
import openai
import os
from streamlit_mic_recorder import mic_recorder

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
    .voice-box {
        background: #f0f0f0;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #10a37f;
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

# Function to get bot response
def get_bot_response(messages):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
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
tab1, tab2, tab3 = st.tabs(["📝 Text Question", "🎤 Voice Input", "💡 Suggested Questions"])

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

# TAB 2: Voice input
with tab2:
    st.info("🎤 Click the microphone to record your question")
    
    # Mic recorder component
    audio = mic_recorder(
        start_prompt="🎤 Start Recording",
        stop_prompt="⏹️ Stop Recording",
        key="recorder"
    )
    
    if audio:
        # Save audio temporarily and transcribe
        with st.spinner("Transcribing your voice..."):
            try:
                # Save the audio file
                audio_bytes = audio['bytes']
                with open("temp_audio.wav", "wb") as f:
                    f.write(audio_bytes)
                
                # Transcribe using OpenAI Whisper API
                with open("temp_audio.wav", "rb") as audio_file:
                    transcript = openai.Audio.transcribe("whisper-1", audio_file)
                
                user_question = transcript["text"]
                st.success(f"✅ Transcribed: '{user_question}'")
                
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
                
                # Clean up temp file
                if os.path.exists("temp_audio.wav"):
                    os.remove("temp_audio.wav")
                
            except Exception as e:
                st.error(f"Error processing voice: {str(e)}")

# TAB 3: Suggested questions
with tab3:
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
    <p>🤖 Powered by OpenAI GPT-3.5 + Whisper | Streamlit</p>
    <p>Features: Text Input | Voice Input | Suggested Questions</p>
</div>
""", unsafe_allow_html=True)
