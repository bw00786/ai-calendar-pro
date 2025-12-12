# AI Calendar Pro+ 🗓️🤖

A powerful AI-powered calendar application with voice commands, Google Calendar sync, email notifications, and natural language event management using LangGraph, LangChain, FastAPI, and React.

![AI Calendar Pro+](https://img.shields.io/badge/AI-Calendar-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![React](https://img.shields.io/badge/React-18+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal)

## 🎯 Features

### Core Features
- ✅ **AI-Powered Calendar Management** - Natural language event creation and management
- ✅ **Voice Commands** - Hands-free calendar control with speech recognition
- ✅ **Google Calendar Sync** - Two-way synchronization with Google Calendar
- ✅ **Email Notifications** - Automatic invitations, reminders, and updates
- ✅ **LangGraph Agent** - Intelligent workflow orchestration
- ✅ **MCP Server** - Model Context Protocol for tool integration
- ✅ **Material-UI Frontend** - Beautiful, responsive React interface
- ✅ **Dark/Light Mode** - Customizable theme preferences

### Advanced Capabilities
- 🎤 Speech-to-text voice input
- 🔄 Real-time event synchronization
- 📧 HTML email templates
- 📅 Calendar visualization with day picker
- 👥 Multi-attendee support
- 🏷️ Event categorization and priorities
- 🔔 Customizable reminders
- ⚡ Fast response with Ollama LLM

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9 or higher** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18 or higher** - [Download Node.js](https://nodejs.org/)
- **Ollama** - [Install Ollama](https://ollama.ai)
- **Git** - [Download Git](https://git-scm.com/)
- **Gmail Account** (for email notifications)
- **Google Cloud Account** (for Calendar API)

---

## 🚀 Quick Start Guide

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/ai-calendar-pro.git
cd ai-calendar-pro
```

### Step 2: Install Ollama and Download Model

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.com/install.sh | sh

# For Windows, download from https://ollama.ai

# Pull the model (choose one)
ollama pull gemma2        # Recommended
# or
ollama pull gpt-oss       # Alternative
# or
ollama pull llama2        # Larger model

# Verify installation
ollama list
```

---

## 🔧 Backend Setup

### Step 1: Create Python Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

### Step 2: Install Python Dependencies

```bash
# Ensure virtual environment is activated
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

The `requirements.txt` includes:
```
fastapi
uvicorn[standard]
pydantic
langchain
langchain-community
langchain-ollama
langgraph
requests
google-auth
google-auth-oauthlib
google-api-python-client
```

### Step 3: Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# backend/.env

# Email Configuration (Gmail)
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Ollama Configuration
OLLAMA_MODEL=gemma2
OLLAMA_BASE_URL=http://localhost:11434

# MCP Server
MCP_SERVER_URL=http://localhost:8000
```

### Step 4: Setup Google Calendar API

#### A. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project: **"AI Calendar Pro"**
3. Enable the **Google Calendar API**:
   - Navigate to **APIs & Services** → **Library**
   - Search for "Google Calendar API"
   - Click **Enable**

#### B. Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth 2.0 Client ID**
3. Configure OAuth consent screen if needed:
   - User Type: **External**
   - App name: **AI Calendar Pro**
   - Add your email
   - Add scopes: `https://www.googleapis.com/auth/calendar`
4. Create OAuth Client ID:
   - Application type: **Desktop app**
   - Name: **AI Calendar Desktop Client**
5. **Download** the JSON file
6. Rename it to `credentials.json`
7. Place it in the `backend/` directory

#### C. Authenticate Google Calendar

```bash
# In backend directory with venv activated
python google_oauth_setup.py
```

This will:
1. Open your browser for Google authentication
2. Ask you to authorize the application
3. Create `token.json` (stores your credentials)
4. You only need to do this once

#### D. Test Google Calendar Connection

```bash
python test_google_calendar.py
```

### Step 5: Setup Gmail App Password (for email notifications)

1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Navigate to **Security** → **2-Step Verification** (enable if not already)
3. Go to **App Passwords**
4. Generate a new app password for "Mail"
5. Copy the 16-character password
6. Add it to your `.env` file as `EMAIL_PASSWORD`

---

## 🎨 Frontend Setup

### Step 1: Navigate to Frontend Directory

```bash
cd ../frontend
# If you're in backend/, use: cd ../frontend
# If you're in project root, use: cd frontend
```

### Step 2: Install Node Dependencies

```bash
# Install all React dependencies
npm install

# This will install:
# - react & react-dom
# - @mui/material & @mui/icons-material
# - @mui/x-date-pickers
# - dayjs
# - and other dependencies from package.json
```

If `package.json` doesn't exist, create it:

```bash
npm init -y

# Install required packages
npm install react react-dom react-scripts
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material
npm install @mui/x-date-pickers
npm install dayjs
npm install web-vitals
```

### Step 3: Configure Frontend

Update `package.json` to include proxy settings:

```json
{
  "name": "ai-calendar-frontend",
  "version": "1.0.0",
  "private": true,
  "proxy": "http://localhost:8000",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "@mui/material": "^5.14.0",
    "@mui/icons-material": "^5.14.0",
    "@mui/x-date-pickers": "^6.18.0",
    "@emotion/react": "^11.11.0",
    "@emotion/styled": "^11.11.0",
    "dayjs": "^1.11.0",
    "web-vitals": "^2.1.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }
}
```

---

## 🏃 Running the Application

You'll need **three terminal windows** to run the complete application.

### Terminal 1: Start Ollama Server

```bash
# Start Ollama service
ollama serve

# Expected output:
# Ollama is now running on http://localhost:11434
```

Keep this terminal running.

### Terminal 2: Start Backend Servers

#### Option A: Start Both Servers Separately (Recommended)

**MCP Calendar Server (Terminal 2a):**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python mcp_calendar_server.py

# Expected output:
# INFO:     Started server process
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

**LangGraph Agent (Terminal 2b):**
```bash
# Open another terminal
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python langgraph_agent.py

# Expected output:
# ✅ Loaded 4 MCP tools
# ✅ Initialized Ollama with model: gemma2
# ✅ LangGraph workflow compiled
# INFO:     Uvicorn running on http://0.0.0.0:8001
```

#### Option B: Create a Startup Script

Create `start_backend.sh` (macOS/Linux):

```bash
#!/bin/bash

# Start MCP Server
cd backend
source venv/bin/activate
python mcp_calendar_server.py &

# Wait a moment
sleep 3

# Start LangGraph Agent
python langgraph_agent.py &

echo "Backend servers started!"
```

Make it executable and run:
```bash
chmod +x start_backend.sh
./start_backend.sh
```

For Windows, create `start_backend.bat`:

```batch
@echo off
cd backend
call venv\Scripts\activate

start cmd /k python mcp_calendar_server.py
timeout /t 3
start cmd /k python langgraph_agent.py

echo Backend servers started!
```

### Terminal 3: Start Frontend

```bash
cd frontend
npm start

# Expected output:
# Compiled successfully!
# Local:            http://localhost:3000
# On Your Network:  http://192.168.x.x:3000
```

Your browser should automatically open to `http://localhost:3000`.

---

## 🧪 Testing the Application

### Test Backend Endpoints

#### 1. Test MCP Server
```bash
# Health check
curl http://localhost:8000/

# List available tools
curl http://localhost:8000/mcp/tools

# Get all events
curl http://localhost:8000/events
```

#### 2. Test LangGraph Agent
```bash
# Health check
curl http://localhost:8001/health

# Send a chat message
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What events do I have today?"}'
```

#### 3. Test Event Creation
```bash
curl -X POST http://localhost:8000/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "calendar_create_event",
    "parameters": {
      "title": "Test Meeting",
      "start_time": "2025-12-15T14:00:00Z",
      "end_time": "2025-12-15T15:00:00Z",
      "description": "Testing the calendar API",
      "location": "Conference Room A"
    }
  }'
```

### Test Voice Commands in Browser

1. Open the application at `http://localhost:3000`
2. Click the microphone icon 🎤
3. Allow microphone permissions when prompted
4. Say: **"Schedule a team meeting tomorrow at 3 PM"**
5. The AI should create the event and respond

### Test Google Calendar Sync

1. Create an event in the UI
2. Check "Sync to Google Calendar"
3. Click "Create Event"
4. Open [Google Calendar](https://calendar.google.com)
5. Verify the event appears

---

## 📁 Project Structure

```
ai-calendar-pro/
├── backend/
│   ├── venv/                          # Virtual environment (created)
│   ├── mcp_calendar_server.py         # MCP Server with calendar tools
│   ├── langgraph_agent.py             # LangGraph AI agent
│   ├── google_oauth_setup.py          # Google OAuth helper
│   ├── test_google_calendar.py        # Google Calendar test script
│   ├── requirements.txt               # Python dependencies
│   ├── credentials.json               # Google OAuth credentials (you provide)
│   ├── token.json                     # Generated after OAuth
│   ├── token.pickle                   # Alternative token format
│   └── .env                           # Environment variables (you create)
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js                     # Main React component
│   │   ├── App.css                    # Styles
│   │   ├── index.js                   # React entry point
│   │   ├── index.css                  # Global styles
│   │   ├── reportWebVitals.js         # Performance monitoring
│   │   └── setupTests.js              # Test configuration
│   ├── package.json                   # Node dependencies
│   └── node_modules/                  # Installed packages (created)
│
├── README.md                          # This file
├── .gitignore                         # Git ignore rules
└── LICENSE                            # License file
```

---

## 🔐 Security Best Practices

### 1. Protect Sensitive Files

Add to `.gitignore`:

```gitignore
# Python
venv/
__pycache__/
*.pyc
*.pyo
.env

# Google Credentials
credentials.json
token.json
token.pickle

# Node
node_modules/
.env.local

# IDE
.vscode/
.idea/
*.swp
```

### 2. Environment Variables

**Never commit**:
- `.env` files
- API keys
- OAuth credentials
- Email passwords

### 3. Production Deployment

For production, use:
- Environment variable management (e.g., AWS Secrets Manager)
- HTTPS/TLS encryption
- Rate limiting
- Input validation
- CORS restrictions
- Authentication/authorization

---

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. **Ollama Not Running**

**Error:** `Failed to connect to Ollama`

**Solution:**
```bash
# Start Ollama
ollama serve

# Check if running
curl http://localhost:11434/api/tags
```

#### 2. **MCP Server 404 Error**

**Error:** `404 Client Error: Not Found for url: http://localhost:8000/mcp/tools`

**Solution:**
```bash
# Make sure MCP server is running
cd backend
source venv/bin/activate
python mcp_calendar_server.py
```

#### 3. **Virtual Environment Not Activated**

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Activate virtual environment
cd backend
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

#### 4. **Google Calendar Sync Fails**

**Error:** `Failed to sync with Google Calendar`

**Solution:**
```bash
# Re-authenticate
rm token.json token.pickle
python google_oauth_setup.py

# Verify credentials.json exists
ls -la credentials.json
```

#### 5. **Voice Recognition Not Working**

**Error:** Voice button does nothing

**Solution:**
- Use Chrome or Edge browser (Firefox has limited support)
- Allow microphone permissions
- Check browser console for errors
- Test microphone: `chrome://settings/content/microphone`

#### 6. **Email Notifications Not Sending**

**Error:** `Email credentials not configured`

**Solution:**
```bash
# Verify .env file
cat backend/.env

# Make sure EMAIL_USER and EMAIL_PASSWORD are set
# Use Gmail App Password, not regular password
```

#### 7. **Port Already in Use**

**Error:** `Address already in use`

**Solution:**
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn mcp_calendar_server:app --port 8002
```

#### 8. **React App Won't Start**

**Error:** `npm ERR! missing script: start`

**Solution:**
```bash
cd frontend
npm install
npm start
```

---

## 📚 Usage Examples

### Example 1: Create Event via Voice

1. Click microphone button
2. Say: **"Schedule a project review next Monday at 10 AM and invite john@example.com"**
3. AI creates the event and sends invitation

### Example 2: Create Event via Chat

Type in chat:
```
Create a dentist appointment on December 20th at 2 PM at Downtown Dental
```

### Example 3: Sync to Google Calendar

1. Create event in UI
2. Check "Sync to Google Calendar"
3. Click "Create Event"
4. Event appears in Google Calendar instantly

### Example 4: Send Reminder

1. Click bell icon 🔔 on any event
2. Enter recipient email
3. HTML email reminder sent immediately

### Example 5: Import from Google

1. Click "Import Google" button in header
2. All upcoming Google Calendar events imported
3. Events appear in the calendar view

---

## 🛠️ Development

### Run in Development Mode

```bash
# Backend with auto-reload
cd backend
source venv/bin/activate
uvicorn mcp_calendar_server:app --reload --port 8000
uvicorn langgraph_agent:app --reload --port 8001

# Frontend with hot-reload
cd frontend
npm start
```

### Add New MCP Tools

1. Edit `mcp_calendar_server.py`
2. Add tool to `MCP_TOOLS` dictionary
3. Implement tool function
4. Restart MCP server
5. Agent automatically discovers new tool

### Customize AI Prompts

Edit `langgraph_agent.py`:

```python
system_prompt = f"""
You are an expert AI Calendar Assistant.

[Add your custom instructions here]
"""
```

---

## 🚢 Production Deployment

### Docker Deployment

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  mcp-server:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - EMAIL_USER=${EMAIL_USER}
      - EMAIL_PASSWORD=${EMAIL_PASSWORD}
    volumes:
      - ./backend:/app

  agent:
    build: ./backend
    ports:
      - "8001:8001"
    depends_on:
      - mcp-server
    environment:
      - OLLAMA_MODEL=gemma2

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - agent
```

Run with:
```bash
docker-compose up
```

### Cloud Deployment

- **Backend:** Deploy to AWS Lambda, Google Cloud Run, or Heroku
- **Frontend:** Deploy to Vercel, Netlify, or AWS S3
- **Database:** Add PostgreSQL or MongoDB for persistence

---

## 📖 API Documentation

### MCP Server Endpoints (Port 8000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Server info |
| GET | `/mcp/tools` | List available tools |
| POST | `/mcp/call` | Execute MCP tool |
| GET | `/events` | Get all events |
| POST | `/events` | Create event |
| GET | `/events/{id}` | Get specific event |
| PUT | `/events/{id}` | Update event |
| DELETE | `/events/{id}` | Delete event |
| POST | `/events/{id}/sync-google` | Sync to Google |
| POST | `/events/{id}/reminder` | Send reminder |

### LangGraph Agent Endpoints (Port 8001)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/chat` | Chat with AI |

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Ollama** for local LLM hosting
- **LangChain** and **LangGraph** for agent framework
- **FastAPI** for backend framework
- **Material-UI** for React components
- **Google** for Calendar API

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/ai-calendar-pro/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/ai-calendar-pro/discussions)
- **Email:** support@example.com

---

## 🗺️ Roadmap

### Version 1.1
- [ ] Persistent database (PostgreSQL)
- [ ] User authentication
- [ ] Multi-user support
- [ ] Recurring events

### Version 1.2
- [ ] Mobile app (React Native)
- [ ] SMS notifications
- [ ] Microsoft Outlook integration
- [ ] Zoom/Teams integration

### Version 2.0
- [ ] AI-powered scheduling suggestions
- [ ] Smart meeting room booking
- [ ] Calendar analytics dashboard
- [ ] Team collaboration features

---

**Made with ❤️ using AI and modern web technologies**

⭐ **Star this repo if you find it helpful!** ⭐
