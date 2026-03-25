import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import json
import uuid
from .config import config  # pyre-ignore[21]

# Load embedding model once (local, free, no API needed)
_embedding_model: Optional[SentenceTransformer] = None


def get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model


def get_chroma_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=config.CHROMA_DB_PATH)


def embed_texts(texts: List[str]) -> List[List[float]]:
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()


class RAGPipeline:
    def __init__(self):
        self.client = get_chroma_client()
        self.test_collection = self.client.get_or_create_collection(
            name=config.CHROMA_COLLECTION_TESTS,
            metadata={"hnsw:space": "cosine"}
        )
        self.bug_collection = self.client.get_or_create_collection(
            name=config.CHROMA_COLLECTION_BUGS,
            metadata={"hnsw:space": "cosine"}
        )
        self.run_collection = self.client.get_or_create_collection(
            name=config.CHROMA_COLLECTION_RUNS,
            metadata={"hnsw:space": "cosine"}
        )

    def add_test_case(self, story_id: str, story_text: str, test_code: str,
                      test_name: str, outcome: str, metadata: dict = None):
        """Store a test case in the knowledge base."""
        doc_id = str(uuid.uuid4())
        document_text = f"Story: {story_text}\nTest: {test_name}\nOutcome: {outcome}"
        embeddings = embed_texts([document_text])
        meta = {
            "story_id": story_id,
            "test_name": test_name,
            "outcome": outcome,
            "test_code": test_code[:2000],  # ChromaDB metadata limit
            **(metadata or {})
        }
        self.test_collection.add(
            ids=[doc_id],
            embeddings=embeddings,
            documents=[document_text],
            metadatas=[meta]
        )
        return doc_id

    def add_bug_report(self, bug_id: str, title: str, description: str,
                       affected_area: str, severity: str):
        """Store a bug report for RAG context."""
        doc_id = str(uuid.uuid4())
        document_text = f"Bug: {title}\nDescription: {description}\nArea: {affected_area}\nSeverity: {severity}"
        embeddings = embed_texts([document_text])
        self.bug_collection.add(
            ids=[doc_id],
            embeddings=embeddings,
            documents=[document_text],
            metadatas=[{
                "bug_id": bug_id,
                "title": title,
                "affected_area": affected_area,
                "severity": severity
            }]
        )

    def add_run_baseline(self, story_id: str, test_name: str,
                          pass_rate: float, avg_duration_ms: float):
        """Store run baseline for regression detection."""
        doc_id = str(uuid.uuid4())
        document_text = f"Baseline for story {story_id} test {test_name}: pass_rate={pass_rate}"
        embeddings = embed_texts([document_text])
        self.run_collection.add(
            ids=[doc_id],
            embeddings=embeddings,
            documents=[document_text],
            metadatas=[{
                "story_id": story_id,
                "test_name": test_name,
                "pass_rate": pass_rate,
                "avg_duration_ms": avg_duration_ms
            }]
        )

    def query_similar_tests(self, story_text: str, n_results: int = 5) -> List[Dict]:
        """Find similar past test cases relevant to a user story."""
        if self.test_collection.count() == 0:
            return []
        embeddings = embed_texts([story_text])
        results = self.test_collection.query(
            query_embeddings=embeddings,
            n_results=min(n_results, self.test_collection.count())
        )
        items = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                items.append({
                    "document": doc,
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if results.get("distances") else 0
                })
        return items

    def query_similar_bugs(self, story_text: str, n_results: int = 5) -> List[Dict]:
        """Find historically relevant bug reports."""
        if self.bug_collection.count() == 0:
            return []
        embeddings = embed_texts([story_text])
        results = self.bug_collection.query(
            query_embeddings=embeddings,
            n_results=min(n_results, self.bug_collection.count())
        )
        items = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                items.append({
                    "document": doc,
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if results.get("distances") else 0
                })
        return items

    def get_baseline_for_test(self, story_id: str, test_name: str) -> Optional[Dict]:
        """Get baseline pass rate for regression comparison."""
        query_text = f"Baseline for story {story_id} test {test_name}"
        if self.run_collection.count() == 0:
            return None
        embeddings = embed_texts([query_text])
        results = self.run_collection.query(
            query_embeddings=embeddings,
            n_results=1
        )
        if results["metadatas"] and results["metadatas"][0]:
            meta = results["metadatas"][0][0]
            if meta.get("story_id") == story_id:
                return meta
        return None

    def get_collection_stats(self) -> Dict:
        return {
            "test_cases": self.test_collection.count(),
            "bug_reports": self.bug_collection.count(),
            "run_baselines": self.run_collection.count()
        }

    def update_test_feedback(self, test_name: str, is_false_positive: bool):
        """Agentic feedback loop: mark test result as false positive."""
        # Query and update metadata to reflect human feedback
        results = self.test_collection.query(
            query_embeddings=embed_texts([test_name]),
            n_results=3
        )
        if results["ids"] and results["ids"][0]:
            for doc_id in results["ids"][0]:
                # ChromaDB doesn't support direct update of metadata,
                # so we add a new entry with the feedback flag
                self.test_collection.upsert(
                    ids=[doc_id + "_feedback"],
                    embeddings=embed_texts([f"FEEDBACK: {test_name} marked as false_positive={is_false_positive}"]),
                    documents=[f"Human feedback: {test_name} is_false_positive={is_false_positive}"],
                    metadatas=[{"test_name": test_name, "false_positive": str(is_false_positive), "type": "feedback"}]
                )


# Global RAG instance
_rag_pipeline: Optional[RAGPipeline] = None


def get_rag_pipeline() -> RAGPipeline:
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline
