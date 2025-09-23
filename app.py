#!/usr/bin/env python3
"""
OpenAI Chat Client with Math and Markdown Rendering

A FastAPI application that provides a web interface for mathematical conversations
with AI, featuring LaTeX rendering and streaming responses.

Required packages: pip install fastapi uvicorn openai python-dotenv
"""

import asyncio
import os
from pathlib import Path
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
from dotenv import load_dotenv
from my_logger import setup_logger;

logger = setup_logger()
# Example usage
logger.debug("Debugging message")
logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error!")

# Constants
DEFAULT_MODEL = "gpt-4o-mini"
AVAILABLE_MODELS = {
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4-turbo",
    "gpt-3.5-turbo",
}
SYSTEM_PROMPT = (
    "You are a helpful mathematics tutor. Use LaTeX notation for all "
    "mathematical expressions. For inline math use $...$ and for display "
    "math use $$...$$.  Provide clear, step-by-step explanations."
)
HTML_FILE_PATH = Path("web") / "index.html"

# Global client instance
_openai_client: Optional[AsyncOpenAI] = None


class Config:
    """Application configuration"""

    def __init__(self):
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))

    @property
    def has_openai_key(self) -> bool:
        return bool(self.openai_api_key)


def get_openai_client() -> Optional[AsyncOpenAI]:
    """Get the OpenAI client instance"""
    return _openai_client


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan manager"""
    global _openai_client
    config = Config()

    # Initialize OpenAI client if API key is available
    if config.has_openai_key:
        _openai_client = AsyncOpenAI(api_key=config.openai_api_key)
        logger.info("OpenAI client initialized")
    else:
        logger.warning("OpenAI API key not found - client not initialized")

    yield

    # Cleanup
    if _openai_client:
        await _openai_client.close()
        logger.info("OpenAI client closed")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="OpenAI Math Chat",
    description="A web interface for mathematical conversations with AI",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="web"), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],  # Restrict to local origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Only allow necessary methods
    allow_headers=["Content-Type", "Authorization"],  # Restrict headers
)

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., min_length=1, description="The user's message")
    model: str = Field(
        default=DEFAULT_MODEL,
        description="OpenAI model to use for the response"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "What is the derivative of x^2?",
                "model": "gpt-4o-mini"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")


class StreamResponse(BaseModel):
    """Stream response model"""
    content: Optional[str] = Field(None, description="Response content")
    error: Optional[str] = Field(None, description="Error message")


class ModelsResponse(BaseModel):
    """Response model for available OpenAI models"""
    models: list[str] = Field(..., description="List of available models")
    default_model: str = Field(..., description="Default model to use")

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main chat interface"""
    try:
        if not HTML_FILE_PATH.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Frontend file not found"
            )

        return HTML_FILE_PATH.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Error serving index page: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load frontend"
        )

async def stream_openai_response(message: str, model: str) -> AsyncGenerator[str, None]:
    """Stream responses from OpenAI API using Server-Sent Events format"""
    client = get_openai_client()

    if not client:
        error_response = ErrorResponse(error="OpenAI API key not configured")
        yield f"data: {error_response.model_dump_json()}\n\n"
        return

    try:
        messages = [
            ChatCompletionSystemMessageParam(role="system", content=SYSTEM_PROMPT),
            ChatCompletionUserMessageParam(role="user", content=message)
        ]

        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            max_tokens=2000
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                response = StreamResponse(content=content, error=None)
                # await asyncio.sleep(0.2)  # Simulate network delay
                yield f"data: {response.model_dump_json()}\n\n"

        yield "data: [DONE]\n\n"

    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        error_response = ErrorResponse(error=f"API error: {str(e)}")
        yield f"data: {error_response.model_dump_json()}\n\n"

@app.post("/chat")
async def chat(request: ChatRequest):
    """Handle streaming chat requests with OpenAI API"""
    client = get_openai_client()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key not configured"
        )

    if request.model not in AVAILABLE_MODELS:
        logger.warning(f"Unsupported model requested: {request.model}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model not supported"
        )

    logger.info(f"Chat request: model={request.model}, message_length={len(request.message)}")

    return StreamingResponse(
        stream_openai_response(request.message, request.model),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*"
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    client = get_openai_client()
    return {
        "status": "healthy",
        "openai_configured": client is not None,
        "version": "1.0.0"
    }


@app.get("/models", response_model=ModelsResponse)
async def list_models():
    """Return the list of available OpenAI models"""
    if not AVAILABLE_MODELS:
        logger.error("No OpenAI models configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No models configured"
        )

    if DEFAULT_MODEL not in AVAILABLE_MODELS:
        logger.warning("DEFAULT_MODEL is not in AVAILABLE_MODELS; using default fallback")

    return ModelsResponse(
        models=list(AVAILABLE_MODELS),
        default_model=DEFAULT_MODEL if DEFAULT_MODEL in AVAILABLE_MODELS else list(AVAILABLE_MODELS)[0]
    )

def print_startup_info(config: Config):
    """Print application startup information"""
    print("=" * 60)
    print("OpenAI Math Chat Server")
    print("=" * 60)

    if not config.has_openai_key:
        print("WARNING: OPENAI_API_KEY not found!")
        print("Create a .env file with:")
        print("OPENAI_API_KEY=your_api_key_here")
        print("The server will run but chat functionality will be disabled.")
    else:
        print("OpenAI API key loaded")

    print(f"Starting server at http://{config.host}:{config.port}")
    print("Health check: /health")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    # Example queries
    print("\nTry asking:")
    print('- "Explain Laplace transform"')
    print('- "What is Heaviside step function?"')
    print('- "Derive the quadratic formula"')
    print()


if __name__ == "__main__":
    import uvicorn

    config = Config()
    print_startup_info(config)

    try:
        uvicorn.run(
            app,
            host=config.host,
            port=config.port,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\nServer stopped gracefully")
    except Exception as e:
        logger.error(f"Server error: {e}")
        print(f"\nError: {e}")
        print(f"Try: uvicorn app:app --host {config.host} --port {config.port}")
