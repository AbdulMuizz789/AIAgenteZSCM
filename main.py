# -------------------------------------------------------------------------
# main.py - Main FastAPI application
# -------------------------------------------------------------------------
import os
import asyncio
import json
import uuid
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

# --- Database Imports ---
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models
import schemas

# Create database tables
Base.metadata.create_all(bind=engine)

# --- Load API Keys ---
load_dotenv()

# --- AI Provider Abstraction (from previous version, unchanged) ---
# [NOTE: The AIProviderFactory and individual provider classes remain the same]
class AIProviderFactory:
    @staticmethod
    def get_provider(provider_name):
        if provider_name == "openai":
            return OpenAIProvider()
        if provider_name == "gemini":
            return GeminiProvider()
        if provider_name == "anthropic":
            return AnthropicProvider()
        # Bonus: Ollama integration
        if provider_name == "ollama":
            return OllamaProvider()
        raise ValueError(f"Unsupported provider: {provider_name}")

class BaseProvider:
    async def stream_chat(self, prompt: str, model: str, history: list = []):
        raise NotImplementedError

class OpenAIProvider(BaseProvider):
    def __init__(self):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(base_url='https://api.zukijourney.com/v1',api_key=os.getenv("API_KEY"))

    async def stream_chat(self, prompt: str, model: str, history: list = []):
        stream = await self.client.chat.completions.create(
            model=model,
            messages=history + [{"role": "user", "content": prompt}],
            stream=True
        )
        async for chunk in stream:
            if chunk.choices:
                content = chunk.choices[0].delta.content
                if content:
                    yield content

class GeminiProvider(BaseProvider):
    def __init__(self):
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.genai = genai

    async def stream_chat(self, prompt: str, model: str):
        model_instance = self.genai.GenerativeModel(model)
        response_stream = await model_instance.generate_content_async(prompt, stream=True)
        async for chunk in response_stream:
            if chunk.text:
                yield chunk.text

class AnthropicProvider(BaseProvider):
    def __init__(self):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(base_url='https://api.zukijourney.com/v1', api_key=os.getenv("ANTHROPIC_API_KEY"))

    async def stream_chat(self, prompt: str, model: str):
        async with self.client.messages.stream(
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
            model=model,
        ) as stream:
            async for text in stream.text_stream:
                yield text

class OllamaProvider(BaseProvider):
    def __init__(self):
        import aiohttp
        self.session = aiohttp.ClientSession()
        self.ollama_api_url = "http://localhost:11434/api/generate"

    async def stream_chat(self, prompt: str, model: str):
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True
        }
        async with self.session.post(self.ollama_api_url, json=payload) as response:
            async for line in response.content:
                if line:
                    try:
                        json_line = json.loads(line.decode('utf-8'))
                        if 'response' in json_line and not json_line.get('done'):
                            yield json_line['response']
                    except json.JSONDecodeError:
                        print(f"Could not decode line: {line}")

# --- FastAPI Application ---
app = FastAPI()

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---

# A mock user for demonstration purposes. In a real app, this would come from a JWT token.
MOCK_USER_ID = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")

@app.get("/sessions", response_model=list[schemas.Session])
def get_sessions(db: Session = Depends(get_db)):
    """Get all sessions for the mock user."""
    return db.query(models.Session).filter(models.Session.user_id == MOCK_USER_ID).all()

@app.post("/sessions", response_model=schemas.Session)
def create_session(session_create: schemas.SessionCreate, db: Session = Depends(get_db)):
    """Create a new session."""
    new_session = models.Session(
        user_id=MOCK_USER_ID,
        title=session_create.title or "New Chat"
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@app.get("/sessions/{session_id}", response_model=schemas.Session)
def get_session_details(session_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get details and messages for a specific session."""
    session = db.query(models.Session).filter(models.Session.id == session_id, models.Session.user_id == MOCK_USER_ID).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


async def stream_and_save(request: Request, payload: schemas.ChatRequest, db: Session):
    """Handles the streaming logic and saves the conversation to the DB."""
    # 1. Save User Message
    user_message_db = models.Message(
        session_id=payload.session_id,
        role="user",
        content=payload.prompt
    )
    db.add(user_message_db)
    db.commit()

    # 2. Stream AI Response
    full_response = ""
    try:
        # Fetch message history for context
        history_db = db.query(models.Message).filter(models.Message.session_id == payload.session_id).order_by(models.Message.created_at).all()
        history = [{"role": m.role, "content": m.content} for m in history_db]

        ai_provider = AIProviderFactory.get_provider(payload.provider)
        async for token in ai_provider.stream_chat(payload.prompt, payload.model, history):
            if await request.is_disconnected():
                print("Client disconnected.")
                break
            
            sse_data = {"delta": token}
            yield f"data: {json.dumps(sse_data)}\n\n"
            full_response += token
            await asyncio.sleep(0.01)

        # 3. Save AI Message
        if full_response:
            ai_message_db = models.Message(
                session_id=payload.session_id,
                role="assistant",
                content=full_response
            )
            db.add(ai_message_db)
            db.commit()
            
        yield "data: [DONE]\n\n"
    except Exception as e:
        print(f"Error during streaming: {e}")
        import traceback
        traceback.print_exc()
        error_data = {"error": str(e)}
        yield f"data: {json.dumps(error_data)}\n\n"


@app.post("/chat/stream")
async def chat_stream(request: Request, payload: schemas.ChatRequest, db: Session = Depends(get_db)):
    """Main endpoint for streaming chat responses."""
    session = db.query(models.Session).filter(models.Session.id == payload.session_id).first()
    if not session or session.user_id != MOCK_USER_ID:
        raise HTTPException(status_code=404, detail="Session not found")
        
    return StreamingResponse(
        stream_and_save(request, payload, db),
        media_type="text/event-stream"
    )
