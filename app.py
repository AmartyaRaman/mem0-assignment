import streamlit as st
import os
from agent import VoiceAgent
import tempfile
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Voice AI Agent",
    page_icon="🎙️",
    layout="wide"
)

st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #161b22 100%);
    }
    .status-card {
        padding: 1.5rem;
        border-radius: 12px;
        background-color: #1a1f26;
        border: 1px solid #30363d;
        margin-bottom: 1rem;
    }
    .step-header {
        color: #58a6ff;
        font-weight: 600;
        font-size: 0.9rem;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .content-text {
        color: #c9d1d9;
        font-size: 1.1rem;
    }
    /* Hide the password visibility toggle (eye icon) */
    [title="Show password text"], [title="Hide password text"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# Session state
if 'confirmed_api_key' not in st.session_state:
    st.session_state['confirmed_api_key'] = os.getenv("OPENAI_API_KEY") if os.getenv("OPENAI_API_KEY") else ""
if 'current_provider' not in st.session_state:
    st.session_state['current_provider'] = "OpenAI"

# Sidebar
with st.sidebar:
    st.title("Configuration")
    
    # Provider Selection
    provider = st.radio("AI Provider", ["OpenAI", "Groq"], index=0 if st.session_state['current_provider'] == "OpenAI" else 1)
    if provider != st.session_state['current_provider']:
        st.session_state['current_provider'] = provider
        st.session_state['confirmed_api_key'] = os.getenv(f"{provider.upper()}_API_KEY", "")
        st.rerun()

    # Dynamic API Key Input
    st.markdown(f"**{provider} API Key**")
    col1, col2 = st.columns([4, 1])
    
    
    # Change to password type to hide the API key
    temp_key = st.text_input(
        "Enter Key", 
        value=st.session_state['confirmed_api_key'], 
        type="password", 
        label_visibility="collapsed"
    )
    
    if not st.session_state['confirmed_api_key']:
        st.warning("Press the enter key after filling the API key.")
    
    st.divider()
    st.markdown("### System Info")
    st.info(f"Active Provider: **{provider}**")
    st.info("Files will be saved in the `output/` directory.")
    
    if st.button("Clear Cache"):
        st.cache_data.clear()
        st.success("Cache cleared!")

st.title("Voice-Controlled Local AI Agent")
st.markdown("Control your local filesystem using your voice or audio files.")

# Agent Initialize
agent = None
if st.session_state['confirmed_api_key']:
    agent = VoiceAgent(provider=provider, api_key=st.session_state['confirmed_api_key'])

tab1, tab2 = st.tabs(["Direct Input", "File Upload"])

audio_to_process = None

with tab1:
    st.write("Click below to record your voice.")
    audio_value = st.audio_input("Record a message")
    if audio_value:
        audio_to_process = audio_value

with tab2:
    st.write("Upload an audio file (.wav, .mp3, .m4a)")
    uploaded_file = st.file_uploader("Choose a file", type=["wav", "mp3", "m4a"])
    if uploaded_file:
        audio_to_process = uploaded_file

# Disabled unless key is confirmed AND audio is present
can_process = agent is not None and audio_to_process is not None

if st.button("Process Voice Command", type="primary", disabled=not can_process):
    with st.status("Processing Pipeline...", expanded=True) as status:
        # 1. Save temporary audio file
        st.write("Saving temporary audio...")
        suffix = Path(audio_to_process.name).suffix if hasattr(audio_to_process, 'name') else ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(audio_to_process.getvalue())
            tmp_path = tmp_file.name

        # 2. Transcription
        status.update(label=f"Transcribing audio ({provider})...", state="running")
        transcript = agent.transcribe_audio(tmp_path)
        
        st.markdown(f'<div class="status-card"><div class="step-header">Transcription</div><div class="content-text">{transcript}</div></div>', unsafe_allow_html=True)

        # 3. Intent Classification
        status.update(label=f"Analyzing intent ({provider})...", state="running")
        classification = agent.classify_intent(transcript)
        
        st.markdown(f'''
            <div class="status-card">
                <div class="step-header">Intent Detected</div>
                <div class="content-text">
                    <b>Type:</b> {classification.intent.replace("_", " ").title()}<br>
                    <b>Thought:</b> {classification.thought}
                </div>
            </div>
        ''', unsafe_allow_html=True)

        # 4. Tool Execution
        status.update(label="Executing action...", state="running")
        result = agent.execute_intent(classification)
        
        st.markdown(f'<div class="status-card"><div class="step-header">Action Result</div><div class="content-text">{result}</div></div>', unsafe_allow_html=True)
        
        # Clean up
        os.unlink(tmp_path)
        status.update(label="Pipeline Complete!", state="complete", expanded=False)

st.divider()

st.subheader("Output Folder Explorer")
output_files = list(Path("output").glob("*"))
if output_files:
    cols = st.columns(3)
    for i, file_path in enumerate(output_files):
        with cols[i % 3]:
            with st.expander(f"📄 {file_path.name}"):
                try:
                    content = file_path.read_text(encoding="utf-8")
                    st.code(content, language="python" if file_path.suffix == ".py" else None)
                except:
                    st.write("Cannot preview binary/large file.")
else:
    st.info("No files found in output directory yet.")
