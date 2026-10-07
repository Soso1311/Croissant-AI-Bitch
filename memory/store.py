import os
from typing import List, Dict, Any
import chromadb
import config

class MemoryStore:
    """Vector memory database for long-term task context and user preferences."""

    def __init__(self):
        db_path = os.path.join(config.PROJECT_ROOT, "jarvis_memory_db")
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            name="jarvis_persistent_memory",
            metadata={"hnsw:space": "cosine"}
        )

    def save(self, content: str, metadata: Dict[str, Any] = None) -> None:
        doc_id = f"mem_{self.collection.count() + 1}"
        self.collection.add(
            documents=[content],
            metadatas=[metadata or {"type": "session_result"}],
            ids=[doc_id]
        )

    def recall(self, query: str, n_results: int = 3) -> List[str]:
        if self.collection.count() == 0:
            return []
        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, self.collection.count())
        )
        return results["documents"][0] if results and "documents" in results else []
