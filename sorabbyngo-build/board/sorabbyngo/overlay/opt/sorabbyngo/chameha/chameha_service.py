# Chameha Service
# Main FastAPI service — handles voice and chat interfaces
# Connects to Byngox via ACP over NATS

import logging
from fastapi import FastAPI
from personality.tone_engine import ToneEngine
from interfaces.voice_interface import VoiceInterface
from interfaces.chat_interface import ChatInterface

log = logging.getLogger(__name__)
app = FastAPI(title="Chameha", version="0.1.0")

tone = ToneEngine()
voice = VoiceInterface()
chat = ChatInterface()

@app.get("/health")
async def health():
    return {"status": "active", "service": "chameha"}

@app.post("/chat")
async def chat_endpoint(message: str, mode: str = "patient"):
    tone.set_mode(mode)
    response = await chat.handle(message)
    return {"response": response, "tone": mode}

@app.post("/voice")
async def voice_endpoint(audio_path: str):
    text = await voice.transcribe(audio_path)
    response = await chat.handle(text)
    audio_out = await voice.synthesize(response)
    return {"transcript": text, "response": response, "audio": audio_out}
