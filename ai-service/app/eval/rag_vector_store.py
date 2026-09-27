import math
import re
from typing import List, Dict, Any, Optional

class VectorDocumentChunk:
    def __init__(self, chunk_id: str, document_id: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.content = content
        self.metadata = metadata or {}

class RAGVectorStore:
    def __init__(self, collection_name: str = "sentinelai_eval_knowledge_base"):
        self.collection_name = collection_name
        self.chunks: Dict[str, VectorDocumentChunk] = {}
        self._chroma_collection = None
        self._init_store()

    def _init_store(self):
        """Initializes ChromaDB collection if available, or uses in-memory vector store."""
        try:
            import chromadb
            client = chromadb.Client()
            self._chroma_collection = client.get_or_create_collection(name=self.collection_name)
        except Exception:
            self._chroma_collection = None

    def ingest_document(self, document_id: str, text: str, metadata: Optional[Dict[str, Any]] = None, chunk_size: int = 300) -> List[str]:
        """Chunks and stores a document in the vector store."""
        words = text.split()
        chunk_ids = []
        
        for i in range(0, max(len(words), 1), chunk_size):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            chunk_id = f"{document_id}_chunk_{i // chunk_size}"
            
            chunk_obj = VectorDocumentChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                content=chunk_text,
                metadata=metadata or {}
            )
            self.chunks[chunk_id] = chunk_obj
            chunk_ids.append(chunk_id)

            if self._chroma_collection:
                try:
                    self._chroma_collection.upsert(
                        ids=[chunk_id],
                        documents=[chunk_text],
                        metadatas=[metadata or {"document_id": document_id}]
                    )
                except Exception:
                    pass

        return chunk_ids

    def _compute_similarity(self, query: str, document_text: str) -> float:
        """Computes lexical cosine/Jaccard similarity between query and document."""
        query_words = set(re.findall(r"\w+", query.lower())) - {"the", "a", "an", "is", "in", "to", "for", "and", "or"}
        doc_words = set(re.findall(r"\w+", document_text.lower()))
        
        if not query_words or not doc_words:
            return 0.0
            
        intersection = query_words.intersection(doc_words)
        return len(intersection) / math.sqrt(len(query_words) * len(doc_words))

    def query(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Queries the vector store for top_k relevant chunks with similarity scores."""
        if not self.chunks:
            return []

        # If ChromaDB is active
        if self._chroma_collection:
            try:
                results = self._chroma_collection.query(
                    query_texts=[query_text],
                    n_results=min(top_k, len(self.chunks))
                )
                if results and results.get("documents") and len(results["documents"][0]) > 0:
                    retrieved = []
                    docs = results["documents"][0]
                    ids = results["ids"][0]
                    distances = results.get("distances", [[0.0] * len(docs)])[0]
                    for d_id, doc, dist in zip(ids, docs, distances):
                        sim_score = max(0.0, 1.0 - float(dist)) if dist else 0.88
                        retrieved.append({
                            "chunk_id": d_id,
                            "content": doc,
                            "similarity_score": round(sim_score, 4),
                            "metadata": self.chunks.get(d_id, VectorDocumentChunk("", "", "")).metadata
                        })
                    return retrieved
            except Exception:
                pass

        # Fallback to in-memory cosine similarity ranking
        scored = []
        for c_id, chunk in self.chunks.items():
            sim = self._compute_similarity(query_text, chunk.content)
            scored.append({
                "chunk_id": c_id,
                "content": chunk.content,
                "similarity_score": round(sim, 4),
                "metadata": chunk.metadata
            })

        scored.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored[:top_k]

# Default initialized knowledge store with sample benchmark documents
default_vector_store = RAGVectorStore()
default_vector_store.ingest_document(
    document_id="doc_return_policy",
    text="Customers may return undamaged products within 30 days of delivery for a 100% full refund to the original payment method. International orders require RMA approval.",
    metadata={"title": "Return and Refund Policy", "department": "Customer Care"}
)
default_vector_store.ingest_document(
    document_id="doc_security_guidelines",
    text="SentinelAI enforces multi-layer defense including input validation, strict RBAC permissions, and automated evaluation metrics (Faithfulness, Relevancy, Hallucination).",
    metadata={"title": "Security Architecture Guidelines", "department": "Engineering"}
)
