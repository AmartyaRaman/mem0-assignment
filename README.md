# Voice-Controlled Local AI Agent

A premium Streamlit-based AI agent that control your local filesystem using voice commands.

## Features
- **Real-time Voice Input**: Use the browser's microphone to give commands.
- **Audio File Upload**: Supports `.wav`, `.mp3`, and `.m4a`.
- **Intelligent Pipeline**:
  - **STT**: Whisper (OpenAI) converts audio to text.
  - **Intent Classification**: GPT-4o-mini analyzes the command and extracts parameters.
  - **Tool Execution**: Performs actions (File creation, Code writing, Summarization) locally.
- **Security**: All file operations are isolated to the `output/` folder.

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **API Key Configuration**:
   - Create a `.env` file from the `.env.example`.
   - Add your `OPENAI_API_KEY`.
   - Alternatively, you can enter the key directly in the application sidebar.

3. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

## Example Commands
- "Create a text file called reminder.txt with the content 'Buy milk tonight'."
- "Write a python script called fib.py that calculates the fibonacci sequence."
- "Summarize the following text: [Your Text Here]"

## Project Structure
- `app.py`: Streamlit frontend and UI layout.
- `agent.py`: Orchestration of STT, Intent Classification, and Tool Routing.
- `tools.py`: Local filesystem operation handlers.
- `output/`: Secure directory for all generated files.
