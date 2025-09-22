# OpenAI Math Chat

A modern FastAPI-based web application that provides an interactive chat interface for mathematical conversations with AI. Features real-time streaming responses, beautiful LaTeX mathematical expression rendering, and a clean, responsive user interface.

## Features

- **Real-time Streaming Chat** - Instant responses with Server-Sent Events
- **Mathematical Expression Rendering** - Beautiful LaTeX rendering with KaTeX
- **Multiple LaTeX Delimiters** - Supports `$...$`, `$$...$$`, `\(...\)`, and `\[...\]`
- **Smart Markdown Processing** - Preserves math expressions during markdown parsing
- **Modern UI** - Responsive design with smooth animations and gradients
- **Production Ready** - Proper error handling, logging, and resource management
- **Health Monitoring** - Built-in health check endpoint for deployment

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd opus_md_math
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create environment file:
```bash
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

4. Run the application:
```bash
python app.py
```

5. Open your browser to `http://localhost:8000`

## Usage

### Basic Chat
Simply type mathematical questions in the chat interface:

- "What is the derivative of x²?"
- "Explain the quadratic formula"
- "Derive the Laplace transform of sin(t)"

### Mathematical Expressions
The system supports various LaTeX delimiter styles:

- **Inline math**: `$x^2$` or `\(x^2\)`
- **Display math**: `$$\frac{-b \pm \sqrt{b^2-4ac}}{2a}$$` or `\[\frac{-b \pm \sqrt{b^2-4ac}}{2a}\]`

### API Usage

**Chat Endpoint:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is calculus?", "model": "gpt-4o-mini"}'
```

**Health Check:**
```bash
curl http://localhost:8000/health
```

## Architecture

### Backend (`app.py`)
- **FastAPI Framework** with async lifespan management
- **Streaming Chat Endpoint** using Server-Sent Events
- **OpenAI Integration** with proper error handling and resource cleanup
- **Custom Logging** with colored output and timestamps
- **Security Features** including CORS restrictions
- **Health Monitoring** endpoint for deployment

### Frontend (`web/index.html`)
- **Vanilla JavaScript** single-page application
- **Real-time Streaming** with accumulative content display
- **KaTeX Integration** for mathematical expression rendering
- **Markdown Processing** with LaTeX expression protection
- **Responsive Design** with modern CSS animations

### Logging (`my_logger.py`)
- **Colored Console Output** with level-specific colors
- **Timestamp Formatting** for debugging and monitoring
- **Unified Configuration** across all application components

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `HOST` | Server host address | `0.0.0.0` |
| `PORT` | Server port number | `8000` |

### Models

Supported OpenAI models:
- `gpt-4o-mini` (default)
- `gpt-4o`
- `gpt-4-turbo`
- `gpt-3.5-turbo`

## Development

### Project Structure
```
opus_md_math/
├── app.py              # Main FastAPI application
├── my_logger.py        # Custom logging configuration
├── requirements.txt    # Python dependencies
├── web/
│   └── index.html     # Frontend interface
├── .vscode/
│   └── launch.json    # VS Code debug configurations
├── .env               # Environment variables (create this)
├── CLAUDE.md          # Development documentation
└── README.md          # This file
```

### Running in Development

**Standard:**
```bash
python app.py
```

**With uvicorn (hot reload):**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**VS Code Debug:**
Use the "Debug FastAPI" configuration in `.vscode/launch.json`

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serves the chat interface |
| `/chat` | POST | Streaming chat with OpenAI |
| `/health` | GET | Health check and status |

## Deployment

### Production Considerations

1. **Environment Variables**: Set `OPENAI_API_KEY` securely
2. **CORS Configuration**: Update allowed origins for your domain
3. **Reverse Proxy**: Use nginx or similar for SSL termination
4. **Process Management**: Use systemd, supervisor, or Docker
5. **Health Monitoring**: Monitor `/health` endpoint

### Docker Example
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "app.py"]
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Kill existing process
pkill -f "python app.py"
# Or use different port
PORT=8001 python app.py
```

**OpenAI API errors:**
- Verify API key is valid and has sufficient credits
- Check rate limits and quotas
- Ensure model access permissions

**Math rendering issues:**
- Ensure KaTeX CSS and JavaScript are loading
- Check browser console for JavaScript errors
- Verify LaTeX syntax is correct

### Debugging

Enable debug logging:
```bash
# In my_logger.py, set level to DEBUG
logger.setLevel(logging.DEBUG)
```

Check health endpoint:
```bash
curl http://localhost:8000/health
```

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [OpenAI](https://openai.com/) for the chat completions API
- [KaTeX](https://katex.org/) for mathematical expression rendering
- [Marked.js](https://marked.js.org/) for markdown processing