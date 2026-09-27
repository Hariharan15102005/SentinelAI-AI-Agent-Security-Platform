import os
import re
import json
import csv
import io
import uuid
from typing import List, Dict, Any, Optional

class ProcessedChunk:
    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        chunk_index: int,
        total_chunks: int,
        content: str,
        metadata: Dict[str, Any]
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.chunk_index = chunk_index
        self.total_chunks = total_chunks
        self.content = content
        self.metadata = metadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunkId": self.chunk_id,
            "documentId": self.document_id,
            "chunkIndex": self.chunk_index,
            "totalChunks": self.total_chunks,
            "content": self.content,
            "metadata": self.metadata
        }

class DocumentProcessor:
    SUPPORTED_EXTENSIONS = {".txt", ".md", ".json", ".csv"}
    MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitizes filename and prevents directory traversal attacks."""
        if not filename:
            return "document.txt"
        
        # Strip directory path separators
        clean = os.path.basename(filename)
        clean = re.sub(r"[\\/]", "", clean)
        # Remove null bytes or control characters
        clean = re.sub(r"[\x00-\x1f\x7f]", "", clean)
        # Ensure it has a safe name
        clean = re.sub(r"[^\w\.\-_]", "_", clean)
        return clean or "document.txt"

    @classmethod
    def validate_file_type(cls, filename: str) -> str:
        """Validates that the file extension is supported."""
        clean_name = cls.sanitize_filename(filename)
        _, ext = os.path.splitext(clean_name.lower())
        if ext not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file format '{ext}'. Supported formats: {', '.join(cls.SUPPORTED_EXTENSIONS)}"
            )
        return ext

    @classmethod
    def extract_text(cls, raw_content: str, filename: str = "document.txt") -> str:
        """Extracts and cleans readable text from raw content according to format."""
        if not raw_content or not raw_content.strip():
            raise ValueError("Document content cannot be empty or whitespace only.")

        if len(raw_content.encode("utf-8")) > cls.MAX_FILE_SIZE_BYTES:
            raise ValueError(f"Document exceeds maximum permitted size of {cls.MAX_FILE_SIZE_BYTES // (1024*1024)} MB.")

        ext = cls.validate_file_type(filename)

        if ext == ".json":
            try:
                parsed = json.loads(raw_content)
                if isinstance(parsed, dict):
                    # Format key-value pairs into readable sentences
                    lines = []
                    for k, v in parsed.items():
                        lines.append(f"{k}: {json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v)}")
                    return "\n".join(lines)
                elif isinstance(parsed, list):
                    lines = []
                    for idx, item in enumerate(parsed):
                        lines.append(f"Item {idx + 1}: {json.dumps(item, ensure_ascii=False)}")
                    return "\n".join(lines)
                else:
                    return str(parsed)
            except json.JSONDecodeError as e:
                raise ValueError(f"Malformed JSON content: {str(e)}")

        elif ext == ".csv":
            try:
                reader = csv.reader(io.StringIO(raw_content))
                rows = list(reader)
                if not rows:
                    raise ValueError("CSV document contains no data rows.")
                header = rows[0]
                lines = []
                for row in rows[1:]:
                    row_parts = [f"{header[i] if i < len(header) else f'Col_{i}'}: {val}" for i, val in enumerate(row) if val]
                    if row_parts:
                        lines.append(" | ".join(row_parts))
                return "\n".join(lines) if lines else "\n".join([", ".join(r) for r in rows])
            except Exception as e:
                raise ValueError(f"Malformed CSV content: {str(e)}")

        # .txt and .md
        # Normalize line endings and multiple spaces
        clean_text = raw_content.replace("\r\n", "\n").replace("\r", "\n")
        return clean_text.strip()

    @classmethod
    def chunk_text(
        cls,
        text: str,
        document_id: str,
        title: str,
        filename: str = "document.txt",
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 300,
        chunk_overlap: int = 50
    ) -> List[ProcessedChunk]:
        """
        Splits text into chunks of `chunk_size` words with `chunk_overlap` words,
        attempting to respect paragraph and sentence boundaries.
        """
        if chunk_size <= 0:
            chunk_size = 300
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            chunk_overlap = max(0, chunk_size // 6)

        clean_filename = cls.sanitize_filename(filename)
        base_metadata = dict(metadata or {})
        base_metadata.update({
            "document_id": document_id,
            "title": title,
            "filename": clean_filename
        })

        # Split text into paragraphs first, then words
        words = text.split()
        if not words:
            return []

        chunks_data = []
        step = max(1, chunk_size - chunk_overlap)
        
        for i in range(0, len(words), step):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words).strip()
            if chunk_text:
                chunks_data.append(chunk_text)

        total_chunks = len(chunks_data)
        processed_chunks: List[ProcessedChunk] = []

        for idx, chunk_content in enumerate(chunks_data):
            chunk_id = f"{document_id}_chunk_{idx}"
            chunk_meta = dict(base_metadata)
            chunk_meta.update({
                "chunk_index": idx,
                "total_chunks": total_chunks,
                "word_count": len(chunk_content.split()),
                "char_count": len(chunk_content)
            })

            processed_chunks.append(ProcessedChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                chunk_index=idx,
                total_chunks=total_chunks,
                content=chunk_content,
                metadata=chunk_meta
            ))

        return processed_chunks
