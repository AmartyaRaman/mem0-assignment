import os
from typing import Optional, List, Dict, Any
from openai import OpenAI
from groq import Groq
from pydantic import BaseModel, Field, ConfigDict
from dotenv import load_dotenv
import json
import tools

load_dotenv()

class IntentClassification(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    intent: str = Field(..., description="The classified intent: 'create_file', 'write_code', 'summarize', or 'chat'")
    
    # Explicit arguments instead of a generic dict to satisfy OpenAI Strict Mode
    filename: Optional[str] = Field(None, description="The name of the file to create or write code to")
    content: Optional[str] = Field(None, description="The content of the file or the code to be written")
    text_to_summarize: Optional[str] = Field(None, description="The text that needs to be summarized")
    query: Optional[str] = Field(None, description="The chat query or general question")
    
    thought: str = Field(..., description="The reasoning behind this classification")

class VoiceAgent:
    def __init__(self, provider: str = "OpenAI", api_key: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key
        
        if provider == "OpenAI":
            self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
            self.model = "gpt-4o-mini"
        elif provider == "Groq":
            self.client = Groq(api_key=api_key or os.getenv("GROQ_API_KEY"))
            self.model = "llama-3.1-8b-instant"

    def transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribes audio file to text."""
        try:
            with open(audio_file_path, "rb") as audio_file:
                if self.provider == "OpenAI":
                    transcript = self.client.audio.transcriptions.create(
                        model="whisper-1", 
                        file=audio_file
                    )
                else: # Groq
                    transcript = self.client.audio.transcriptions.create(
                        model="whisper-large-v3", 
                        file=audio_file
                    )
            return transcript.text
        except Exception as e:
            return f"Error during transcription ({self.provider}): {str(e)}"

    def classify_intent(self, text: str) -> IntentClassification:
        """Uses LLM to classify intent and extract arguments from text."""
        system_prompt = """
        You are an AI intent classifier for a local file-system agent.
        Classify the user's intent and extract necessary arguments.
        
        Valid Intents:
        1. create_file: User wants to create a new file. Use fields 'filename' and 'content'.
        2. write_code: User wants to write code to a file. Use fields 'filename' and 'content' (for the code).
        3. summarize: User wants to summarize some text. Use field 'text_to_summarize'.
        4. chat: User is just talking or asking a question. Use field 'query'.
        
        Always return a structured response in valid JSON format.
        """
        
        try:
            if self.provider == "OpenAI":
                response = self.client.beta.chat.completions.parse(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text}
                    ],
                    response_format=IntentClassification
                )
                return response.choices[0].message.parsed
            else: # Groq
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt + "\nResponse must be a SINGLE JSON object."},
                        {"role": "user", "content": text}
                    ],
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
                return IntentClassification.model_validate_json(content)
                
        except Exception as e:
            return IntentClassification(
                intent="chat",
                query=text,
                thought=f"Error in classification ({self.provider}): {str(e)}"
            )

    def execute_intent(self, classification: IntentClassification) -> str:
        """Executes the tool corresponding to the classified intent."""
        intent = classification.intent
        
        if intent == "create_file":
            return tools.create_file(classification.filename or "new_file.txt", classification.content or "")
        elif intent == "write_code":
            return tools.write_code(classification.filename or "script.py", classification.content or "")
        elif intent == "summarize":
            text_to_summarize = classification.text_to_summarize
            if not text_to_summarize:
                return "No text provided for summarization."
            
            summary_resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Summarize the following text concisely."},
                    {"role": "user", "content": text_to_summarize}
                ]
            )
            summary = summary_resp.choices[0].message.content
            return tools.summarize_text(summary)
            
        elif intent == "chat":
            query = classification.query or ""
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": query}]
            )
            return resp.choices[0].message.content
        
        return "Unknown intent."
