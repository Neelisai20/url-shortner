# Shortr — URL Shortener

A modern, fast URL shortening service built with FastAPI and a beautiful dark-themed UI.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)

## Features

- 🚀 **Fast** — Built with FastAPI for high performance
- 🎨 **Beautiful UI** — Modern dark theme with smooth animations
- 🔗 **Custom Codes** — Use your own custom short codes
- 📊 **Statistics** — Track total URLs and clicks
- 📋 **Copy to Clipboard** — One-click copy functionality
- 💾 **Recent URLs** — Locally stored recent URLs
- 📱 **Responsive** — Works on desktop and mobile

## Quick Start

### 1. Create a virtual environment (recommended)

```bash
cd "url shortner"
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
python app.py
```

Or using uvicorn directly:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 4. Open in browser

Navigate to [http://localhost:8000](http://localhost:8000)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Main web interface |
| `POST` | `/api/shorten` | Create a short URL |
| `GET` | `/api/stats` | Get service statistics |
| `GET` | `/api/url/{code}` | Get URL information |
| `GET` | `/{code}` | Redirect to original URL |

### Create Short URL

```bash
curl -X POST http://localhost:8000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/url"}'
```

Response:
```json
{
  "short_code": "abc123",
  "short_url": "http://localhost:8000/abc123",
  "original_url": "https://example.com/very/long/url",
  "created_at": "2024-01-09T12:00:00",
  "clicks": 0
}
```

### Custom Short Code

```bash
curl -X POST http://localhost:8000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "custom_code": "my-link"}'
```

## Project Structure

```
url shortner/
├── app.py              # Main FastAPI application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Production Notes

For production deployment:

1. Replace in-memory storage with a proper database (Redis, PostgreSQL, etc.)
2. Add rate limiting
3. Configure CORS properly
4. Use environment variables for configuration
5. Deploy behind a reverse proxy (nginx, etc.)

## License

MIT License — feel free to use and modify!

