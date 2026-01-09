"""
URL Shortener Application
A modern, fast URL shortening service built with FastAPI
"""

import string
import random
import hashlib
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, HttpUrl

app = FastAPI(
    title="URL Shortener",
    description="A modern URL shortening service",
    version="1.0.0"
)

# In-memory storage (replace with database in production)
url_database: dict[str, dict] = {}
stats: dict[str, int] = {"total_urls": 0, "total_clicks": 0}

# Characters for generating short codes
CHARACTERS = string.ascii_letters + string.digits


class URLCreate(BaseModel):
    """Request model for creating a short URL"""
    url: HttpUrl
    custom_code: Optional[str] = None


class URLResponse(BaseModel):
    """Response model for a shortened URL"""
    short_code: str
    short_url: str
    original_url: str
    created_at: str
    clicks: int


def generate_short_code(length: int = 6) -> str:
    """Generate a random short code"""
    return ''.join(random.choices(CHARACTERS, k=length))


def generate_hash_code(url: str) -> str:
    """Generate a deterministic short code based on URL hash"""
    hash_object = hashlib.md5(url.encode())
    return hash_object.hexdigest()[:6]


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main page"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shortr — URL Shortener</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Sora:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0a0a0f;
            --bg-secondary: #12121a;
            --bg-tertiary: #1a1a25;
            --accent-primary: #00ff88;
            --accent-secondary: #00cc6a;
            --accent-glow: rgba(0, 255, 136, 0.3);
            --text-primary: #ffffff;
            --text-secondary: #8888aa;
            --text-muted: #555566;
            --border-color: #2a2a3a;
            --error: #ff4466;
            --success: #00ff88;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Sora', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* Animated background */
        .bg-pattern {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            background: 
                radial-gradient(circle at 20% 20%, rgba(0, 255, 136, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(0, 204, 106, 0.05) 0%, transparent 50%),
                linear-gradient(135deg, var(--bg-primary) 0%, #0d0d14 100%);
        }

        .grid-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            background-image: 
                linear-gradient(rgba(0, 255, 136, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 136, 0.03) 1px, transparent 1px);
            background-size: 50px 50px;
            animation: gridMove 20s linear infinite;
        }

        @keyframes gridMove {
            0% { transform: translateY(0); }
            100% { transform: translateY(50px); }
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        header {
            text-align: center;
            padding: 60px 0 40px;
        }

        .logo {
            font-size: 3.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -2px;
            margin-bottom: 16px;
            position: relative;
            display: inline-block;
        }

        .logo::after {
            content: '_';
            animation: blink 1s step-end infinite;
            -webkit-text-fill-color: var(--accent-primary);
        }

        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0; }
        }

        .tagline {
            color: var(--text-secondary);
            font-size: 1.1rem;
            font-weight: 300;
            letter-spacing: 0.5px;
        }

        .main-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 24px;
            padding: 48px;
            margin: 20px 0;
            position: relative;
            overflow: hidden;
        }

        .main-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, transparent, var(--accent-primary), transparent);
        }

        .input-group {
            display: flex;
            gap: 12px;
            margin-bottom: 24px;
        }

        .url-input {
            flex: 1;
            padding: 18px 24px;
            font-size: 1rem;
            font-family: 'JetBrains Mono', monospace;
            background: var(--bg-tertiary);
            border: 2px solid var(--border-color);
            border-radius: 12px;
            color: var(--text-primary);
            transition: all 0.3s ease;
        }

        .url-input:focus {
            outline: none;
            border-color: var(--accent-primary);
            box-shadow: 0 0 30px var(--accent-glow);
        }

        .url-input::placeholder {
            color: var(--text-muted);
        }

        .shorten-btn {
            padding: 18px 36px;
            font-size: 1rem;
            font-family: 'Sora', sans-serif;
            font-weight: 600;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            border: none;
            border-radius: 12px;
            color: var(--bg-primary);
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .shorten-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 40px var(--accent-glow);
        }

        .shorten-btn:active {
            transform: translateY(0);
        }

        .shorten-btn.loading {
            pointer-events: none;
        }

        .shorten-btn.loading::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 20px;
            height: 20px;
            margin: -10px 0 0 -10px;
            border: 2px solid transparent;
            border-top-color: var(--bg-primary);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .custom-code-toggle {
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--text-secondary);
            font-size: 0.9rem;
            cursor: pointer;
            margin-bottom: 16px;
        }

        .custom-code-toggle input[type="checkbox"] {
            accent-color: var(--accent-primary);
            width: 18px;
            height: 18px;
        }

        .custom-code-input {
            display: none;
            margin-bottom: 16px;
        }

        .custom-code-input.visible {
            display: block;
        }

        .custom-code-input input {
            width: 100%;
            padding: 14px 20px;
            font-size: 0.95rem;
            font-family: 'JetBrains Mono', monospace;
            background: var(--bg-tertiary);
            border: 2px solid var(--border-color);
            border-radius: 10px;
            color: var(--text-primary);
            transition: all 0.3s ease;
        }

        .custom-code-input input:focus {
            outline: none;
            border-color: var(--accent-primary);
        }

        /* Result section */
        .result {
            display: none;
            padding: 24px;
            background: var(--bg-tertiary);
            border-radius: 16px;
            border: 1px solid var(--border-color);
            animation: slideUp 0.4s ease;
        }

        .result.visible {
            display: block;
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .result-label {
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .short-url {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
        }

        .short-url-text {
            flex: 1;
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.2rem;
            color: var(--accent-primary);
            word-break: break-all;
        }

        .copy-btn {
            padding: 12px 20px;
            font-size: 0.9rem;
            font-family: 'Sora', sans-serif;
            font-weight: 500;
            background: transparent;
            border: 2px solid var(--accent-primary);
            border-radius: 8px;
            color: var(--accent-primary);
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .copy-btn:hover {
            background: var(--accent-primary);
            color: var(--bg-primary);
        }

        .copy-btn.copied {
            background: var(--accent-primary);
            color: var(--bg-primary);
        }

        .original-url {
            font-size: 0.85rem;
            color: var(--text-muted);
            word-break: break-all;
        }

        .original-url span {
            color: var(--text-secondary);
        }

        /* Error message */
        .error-msg {
            display: none;
            padding: 16px 20px;
            background: rgba(255, 68, 102, 0.1);
            border: 1px solid var(--error);
            border-radius: 10px;
            color: var(--error);
            font-size: 0.9rem;
            margin-top: 16px;
        }

        .error-msg.visible {
            display: block;
            animation: shake 0.5s ease;
        }

        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }

        /* Stats section */
        .stats-section {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-top: 40px;
        }

        .stat-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 28px;
            text-align: center;
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            border-color: var(--accent-primary);
            transform: translateY(-4px);
        }

        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--accent-primary);
            font-family: 'JetBrains Mono', monospace;
        }

        .stat-label {
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-top: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Recent URLs */
        .recent-section {
            margin-top: 40px;
        }

        .section-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 20px;
            color: var(--text-primary);
        }

        .recent-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .recent-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 20px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            transition: all 0.3s ease;
        }

        .recent-item:hover {
            border-color: var(--accent-primary);
        }

        .recent-short {
            font-family: 'JetBrains Mono', monospace;
            color: var(--accent-primary);
            font-size: 0.95rem;
        }

        .recent-original {
            color: var(--text-muted);
            font-size: 0.85rem;
            max-width: 300px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .recent-clicks {
            color: var(--text-secondary);
            font-size: 0.85rem;
        }

        /* Footer */
        footer {
            margin-top: auto;
            padding: 40px 0 20px;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.85rem;
        }

        footer a {
            color: var(--accent-primary);
            text-decoration: none;
        }

        /* Mobile responsive */
        @media (max-width: 640px) {
            .logo {
                font-size: 2.5rem;
            }

            .main-card {
                padding: 32px 24px;
            }

            .input-group {
                flex-direction: column;
            }

            .shorten-btn {
                width: 100%;
            }

            .stats-section {
                grid-template-columns: 1fr;
            }

            .recent-item {
                flex-direction: column;
                align-items: flex-start;
                gap: 8px;
            }

            .recent-original {
                max-width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="bg-pattern"></div>
    <div class="grid-overlay"></div>

    <div class="container">
        <header>
            <h1 class="logo">Shortr</h1>
            <p class="tagline">Transform long URLs into memorable short links</p>
        </header>

        <main>
            <div class="main-card">
                <div class="input-group">
                    <input 
                        type="url" 
                        id="urlInput" 
                        class="url-input" 
                        placeholder="Paste your long URL here..."
                        autocomplete="off"
                    >
                    <button class="shorten-btn" id="shortenBtn" onclick="shortenUrl()">
                        Shorten
                    </button>
                </div>

                <label class="custom-code-toggle">
                    <input type="checkbox" id="customCodeCheck" onchange="toggleCustomCode()">
                    Use custom short code
                </label>

                <div class="custom-code-input" id="customCodeSection">
                    <input 
                        type="text" 
                        id="customCode" 
                        placeholder="Enter custom code (e.g., my-link)"
                        maxlength="20"
                    >
                </div>

                <div class="result" id="result">
                    <p class="result-label">Your shortened URL</p>
                    <div class="short-url">
                        <span class="short-url-text" id="shortUrlText"></span>
                        <button class="copy-btn" id="copyBtn" onclick="copyToClipboard()">Copy</button>
                    </div>
                    <p class="original-url">
                        <span>Original:</span> <span id="originalUrlText"></span>
                    </p>
                </div>

                <div class="error-msg" id="errorMsg"></div>
            </div>

            <div class="stats-section">
                <div class="stat-card">
                    <div class="stat-value" id="totalUrls">0</div>
                    <div class="stat-label">URLs Shortened</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="totalClicks">0</div>
                    <div class="stat-label">Total Clicks</div>
                </div>
            </div>

            <div class="recent-section" id="recentSection" style="display: none;">
                <h2 class="section-title">Recent URLs</h2>
                <div class="recent-list" id="recentList"></div>
            </div>
        </main>

        <footer>
            <p>Built with FastAPI & Love</p>
        </footer>
    </div>

    <script>
        const BASE_URL = window.location.origin;
        let recentUrls = JSON.parse(localStorage.getItem('recentUrls') || '[]');

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            loadStats();
            renderRecentUrls();
            
            // Enter key to submit
            document.getElementById('urlInput').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') shortenUrl();
            });
        });

        function toggleCustomCode() {
            const section = document.getElementById('customCodeSection');
            const checkbox = document.getElementById('customCodeCheck');
            section.classList.toggle('visible', checkbox.checked);
        }

        async function shortenUrl() {
            const urlInput = document.getElementById('urlInput');
            const customCode = document.getElementById('customCode');
            const useCustom = document.getElementById('customCodeCheck').checked;
            const btn = document.getElementById('shortenBtn');
            const result = document.getElementById('result');
            const errorMsg = document.getElementById('errorMsg');

            // Reset states
            result.classList.remove('visible');
            errorMsg.classList.remove('visible');

            const url = urlInput.value.trim();
            if (!url) {
                showError('Please enter a URL');
                return;
            }

            // Add protocol if missing
            let finalUrl = url;
            if (!url.match(/^https?:\/\//)) {
                finalUrl = 'https://' + url;
            }

            btn.classList.add('loading');
            btn.textContent = '';

            try {
                const payload = { url: finalUrl };
                if (useCustom && customCode.value.trim()) {
                    payload.custom_code = customCode.value.trim();
                }

                const response = await fetch('/api/shorten', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || 'Failed to shorten URL');
                }

                // Show result
                const shortUrl = `${BASE_URL}/${data.short_code}`;
                document.getElementById('shortUrlText').textContent = shortUrl;
                document.getElementById('originalUrlText').textContent = data.original_url;
                result.classList.add('visible');

                // Save to recent
                addToRecent({
                    short_code: data.short_code,
                    original_url: data.original_url,
                    clicks: 0
                });

                // Update stats
                loadStats();

                // Clear inputs
                urlInput.value = '';
                customCode.value = '';

            } catch (error) {
                showError(error.message);
            } finally {
                btn.classList.remove('loading');
                btn.textContent = 'Shorten';
            }
        }

        function showError(message) {
            const errorMsg = document.getElementById('errorMsg');
            errorMsg.textContent = message;
            errorMsg.classList.add('visible');
        }

        async function copyToClipboard() {
            const shortUrl = document.getElementById('shortUrlText').textContent;
            const copyBtn = document.getElementById('copyBtn');
            
            try {
                await navigator.clipboard.writeText(shortUrl);
                copyBtn.textContent = 'Copied!';
                copyBtn.classList.add('copied');
                
                setTimeout(() => {
                    copyBtn.textContent = 'Copy';
                    copyBtn.classList.remove('copied');
                }, 2000);
            } catch (err) {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = shortUrl;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                
                copyBtn.textContent = 'Copied!';
                copyBtn.classList.add('copied');
                
                setTimeout(() => {
                    copyBtn.textContent = 'Copy';
                    copyBtn.classList.remove('copied');
                }, 2000);
            }
        }

        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                animateNumber('totalUrls', data.total_urls);
                animateNumber('totalClicks', data.total_clicks);
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        }

        function animateNumber(elementId, target) {
            const element = document.getElementById(elementId);
            const current = parseInt(element.textContent) || 0;
            const increment = Math.ceil((target - current) / 20);
            
            if (current < target) {
                element.textContent = Math.min(current + increment, target);
                setTimeout(() => animateNumber(elementId, target), 30);
            }
        }

        function addToRecent(urlData) {
            // Remove duplicates
            recentUrls = recentUrls.filter(u => u.short_code !== urlData.short_code);
            
            // Add to beginning
            recentUrls.unshift(urlData);
            
            // Keep only last 5
            recentUrls = recentUrls.slice(0, 5);
            
            // Save to localStorage
            localStorage.setItem('recentUrls', JSON.stringify(recentUrls));
            
            renderRecentUrls();
        }

        function renderRecentUrls() {
            const section = document.getElementById('recentSection');
            const list = document.getElementById('recentList');
            
            if (recentUrls.length === 0) {
                section.style.display = 'none';
                return;
            }
            
            section.style.display = 'block';
            list.innerHTML = recentUrls.map(url => `
                <div class="recent-item">
                    <a href="${BASE_URL}/${url.short_code}" target="_blank" class="recent-short">
                        ${BASE_URL}/${url.short_code}
                    </a>
                    <span class="recent-original">${url.original_url}</span>
                </div>
            `).join('');
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.post("/api/shorten")
async def create_short_url(url_data: URLCreate, request: Request):
    """Create a shortened URL"""
    original_url = str(url_data.url)
    
    # Use custom code or generate one
    if url_data.custom_code:
        short_code = url_data.custom_code
        # Validate custom code
        if not short_code.replace("-", "").replace("_", "").isalnum():
            raise HTTPException(
                status_code=400, 
                detail="Custom code can only contain letters, numbers, hyphens, and underscores"
            )
        if short_code in url_database:
            raise HTTPException(
                status_code=400, 
                detail="This custom code is already taken"
            )
    else:
        # Generate unique short code
        short_code = generate_short_code()
        while short_code in url_database:
            short_code = generate_short_code()
    
    # Store the URL
    url_database[short_code] = {
        "original_url": original_url,
        "created_at": datetime.now().isoformat(),
        "clicks": 0
    }
    
    stats["total_urls"] += 1
    
    base_url = str(request.base_url).rstrip("/")
    
    return {
        "short_code": short_code,
        "short_url": f"{base_url}/{short_code}",
        "original_url": original_url,
        "created_at": url_database[short_code]["created_at"],
        "clicks": 0
    }


@app.get("/api/stats")
async def get_stats():
    """Get service statistics"""
    return stats


@app.get("/api/url/{short_code}")
async def get_url_info(short_code: str):
    """Get information about a shortened URL"""
    if short_code not in url_database:
        raise HTTPException(status_code=404, detail="URL not found")
    
    return {
        "short_code": short_code,
        "original_url": url_database[short_code]["original_url"],
        "created_at": url_database[short_code]["created_at"],
        "clicks": url_database[short_code]["clicks"]
    }


@app.get("/{short_code}")
async def redirect_to_url(short_code: str):
    """Redirect to the original URL"""
    if short_code not in url_database:
        raise HTTPException(status_code=404, detail="URL not found")
    
    # Increment click counter
    url_database[short_code]["clicks"] += 1
    stats["total_clicks"] += 1
    
    return RedirectResponse(
        url=url_database[short_code]["original_url"],
        status_code=307
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

