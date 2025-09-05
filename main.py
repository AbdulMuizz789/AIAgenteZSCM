# -------------------------------------------------------------------------
# main.py - Main FastAPI application
# -------------------------------------------------------------------------
import os
import asyncio
import json
import uuid
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from dotenv import load_dotenv
from datetime import timedelta

from sqlalchemy.orm import Session
import models, schemas, crud, security
from database import engine, get_db

# Create database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

load_dotenv()

# --- AI Provider Abstraction (Dummy for Demonstration) ---
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
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
        self.client = AsyncOpenAI(base_url="https://api.anthropic.com/v1/", api_key=os.getenv("ANTHROPIC_API_KEY"))

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Authentication Endpoints ---
@app.post("/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = crud.authenticate_user(db, email=form_data.username, password=form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
    except Exception as e:
        print(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(security.get_current_user)) -> schemas.User:
    return current_user

# --- Session Endpoints ---
@app.get("/sessions", response_model=list[schemas.Session])
def get_sessions(db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    return crud.get_sessions(db=db, user_id=current_user.id)

@app.post("/sessions", response_model=schemas.Session)
def create_session(session_create: schemas.SessionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    return crud.create_session(db=db, session=session_create, user_id=current_user.id)

@app.get("/sessions/{session_id}", response_model=schemas.Session)
def get_session_details(session_id: uuid.UUID, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    session = crud.get_session(db=db, session_id=session_id, user_id=current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.put("/sessions/{session_id}", response_model=schemas.Session)
def update_session_title(session_id: uuid.UUID, session_update: schemas.SessionUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    return crud.update_session_title(db=db, session_id=session_id, user_id=current_user.id, title=session_update.title)

@app.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: uuid.UUID, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    success = crud.delete_session(db=db, session_id=session_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return None

# --- Chat Streaming Endpoint ---
async def stream_and_save(request: Request, payload: schemas.ChatRequest, db: Session, user_id: uuid.UUID):
    # ... (Logic from previous version, adapted to use crud functions)
    # 1. Save User Message
    crud.create_message(db, session_id=payload.session_id, role="user", content=payload.prompt, user_id=user_id)
    
    # 2. Stream AI Response
    full_response = ""
    try:
        history_db = crud.get_messages(db, session_id=payload.session_id, user_id=user_id)
        history = [{"role": m.role, "content": m.content} for m in history_db]

        ai_provider = AIProviderFactory.get_provider(payload.provider)
        async for token in ai_provider.stream_chat(payload.prompt, payload.model, history):
            if await request.is_disconnected(): break
            yield f"data: {json.dumps({'delta': token})}\n\n"
            full_response += token
            await asyncio.sleep(0.01)

        if full_response:
             crud.create_message(db, session_id=payload.session_id, role="assistant", content=full_response, user_id=user_id)
        
        yield "data: [DONE]\n\n"
    except Exception as e:
        print(f"Error during streaming: {e}")
        import traceback
        traceback.print_exc()
        error_data = {"error": str(e)}
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

@app.post("/chat/stream")
async def chat_stream(request: Request, payload: schemas.ChatRequest, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    session = crud.get_session(db=db, session_id=payload.session_id, user_id=current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return StreamingResponse(
        stream_and_save(request, payload, db, current_user.id),
        media_type="text/event-stream"
    )
