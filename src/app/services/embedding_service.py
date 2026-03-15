"""
EmbeddingService — generates vector embeddings via a local Ollama model.

Uses the same model (nomic-embed-text) already in use in the project's
Moodle RAG chatbot, keeping the dependency consistent.

Architecture rule:
    Agents and other services must NOT call the Ollama embedding API directly.
    All embedding generation goes through EmbeddingService.

If Ollama is unavailable, calls raise EmbeddingError with a clear message.
"""

from __future__ import annotations

import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

_DEFAULT_MODEL = "nomic-embed-text"
_DEFAULT_BASE_URL = "http://localhost:11434"


class EmbeddingError(RuntimeError):
    """Raised when the embedding API call fails."""


class EmbeddingService:
    """
    Generates text embeddings using a locally-running Ollama model.

    Usage:
        svc = EmbeddingService()
        vector = svc.embed("photosynthesis is the process...")
        matrix = svc.embed_batch(["text A", "text B"])
    """

    def __init__(
        self,
        model: str = _DEFAULT_MODEL,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: int = 30,
    ) -> None:
        """
        Args:
            model:    Ollama model name that supports embeddings.
            base_url: Ollama server URL (default http://localhost:11434).
            timeout:  HTTP request timeout in seconds.
        """
        self.model = model
        self._url = f"{base_url.rstrip('/')}/api/embeddings"
        self._timeout = timeout

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def embed(self, text: str) -> list[float]:
        """
        Generate an embedding vector for a single text string.

        Args:
            text: The text to embed.

        Returns:
            List of floats representing the embedding vector.

        Raises:
            EmbeddingError: If the Ollama API call fails.
        """
        return self._call(text)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embedding vectors for a list of texts.

        Ollama's embeddings API is single-input only, so this method
        calls embed() for each text sequentially.

        Args:
            texts: List of strings to embed.

        Returns:
            List of embedding vectors in the same order as inputs.

        Raises:
            EmbeddingError: If any individual embedding call fails.
        """
        return [self._call(text) for text in texts]

    def is_available(self) -> bool:
        """
        Check whether the Ollama embedding service is reachable.

        Returns:
            True if reachable, False otherwise.
        """
        try:
            resp = requests.get(
                self._url.replace("/api/embeddings", "/"),
                timeout=5,
            )
            return resp.status_code < 500
        except requests.RequestException:
            return False

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _call(self, text: str) -> list[float]:
        try:
            resp = requests.post(
                self._url,
                json={"model": self.model, "prompt": text},
                timeout=self._timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            embedding = data.get("embedding")
            if not isinstance(embedding, list):
                raise EmbeddingError(
                    f"Unexpected embedding API response: {data}"
                )
            return embedding
        except requests.RequestException as exc:
            raise EmbeddingError(
                f"Embedding API call failed ({self._url}): {exc}"
            ) from exc
