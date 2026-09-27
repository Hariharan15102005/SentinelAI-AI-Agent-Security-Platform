import os
import re
import math
import hashlib
import logging
from typing import List, Optional
from app.config.settings import settings


logger = logging.getLogger(__name__)

class EmbeddingService:
    EMBEDDING_DIM = 768

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.RAG_EMBEDDING_MODEL
        self.is_configured = False

        if self.api_key and self.api_key != "your_gemini_api_key_here":
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.is_configured = True
                logger.info(f"Gemini Embedding API configured with model '{self.model_name}'.")
            except Exception as e:
                logger.warning(f"Failed to configure Gemini Embedding API: {e}. Using deterministic local embeddings.")
                self.is_configured = False
        else:
            logger.info("Operating in Local / Mock Embedding Mode.")

    def embed_text(self, text: str, is_query: bool = False) -> List[float]:
        """Generates a normalized 768-dimensional embedding vector for input text."""
        if not text:
            return [0.0] * self.EMBEDDING_DIM

        if self.is_configured and not settings.MOCK_LLM_MODE:
            try:
                import google.generativeai as genai
                task_type = "retrieval_query" if is_query else "retrieval_document"
                result = genai.embed_content(
                    model=self.model_name,
                    content=text,
                    task_type=task_type
                )
                if "embedding" in result and result["embedding"]:
                    vec = result["embedding"]
                    # Ensure standard dimension
                    if len(vec) == self.EMBEDDING_DIM:
                        return vec
                    elif len(vec) > self.EMBEDDING_DIM:
                        return vec[:self.EMBEDDING_DIM]
                    else:
                        return vec + [0.0] * (self.EMBEDDING_DIM - len(vec))
            except Exception as e:
                logger.warning(f"Gemini embedding call failed: {e}. Falling back to deterministic local embedding.")

        return self._generate_local_embedding(text)

    def embed_batch(self, texts: List[str], is_query: bool = False) -> List[List[float]]:
        """Generates embeddings for a batch of texts."""
        if not texts:
            return []
        
        if self.is_configured and not settings.MOCK_LLM_MODE:
            try:
                import google.generativeai as genai
                task_type = "retrieval_query" if is_query else "retrieval_document"
                result = genai.embed_content(
                    model=self.model_name,
                    content=texts,
                    task_type=task_type
                )
                if "embedding" in result and result["embedding"]:
                    embeddings = result["embedding"]
                    if isinstance(embeddings[0], list):
                        return embeddings
                    return [embeddings]
            except Exception as e:
                logger.warning(f"Gemini batch embedding call failed: {e}. Falling back to local embeddings.")

        return [self._generate_local_embedding(t) for t in texts]

    def _generate_local_embedding(self, text: str) -> List[float]:
        """
        Deterministic, dense 768-dimensional vector generator based on word frequency
        and cryptographic token hash projection with L2 normalization.
        """
        vec = [0.0] * self.EMBEDDING_DIM
        clean_text = text.lower()
        stopwords = {"what", "is", "the", "for", "and", "a", "an", "in", "to", "of", "on", "with", "at", "by", "from", "as", "about"}
        
        # Extract alphanumeric tokens
        raw_words = re.findall(r"\b[a-z0-9]+\b", clean_text)
        words = [w for w in raw_words if w not in stopwords]
        if not words:
            words = raw_words or ["empty"]

        for word in words:
            # Simple stemming: strip trailing 's', 'ing', 'ed' if length > 4
            stem = word
            if len(stem) > 4 and stem.endswith("ing"):
                stem = stem[:-3]
            elif len(stem) > 3 and stem.endswith("ed"):
                stem = stem[:-2]
            elif len(stem) > 3 and stem.endswith("s"):
                stem = stem[:-1]

            # Primary hash projection
            h = int(hashlib.sha256(stem.encode("utf-8")).hexdigest(), 16)
            idx1 = h % self.EMBEDDING_DIM
            idx2 = (h >> 16) % self.EMBEDDING_DIM
            idx3 = (h >> 32) % self.EMBEDDING_DIM
            
            vec[idx1] += 2.0
            vec[idx2] += 1.0
            vec[idx3] += 0.5

        # L2 Normalization
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]

        return vec


default_embedding_service = EmbeddingService()
