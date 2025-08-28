from langchain_core.documents.base import BaseMedia, Document
from typing import Any, Literal, Self

from langchain_core.load.serializable import Serializable
import yaml

class ScoredDocument(Document):
    score: float

    def __init__(self, page_content: str, score: float, **kwargs: Any) -> None:
        """Pass page_content in as positional or named arg."""
        super().__init__(page_content=page_content, score=score, **kwargs)  # type: ignore[call-arg]

    @classmethod
    def from_doc(cls, doc: Document, score: float) -> Self: # pyright: ignore[reportIncompatibleMethodOverride]
        return cls(
            score=score,
            id=doc.id,
            page_content=doc.page_content,
            metadata=doc.metadata,
        )

    def __str__(self) -> str:
        """Override __str__ to restrict it to page_content, score, and metadata."""
        # The format matches pydantic format for __str__.
        if self.metadata:
            return f"score={self.score} page_content='{self.page_content}' metadata={self.metadata}"
        return f"score={self.score} page_content='{self.page_content}'"

class DocumentReference(BaseMedia):
    type: Literal["DocumentReference"] = "DocumentReference"

    def __init__(self, id: str, **kwargs: Any) -> None:
        """Pass id in as positional or named arg."""
        super().__init__(id=id, **kwargs)  # type: ignore[call-arg]

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Return whether this class is serializable."""
        return True

    def __str__(self) -> str:
        """Override __str__ to restrict it to document_id and metadata."""
        # The format matches pydantic format for __str__.
        if self.metadata:
            return f"document_id='{self.id}' metadata={self.metadata}"
        return f"document_id='{self.id}'"


class DocumentChunk(BaseMedia):
    chunk_content: str
    """String text."""

    type: str = "DocumentChunk"

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Return whether this class is serializable."""
        return True

    def __str__(self) -> str:
        """Override __str__ to restrict it to chunk_content and metadata."""
        # The format matches pydantic format for __str__.
        if self.metadata:
            return f"chunk_content='{self.chunk_content}'  metadata={self.metadata}"
        return f"chunk_content='{self.chunk_content}'"

class ScoredDocumentChunk(DocumentChunk):
    score: float

    type: str = "ScoredDocumentChunk"

    def __str__(self) -> str:
        """Override __str__ to restrict it to chunk_content and metadata."""
        # The format matches pydantic format for __str__.
        if self.metadata:
            return f"score={self.score} chunk_content='{self.chunk_content}' metadata={self.metadata}"
        return f"score={self.score} chunk_content='{self.chunk_content}'"


class DocumentChunks(BaseMedia):
    chunks: list[DocumentChunk]

    type: str = "DocumentChunks" # pyright: ignore[reportIncompatibleVariableOverride]

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Return whether this class is serializable."""
        return True

    def __str__(self) -> str:
        """Override __str__ to restrict it to chunk_content and metadata."""
        # The format matches pydantic format for __str__.
        chunks_str = [chunk.__str__() for chunk in self.chunks]

        if self.metadata:
            return f"chunks={chunks_str} metadata={self.metadata}"
        return f"chunks={chunks_str}"


class ScoredDocumentChunks(DocumentChunks):
    chunks: list[ScoredDocumentChunk] # pyright: ignore[reportIncompatibleVariableOverride]

    type: str = "ScoredDocumentChunks"

    @property
    def total_score(self) -> float:
        return sum(chunk.score for chunk in self.chunks)
    
__all__ = [
    "ScoredDocument",
    "DocumentReference",
    "DocumentChunk",
    "ScoredDocumentChunk",
    "DocumentChunks",
    "ScoredDocumentChunks",
]
