````markdown
# 🚀 AI Backend API - Production Ready

A high-performance, production-ready AI API built with FastAPI and OpenAI, optimized for Railway deployment and mobile frontends.

## ✨ Features

- **🤖 OpenAI Integration** - Latest GPT models (GPT-4o, GPT-4o-mini)
- **💬 Chat Endpoint** - Simple POST endpoint for AI responses
- **⚡ Streaming Support** - Real-time responses with Server-Sent Events (SSE)
- **🧠 Conversation Memory** - Maintains chat history per conversation
- **📱 Mobile Optimized** - CORS enabled for all frontends
- **🔒 Security** - Environment variable based API key management
- **📊 Logging** - Production-grade logging system
- **✅ Health Check** - Monitoring endpoint for uptime
- **📝 Type Validation** - Pydantic models for request validation
- **⚙️ Async/Await** - High-performance async operations

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- OpenAI API Key (get one [here](https://platform.openai.com/api-keys))

### Local Setup

1. **Clone and navigate to the repository**
   ```bash
   cd ai-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

5. **Run locally**
   ```bash
   python main.py
   ```
   Visit: `http://localhost:8000/docs`

## 🚂 Railway Deployment

### Step 1: Connect Repository
1. Go to [Railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub"
4. Connect your GitHub repository

### Step 2: Add Environment Variables
1. In Railway dashboard, go to your **ai-backend** project
2. Click **Variables**
3. Add:
   ```
   OPENAI_API_KEY = sk-your-actual-api-key
   ```
4. Click **Deploy**

### Step 3: Connect Domain
1. Go to **Settings** → **Domains**
2. Click **Add Domain**
3. Enter: `bbytota87.duckdns.org`
4. Railway shows you DNS records
5. Update your DuckDNS settings
6. Wait 5-15 minutes for propagation

### Step 4: Test Deployment
```bash
curl https://bbytota87.duckdns.org/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-05-20T10:30:00.000000",
  "api_version": "1.0.0"
}
```

## 📡 API Endpoints

### 1. Health Check
```http
GET /health
```
Monitor if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-05-20T10:30:00.000000",
  "api_version": "1.0.0"
}
```

### 2. Chat (Non-Streaming)
```http
POST /chat
Content-Type: application/json

{
  "prompt": "What is the capital of France?",
  "conversation_id": "conv_12345",
  "model": "gpt-4o-mini",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**Response:**
```json
{
  "conversation_id": "conv_12345",
  "response": "The capital of France is Paris...",
  "model": "gpt-4o-mini",
  "tokens_used": {
    "prompt_tokens": 15,
    "completion_tokens": 45,
    "total_tokens": 60
  },
  "timestamp": "2025-05-20T10:30:00.000000"
}
```

### 3. Chat Streaming (Real-time)
```http
POST /stream
Content-Type: application/json

{
  "prompt": "Explain quantum computing",
  "conversation_id": "conv_12345",
  "model": "gpt-4o-mini",
  "temperature": 0.7
}
```

**Response:** Server-Sent Events (SSE) stream
```
data: {"type": "content", "content": "Quantum", "timestamp": "..."}
data: {"type": "content", "content": " computing", "timestamp": "..."}
data: {"type": "content", "content": " is...", "timestamp": "..."}
data: {"type": "done", "content": "conv_12345", "timestamp": "..."}
```

### 4. Get Conversation History
```http
GET /conversation/conv_12345
```

**Response:**
```json
{
  "conversation_id": "conv_12345",
  "messages": [
    {
      "role": "user",
      "content": "Hello!"
    },
    {
      "role": "assistant",
      "content": "Hi! How can I help?"
    }
  ],
  "message_count": 2
}
```

### 5. Clear Conversation
```http
DELETE /conversation/conv_12345
```

**Response:**
```json
{
  "status": "cleared",
  "conversation_id": "conv_12345"
}
```

## 📱 Usage Examples

### JavaScript/Fetch (Mobile/Web)

#### Basic Chat
```javascript
const response = await fetch('https://bbytota87.duckdns.org/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: "Hello, how are you?",
    conversation_id: "user_123"
  })
});

const data = await response.json();
console.log(data.response);
```

#### Streaming Chat
```javascript
const response = await fetch('https://bbytota87.duckdns.org/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: "Write a poem about AI",
    conversation_id: "user_123"
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const line = decoder.decode(value);
  if (line.startsWith('data: ')) {
    const event = JSON.parse(line.slice(6));
    console.log(event.content);
  }
}
```

### Python Requests

```python
import requests

response = requests.post('https://bbytota87.duckdns.org/chat', json={
    'prompt': 'Explain relativity',
    'conversation_id': 'user_123',
    'temperature': 0.8
})

print(response.json()['response'])
```

### cURL

```bash
curl -X POST https://bbytota87.duckdns.org/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is machine learning?",
    "conversation_id": "user_123"
  }'
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | - | Your OpenAI API key |
| `PORT` | ❌ No | 8000 | Server port (Railway sets this) |
| `ALLOWED_ORIGINS` | ❌ No | * | CORS origins (comma-separated) |
| `LOG_LEVEL` | ❌ No | INFO | Logging level |

### Request Parameters

#### ChatRequest
- **prompt** (string, required): User's message (1-4000 chars)
- **conversation_id** (string, optional): ID for conversation history
- **model** (string, default: "gpt-4o-mini"): OpenAI model
- **temperature** (float, default: 0.7): Creativity (0-2)
- **max_tokens** (int, default: 2000): Response length (1-4000)
- **stream** (boolean, default: false): Enable streaming

## 📊 Performance

- **Response Time**: ~500ms-2s (depending on prompt complexity)
- **Streaming**: Real-time token delivery (~50-100ms per token)
- **Concurrent Users**: Supports multiple simultaneous requests
- **Memory**: ~100MB base + conversation history
- **Cost**: Per-token billing from OpenAI

## 🔒 Security Best Practices

1. **Never commit `.env` file** - It's in `.gitignore`
2. **Use Railway Variables** - Not local `.env` files
3. **Rotate API keys regularly** - Check OpenAI dashboard
4. **Validate input** - Pydantic models handle this
5. **HTTPS only** - Railway provides SSL/TLS
6. **Rate limiting** - Consider adding in production

## 🐛 Troubleshooting

### API Key Error
```
ValueError: OPENAI_API_KEY environment variable is required
```
**Solution:** Add `OPENAI_API_KEY` to Railway Variables

### 401 Unauthorized
```
OpenAI API error: Incorrect API key provided
```
**Solution:** Check your API key is correct and hasn't expired

### Railway Deploy Failed
**Solution:** Check logs in Railway dashboard:
1. Click your project
2. View **Deployments**
3. Click failed deployment
4. Check **Logs** tab

### Streaming Not Working
**Solution:** Ensure you're using:
- `POST /stream` endpoint (not `/chat`)
- `text/event-stream` media type handling
- Proper SSE event parsing

### CORS Issues
**Solution:** Check `ALLOWED_ORIGINS` variable in Railway

## 📈 Monitoring

### Health Check Script
```bash
#!/bin/bash
while true; do
  curl -s https://bbytota87.duckdns.org/health
  sleep 60
done
```

### Check Logs
Railway Logs → Deployments → Click latest → View logs

## 🤝 Support

- **OpenAI Docs**: https://platform.openai.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Railway Docs**: https://docs.railway.app
- **Issues**: Create a GitHub issue in this repository

## 📄 License

MIT License - Feel free to use this for your projects!

---

**Made with ❤️ for AI development**
````
