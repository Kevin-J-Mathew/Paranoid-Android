# Sentinel-Agent: Autonomous Context-Aware QA Orchestrator

> AI-Agent Driven, Context-Aware Release Testing MVP

## Quick Start

### 1. Get FREE Groq API Key
Visit https://console.groq.com → Sign up (no credit card) → API Keys → Create Key

### 2. Backend Setup
```bash
cd backend
cp ../.env.example .env
# Edit .env and add your GROQ_API_KEY

pip install -r requirements.txt
playwright install chromium

# Seed the knowledge base (run once)
python seed_knowledge.py

# Start the API server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. Open Dashboard
Navigate to: http://localhost:5173

## Architecture
- **LangGraph** multi-agent pipeline (6 specialized agents)
- **Groq API** free LLM (llama-3.3-70b-versatile)
- **ChromaDB** + sentence-transformers RAG (fully local, no API key)
- **Playwright** automated test execution
- **FastAPI** + SSE real-time streaming
- **React** + Tailwind dashboard

## Demo Flow
1. Select a user story from the list
2. Click "Run Tests"
3. Watch the 6 agents work in real time on the dashboard
4. View generated tests, execution results, regression analysis
5. Open the full HTML report with screenshots and evidence
