# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based OpenAI Math Chat application that provides a web interface for mathematical conversations with AI. The application renders LaTeX mathematical expressions using KaTeX and supports streaming responses from OpenAI's API.

## Architecture

### Backend (`app.py`)
- **FastAPI application** serving HTTP endpoints
- **Streaming chat endpoint** (`/chat`) that proxies requests to OpenAI API with server-sent events
- **Static file serving** for the web interface
- **Environment-based configuration** for OpenAI API key via `.env` file

### Frontend (`web/index.html`)
- **Single-page application** with vanilla JavaScript
- **Real-time streaming** chat interface with Server-Sent Events
- **Mathematical rendering** using KaTeX for LaTeX expressions (inline `$...$` and display `$$...$$`)
- **Markdown processing** using marked.js with LaTeX expression protection

### Key Dependencies
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `openai` - OpenAI API client with streaming support
- `python-dotenv` - Environment variable management

## Development Commands

### Running the Application
```bash
# Start the development server
python app.py

# Alternative using uvicorn directly
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Environment Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn openai python-dotenv
```

### Configuration
- Copy `.env` file and set `OPENAI_API_KEY` for OpenAI integration
- The application will run without API key but show warnings

## File Structure
```
app.py          # Main FastAPI application
web/            # Frontend assets
  index.html    # Single-page chat interface
.env            # Environment variables (API keys)
.gitignore      # Git ignore patterns
```

## API Endpoints

- `GET /` - Serves the main chat interface
- `POST /chat` - Streaming chat endpoint accepting `{"message": "...", "model": "gpt-4o-mini"}`

## Frontend Integration Notes

The JavaScript frontend:
- Processes LaTeX expressions before markdown parsing to prevent conflicts
- Uses placeholder replacement to protect math expressions during markdown rendering
- Implements real-time streaming with accumulative content display
- Automatically renders math expressions using KaTeX after each content update