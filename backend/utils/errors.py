"""
Custom exception classes for AI Codebase Mentor backend error handling.
"""

class CodebaseMentorError(Exception):
    """Base exception for all AI Codebase Mentor backend errors."""
    pass


class LLMQuotaExhaustedError(CodebaseMentorError):
    """Raised when Gemini LLM returns a 429 RESOURCE_EXHAUSTED error."""
    pass


class RepositoryError(CodebaseMentorError):
    """Base exception for repository operations."""
    pass


class RepositoryNotFoundError(RepositoryError):
    """Raised when a repository path or URL cannot be found or accessed."""
    pass


class InvalidFileRangeError(CodebaseMentorError):
    """Raised when invalid line numbers or file ranges are requested."""
    pass


class IndexingError(CodebaseMentorError):
    """Raised when repository indexing fails."""
    pass


class ChromaDBError(CodebaseMentorError):
    """Raised when ChromaDB operations fail."""
    pass
