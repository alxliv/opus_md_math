#!/usr/bin/env python3
"""
OpenAI Chat Client with Math and Markdown Rendering
Required packages: pip install fastapi uvicorn openai python-dotenv
"""

import os
import json
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    client = AsyncOpenAI(api_key=api_key)
else:
    client = None

# Request model
class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-4o-mini"


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main page"""
    with open("web/index.html", "r", encoding="utf-8") as f:
        return f.read()

async def stream_openai_response(message: str, model: str) -> AsyncGenerator[str, None]:
    """Stream responses from OpenAI API"""
    if not client:
        yield f"data: {json.dumps({'error': 'OpenAI API key not configured'})}\n\n"
        return

    try:
        stream = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful mathematics tutor. Use LaTeX notation for all mathematical expressions. For inline math use $...$ and for display math use $$...$$.  Provide clear, step-by-step explanations."
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            stream=True,
            temperature=0.7
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                yield f"data: {json.dumps({'content': content})}\n\n"

        yield "data: [DONE]\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

@app.post("/chat")
async def chat(request: ChatRequest):
    """Handle chat requests"""
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    return StreamingResponse(
        stream_openai_response(request.message, request.model),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

if __name__ == "__main__":
    import uvicorn
# try "Explain Laplace transform"
    print("=" * 60)
    if not api_key:
        print("⚠️  WARNING: OPENAI_API_KEY not found!")
        print("Create a .env file with:")
        print("OPENAI_API_KEY=your_api_key_here")
    else:
        print("✅ OpenAI API key loaded")
    print("=" * 60)
    print("🚀 Starting server at http://localhost:8000")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("\n✅ Server stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Try: uvicorn app:app --host 0.0.0.0 --port 8000")