from langchain_groq import ChatGroq
from .config import config  # pyre-ignore[21]


def get_llm(temperature: float = 0.1) -> ChatGroq:
    """Returns a configured ChatGroq LLM instance using the free Groq API."""
    if not config.GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is not set. Get your free key at https://console.groq.com "
            "(no credit card required). Add it to backend/.env as GROQ_API_KEY=your_key_here"
        )
    return ChatGroq(
        model=config.GROQ_MODEL,
        api_key=config.GROQ_API_KEY,
        temperature=temperature,
        max_tokens=4096,
    )
