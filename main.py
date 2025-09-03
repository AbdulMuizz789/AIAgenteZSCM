# main.py
# To run:
# 1. pip install fastapi uvicorn python-dotenv openai google-generativeai anthropic
# 2. Create a .env file with your API keys:
#    OPENAI_API_KEY="your_openai_key"
#    GEMINI_API_KEY="your_gemini_key"
#    ANTHROPIC_API_KEY="your_anthropic_key"
# 3. Run the server: uvicorn main:app --reload

import os
import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

# --- Load API Keys ---
load_dotenv()
# Make sure to have these in your .env file
# OPENAI_API_KEY=...
# GEMINI_API_KEY=...
# ANTHROPIC_API_KEY=...

# --- AI Provider Abstraction ---

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
    async def stream_chat(self, prompt: str, model: str):
        raise NotImplementedError

class OpenAIProvider(BaseProvider):
    def __init__(self):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(base_url='https://api.zukijourney.com/v1',api_key=os.getenv("API_KEY"))

    async def stream_chat(self, prompt: str, model: str):
        stream = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices:
                content = chunk.choices[0].delta.content
                if content:
                    print(f"OpenAI chunk: {content}")
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
    allow_origins=["*"], # Allow all origins for simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def event_generator(request: Request, prompt: str, provider: str, model: str):
    try:
        ai_provider = AIProviderFactory.get_provider(provider)
        async for token in ai_provider.stream_chat(prompt, model):
            if await request.is_disconnected():
                print("Client disconnected.")
                break
            
            sse_data = {"delta": token}
            yield f"data: {json.dumps(sse_data)}\n\n"
            await asyncio.sleep(0.01) # Prevent overwhelming the client
            
        yield "data: [DONE]\n\n"
    except Exception as e:
        print(f"Error during streaming: {e}")
        import traceback
        traceback.print_exc()
        error_data = {"error": str(e)}
        yield f"data: {json.dumps(error_data)}\n\n"

@app.get("/chat/stream")
async def chat_stream(request: Request, prompt: str, provider: str = "gemini", model: str = "gemini-pro"):
    return StreamingResponse(
        event_generator(request, prompt, provider, model),
        media_type="text/event-stream"
    )

@app.get("/")
def read_root():
    return {"message": "AI Chatbot Backend is running."}

# To run this app:
# 1. Save the code as main.py
# 2. Install dependencies: pip install fastapi "uvicorn[standard]" python-dotenv openai google-generativeai anthropic aiohttp
# 3. Create a .env file in the same directory with your API keys:
#    OPENAI_API_KEY="sk-..."
#    GEMINI_API_KEY="..."
#    ANTHROPIC_API_KEY="..."
# 4. Run the server from your terminal: uvicorn main:app --reload