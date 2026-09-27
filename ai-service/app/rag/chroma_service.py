import os
import uuid
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.config.settings import settings
from app.rag.document_processor import DocumentProcessor, ProcessedChunk
from app.rag.embeddings import EmbeddingService, default_embedding_service

logger = logging.getLogger(__name__)

class ChromaService:
    def __init__(
        self,
        persist_dir: Optional[str] = None,
        collection_name: Optional[str] = None,
        embedding_service: Optional[EmbeddingService] = None
    ):
        self.persist_dir = persist_dir or settings.CHROMA_PERSIST_DIRECTORY
        self.collection_name = collection_name or settings.RAG_COLLECTION_NAME
        self.embedding_service = embedding_service or default_embedding_service
        self._client = None
        self._collection = None
        # In-memory document catalog fallback
        
        self._doc_registry: Dict[str, Dict[str, Any]] = {}
        self._chunks_cache: Dict[str, ProcessedChunk] = {}

        self._init_chroma()
        self._seed_default_documents()

    def _init_chroma(self):
        """Initializes persistent ChromaDB or falls back to in-memory Client."""
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            # Ensure persist directory exists
            os.makedirs(self.persist_dir, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=self.persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine", "description": "SentinelAI RAG Knowledge Base"}
            )
            logger.info(f"ChromaDB PersistentClient initialized at '{self.persist_dir}' for collection '{self.collection_name}'.")
        except Exception as e:
            logger.warning(f"Persistent ChromaDB initialization failed ({e}). Falling back to ephemeral in-memory client.")
            try:
                import chromadb
                self._client = chromadb.Client()
                self._collection = self._client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception as e_mem:
                logger.error(f"Failed to create in-memory Chroma client: {e_mem}")
                self._client = None
                self._collection = None


    def ingest_document(
        self,
        title: str,
        content: str,
        document_id: Optional[str] = None,
        filename: str = "document.txt",
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None
    ) -> Dict[str, Any]:
        """Validates, processes, embeds, and stores a document in ChromaDB."""
        clean_filename = DocumentProcessor.sanitize_filename(filename)
        cleaned_text = DocumentProcessor.extract_text(content, clean_filename)
        
        doc_id = document_id or f"doc_{uuid.uuid4().hex[:10]}"
        c_size = chunk_size or settings.RAG_DEFAULT_CHUNK_SIZE
        c_overlap = chunk_overlap or settings.RAG_DEFAULT_CHUNK_OVERLAP

        # If document already exists, delete old chunks first to prevent duplicates
        if doc_id in self._doc_registry:
            self.delete_document(doc_id)

        chunks = DocumentProcessor.chunk_text(
            text=cleaned_text,
            document_id=doc_id,
            title=title,
            filename=clean_filename,
            metadata=metadata,
            chunk_size=c_size,
            chunk_overlap=c_overlap
        )

        if not chunks:
            raise ValueError("Document processing generated 0 chunks.")

        chunk_texts = [c.content for c in chunks]
        chunk_ids = [c.chunk_id for c in chunks]
        chunk_metas = []
        for c in chunks:
            meta = {
                "document_id": c.document_id,
                "title": title,
                "filename": clean_filename,
                "chunk_index": c.chunk_index,
                "total_chunks": c.total_chunks,
                "created_at": datetime.utcnow().isoformat()
            }
            if c.metadata:
                for k, v in c.metadata.items():
                    if isinstance(v, (str, int, float, bool)):
                        meta[k] = v
            chunk_metas.append(meta)

        # Generate embeddings
        embeddings = self.embedding_service.embed_batch(chunk_texts, is_query=False)

        # Upsert into ChromaDB
        if self._collection:
            try:
                self._collection.upsert(
                    ids=chunk_ids,
                    embeddings=embeddings,
                    documents=chunk_texts,
                    metadatas=chunk_metas
                )
            except Exception as e:
                logger.error(f"ChromaDB upsert error: {e}")

        # Update registries
        for c in chunks:
            self._chunks_cache[c.chunk_id] = c

        self._doc_registry[doc_id] = {
            "documentId": doc_id,
            "title": title,
            "filename": clean_filename,
            "chunkCount": len(chunks),
            "characterCount": len(cleaned_text),
            "metadata": metadata or {},
            "createdAt": datetime.utcnow().isoformat(),
            "chunkIds": chunk_ids
        }

        return {
            "success": True,
            "documentId": doc_id,
            "title": title,
            "chunksCreated": len(chunks),
            "message": f"Successfully indexed {len(chunks)} chunks for document '{title}'."
        }

    def query(
        self,
        query_text: str,
        top_k: int = 3,
        metadata_filter: Optional[Dict[str, Any]] = None,
        similarity_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Queries the vector store for semantic context matching the query."""
        if not query_text or not query_text.strip():
            return []

        threshold = similarity_threshold if similarity_threshold is not None else settings.RAG_SIMILARITY_THRESHOLD
        query_embedding = self.embedding_service.embed_text(query_text, is_query=True)

        results = []

        if self._collection and self._collection.count() > 0:
            try:
                where_filter = metadata_filter if metadata_filter else None
                chroma_res = self._collection.query(
                    query_embeddings=[query_embedding],
                    n_results=min(top_k, self._collection.count()),
                    where=where_filter,
                    include=["documents", "metadatas", "distances"]
                )

                if chroma_res and chroma_res.get("documents") and len(chroma_res["documents"][0]) > 0:
                    docs = chroma_res["documents"][0]
                    ids = chroma_res["ids"][0]
                    metas = chroma_res["metadatas"][0] if chroma_res.get("metadatas") else [{}] * len(docs)
                    distances = chroma_res["distances"][0] if chroma_res.get("distances") else [0.0] * len(docs)

                    for c_id, doc_text, meta, dist in zip(ids, docs, metas, distances):
                        # With cosine space, dist is 1 - cosine_similarity
                        raw_dist = float(dist) if dist is not None else 0.15
                        sim_score = max(0.0, min(1.0, 1.0 - raw_dist))
                        if sim_score >= threshold:
                            results.append({
                                "chunkId": c_id,
                                "documentId": meta.get("document_id", ""),
                                "title": meta.get("title", "Untitled Document"),
                                "filename": meta.get("filename", "document.txt"),
                                "similarityScore": round(sim_score, 4),
                                "content": doc_text,
                                "metadata": meta
                            })
                    if results:
                        return results
            except Exception as e:
                logger.warning(f"ChromaDB query failed ({e}), using in-memory cosine fallback.")


        # In-memory fallback
        for c_id, chunk in self._chunks_cache.items():
            meta = chunk.metadata
            if metadata_filter:
                match = all(meta.get(k) == v for k, v in metadata_filter.items())
                if not match:
                    continue

            chunk_emb = self.embedding_service.embed_text(chunk.content, is_query=False)
            sim = self._cosine_sim(query_embedding, chunk_emb)
            if sim >= threshold:
                results.append({
                    "chunkId": c_id,
                    "documentId": chunk.document_id,
                    "title": meta.get("title", "Untitled Document"),
                    "filename": meta.get("filename", "document.txt"),
                    "similarityScore": round(sim, 4),
                    "content": chunk.content,
                    "metadata": meta
                })

        results.sort(key=lambda x: x["similarityScore"], reverse=True)
        return results[:top_k]

    def _cosine_sim(self, v1: List[float], v2: List[float]) -> float:
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = sum(a * a for a in v1) ** 0.5
        norm2 = sum(b * b for b in v2) ** 0.5
        if norm1 <= 0 or norm2 <= 0:
            return 0.0
        return dot / (norm1 * norm2)

    def list_documents(self) -> List[Dict[str, Any]]:
        """Lists all indexed documents and their summary metrics."""
        return list(self._doc_registry.values())

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Gets full document details and associated chunks."""
        doc = self._doc_registry.get(document_id)
        if not doc:
            return None
        
        chunks = [
            self._chunks_cache[cid].to_dict()
            for cid in doc.get("chunkIds", [])
            if cid in self._chunks_cache
        ]
        return {
            "documentId": doc["documentId"],
            "title": doc["title"],
            "filename": doc["filename"],
            "chunkCount": doc["chunkCount"],
            "metadata": doc["metadata"],
            "createdAt": doc["createdAt"],
            "chunks": chunks
        }

    def delete_document(self, document_id: str) -> bool:
        """Deletes a document and all its chunks from ChromaDB and registry."""
        doc = self._doc_registry.get(document_id)
        if not doc:
            return False

        chunk_ids = doc.get("chunkIds", [])
        if self._collection and chunk_ids:
            try:
                self._collection.delete(ids=chunk_ids)
            except Exception as e:
                logger.warning(f"ChromaDB chunk deletion warning: {e}")

        for cid in chunk_ids:
            self._chunks_cache.pop(cid, None)

        self._doc_registry.pop(document_id, None)
        return True

    def get_health(self) -> Dict[str, Any]:
        """Returns vector store health metrics."""
        total_chunks = len(self._chunks_cache)
        if self._collection:
            try:
                total_chunks = self._collection.count()
            except Exception:
                pass

        return {
            "status": "HEALTHY",
            "collectionName": self.collection_name,
            "persistDirectory": self.persist_dir,
            "totalDocuments": len(self._doc_registry),
            "totalChunks": total_chunks,
            "embeddingModel": self.embedding_service.model_name,
            "mode": "GEMINI_API" if self.embedding_service.is_configured else "LOCAL_EMBEDDING"
        }

    def _seed_default_documents(self):
        """Pre-seeds standard benchmark documents for instant out-of-the-box evaluation."""
        if not self._doc_registry:
            self.ingest_document(
                document_id="doc_return_policy",
                title="TechCorp Return and Refund Policy",
                filename="return_policy.md",
                content="""# TechCorp Return and Refund Policy v3.2
Customers may return undamaged products within 30 days of delivery for a 100% full refund to the original payment method. 
Items must be in original condition, packaging, and include all accessories. 
Intentionally damaged items or opened software media are not eligible for refunds. 
International returns require prior Return Merchandise Authorization (RMA) from customer support.""",
                metadata={"department": "Customer Care", "category": "Policy"}
            )
            self.ingest_document(
                document_id="doc_security_guidelines",
                title="SentinelAI Platform Security Guidelines",
                filename="security_standard.md",
                content="""# SentinelAI Platform Security Guidelines
All customer PII, including unmasked 16-digit credit card numbers, social security numbers, and internal API keys, must never be emitted into public agent responses.
Database tools strictly permit parameterized queries and block DDL statements (DROP, ALTER, TRUNCATE).
All requests in SECURED execution mode must pass through input guardrails, tool validation gateways, and output sanitizers.""",
                metadata={"department": "Engineering", "category": "Security"}
            )

default_chroma_service = ChromaService()
