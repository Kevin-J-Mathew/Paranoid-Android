# Paranoid Android (Sentinel-Agent)

## Overview
Paranoid Android is an autonomous, context-aware Quality Assurance orchestrator. It functions as a complete AI-driven testing pipeline that translates unrefined User Stories directly into executable, validated, and historically-aware integration tests. 

Rather than relying on static scripts, the system leverages a multi-agent architecture to read requirements, query local vector databases for historical context, generate browser automation scripts, execute them in sandboxed environments, and autonomously evaluate the outcomes for regression risks.

## Real-World Application
In traditional CI/CD pipelines, automated testing suffers from high maintenance overhead, flaky script execution, and a lack of contextual memory regarding past bugs. Paranoid Android solves these structural inefficiencies.

**Key Scenarios:**
- **Zero-Touch Test Generation:** A Product Manager writes a Jira ticket or User Story. The system ingests the raw text, extracts the acceptance criteria, and immediately generates the corresponding Playwright interaction scripts without human intervention.
- **Context-Aware Regression Triaging:** When a test fails, the system does not simply throw an error. It queries its local RAG (Retrieval-Augmented Generation) memory to determine if this failure is a known flaky component, a documented past bug, or a genuinely new regression, drastically reducing false positives.
- **Self-Healing Automation:** If a generated test script fails due to a selector mismatch or structural DOM change, the execution agent feeds the exact traceback back into the language model to patch the script and re-execute it dynamically.

## Core Architecture
The backend operates via a state-machine orchestrated by LangGraph, moving sequentially through specialized agents:

1. **Requirements parsing:** Ingests the raw narrative and outputs structured, testable criteria.
2. **Knowledge Retrieval (RAG):** Searches the local ChromaDB vector store for semantic matches against past bugs, historical test executions, and baselines.
3. **Test Generation:** Synthesizes the requirements and the historical context into functional Playwright execution scripts.
4. **Execution & Sandboxing:** Physically launches a headless browser, executes the newly generated Python/Playwright script against the target, and captures runtime telemetry and screenshots.
5. **Regression Analysis:** Compares the execution latency, outcome, and traceback against the retrieved baseline datastore to assign a statistical risk severity.
6. **Reporting & Memory Consolidation:** Compiles a standalone HTML artifact of the run and embeds the newly discovered vectors back into ChromaDB to perpetually improve future context retrieval.

## Technology Stack

**Backend System:**
- **Python / FastAPI:** High-performance asynchronous API tier and Server-Sent Events (SSE) streaming.
- **LangGraph:** Graph-based state orchestration for the multi-agent pipeline.
- **LLM Inference:** Groq API utilizing the `llama-3.3-70b-versatile` model for high-throughput, low-latency reasoning.
- **Vector Database:** ChromaDB coupled with `SentenceTransformers` (`all-MiniLM-L6-v2`) for entirely localized Retrieval-Augmented Generation.
- **Browser Automation:** Playwright for Python.
- **Relational Storage:** SQLite with `aiosqlite` for asynchronous run metadata persistence.

**Frontend Interface:**
- **React 18 / Vite:** Modern component architecture and optimized build tooling.
- **Tailwind CSS:** Utility-first styling configured with a strict custom dark-mode design system.
- **Axios:** Asynchronous HTTP/SSE client for real-time telemetry streaming from the backend.

## Local Installation

**Prerequisites:**
You will need a Groq API Key.

**Backend Initialization:**
1. Navigate to the `backend` directory.
2. Copy the `.env.example` file to `.env` and insert your API credentials.
3. Install the required Python packages and browser binaries:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
4. Seed the local vector database with foundational knowledge:
   ```bash
   python seed_knowledge.py
   ```
5. Boot the FastAPI server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

**Frontend Initialization:**
1. Navigate to the `frontend` directory.
2. Install the Node modules:
   ```bash
   npm install
   ```
3. Boot the Vite development server:
   ```bash
   npm run dev
   ```

Access the dashboard at `http://localhost:5173`. Select a simulated User Story from the orchestrator and initiate a run to monitor the agent pipeline in real time.
