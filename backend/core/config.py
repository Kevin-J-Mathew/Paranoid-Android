import os
from dotenv import load_dotenv

# Load .env from the backend directory (parent of core/)
_backend_dir = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(_backend_dir, ".env"))

class Config:
    # Groq LLM (FREE - get key at console.groq.com, no credit card needed)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    # ChromaDB
    CHROMA_DB_PATH: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
    CHROMA_COLLECTION_TESTS: str = "test_knowledge"
    CHROMA_COLLECTION_BUGS: str = "bug_history"
    CHROMA_COLLECTION_RUNS: str = "run_baselines"
    
    # Paths
    TESTS_OUTPUT_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tests_output")
    REPORTS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
    SCREENSHOTS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "screenshots")
    
    # Target App for Playwright Tests (public stable demo app)
    TARGET_APP_URL: str = "https://demo.playwright.dev/todomvc"
    
    # Jira (optional — leave blank to use mock data)
    JIRA_SERVER: str = os.getenv("JIRA_SERVER", "")
    JIRA_EMAIL: str = os.getenv("JIRA_EMAIL", "")
    JIRA_API_TOKEN: str = os.getenv("JIRA_API_TOKEN", "")
    JIRA_PROJECT_KEY: str = os.getenv("JIRA_PROJECT_KEY", "")
    
    # SQLite
    DATABASE_URL: str = "sqlite+aiosqlite:///./sentinel.db"

config = Config()
