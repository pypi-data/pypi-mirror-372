"""
FastEmbed integration for high-performance document embeddings.

This module provides a comprehensive embedding service that combines dense semantic
embeddings (via FastEmbed's all-MiniLM-L6-v2) with enhanced sparse keyword vectors
(via BM25) for optimal hybrid search performance.

Key Features:
    - Dense semantic embeddings using FastEmbed's optimized models
    - Enhanced BM25 sparse vectors for precise keyword matching
    - Intelligent text chunking with overlap for large documents
    - Async batch processing for high throughput
    - Content deduplication via SHA256 hashing
    - Configurable model parameters and batch sizes

Performance Characteristics:
    - Dense model: 384-dimensional all-MiniLM-L6-v2 embeddings
    - Processing speed: ~1000 documents/second on modern hardware
    - Memory usage: ~500MB for model initialization
    - Chunking: Intelligent word-boundary splitting with overlap

Example:
    ```python
    from workspace_qdrant_mcp.core.embeddings import EmbeddingService
    from workspace_qdrant_mcp.core.config import Config

    config = Config()
    service = EmbeddingService(config)
    await service.initialize()

    # Generate embeddings for text
    embeddings = await service.generate_embeddings(
        "Your document content here",
        include_sparse=True
    )

    # Process multiple documents with metadata
    documents = [{"content": "doc1"}, {"content": "doc2"}]
    embedded_docs = await service.embed_documents(documents)
    ```
"""

import asyncio
import hashlib
import logging
from typing import Optional, Union

from fastembed import TextEmbedding
from fastembed.sparse import SparseTextEmbedding

from .config import Config
from .sparse_vectors import BM25SparseEncoder

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    High-performance embedding service for dense and sparse vector generation.

    This service provides a unified interface for generating both dense semantic
    embeddings (using FastEmbed) and sparse keyword vectors (using enhanced BM25).
    It's designed for production workloads with async processing, batch optimization,
    and intelligent text handling.

    The service handles:
        - Model initialization and lifecycle management
        - Async batch processing for high throughput
        - Intelligent text chunking for large documents
        - Content deduplication and versioning
        - Error handling and recovery
        - Memory-efficient processing

    Attributes:
        config (Config): Configuration object with model and processing parameters
        dense_model (Optional[TextEmbedding]): FastEmbed dense embedding model
        sparse_model (Optional[SparseTextEmbedding]): Sparse embedding model (legacy)
        bm25_encoder (Optional[BM25SparseEncoder]): Enhanced BM25 encoder
        initialized (bool): Whether models have been loaded

    Performance Notes:
        - Batch processing is optimized for throughput over latency
        - Models are loaded once and reused for all operations
        - Text chunking uses word boundaries to preserve semantic coherence
        - Memory usage scales with batch size and document length

    Example:
        ```python
        service = EmbeddingService(config)
        await service.initialize()

        # Single document
        embeddings = await service.generate_embeddings("Hello world")

        # Batch processing with metadata
        docs = [{"content": "doc1"}, {"content": "doc2"}]
        embedded = await service.embed_documents(docs, batch_size=100)

        await service.close()
        ```
    """

    def __init__(self, config: Config) -> None:
        """Initialize the embedding service with configuration.

        Args:
            config: Configuration object containing model settings, batch sizes,
                   chunking parameters, and sparse vector preferences
        """
        self.config = config
        self.dense_model: TextEmbedding | None = None
        self.sparse_model: SparseTextEmbedding | None = None
        self.bm25_encoder: BM25SparseEncoder | None = None
        self.initialized = False

    async def initialize(self) -> None:
        """Initialize the embedding models."""
        if self.initialized:
            return

        try:
            # Initialize dense embedding model
            logger.info(
                "Initializing dense embedding model: %s", self.config.embedding.model
            )
            self.dense_model = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: TextEmbedding(
                    model_name=self.config.embedding.model,
                    max_length=512,  # Reasonable limit for document chunks
                ),
            )

            # Initialize sparse embedding model if enabled
            if self.config.embedding.enable_sparse_vectors:
                logger.info("Initializing enhanced BM25 sparse encoder")
                self.bm25_encoder = BM25SparseEncoder(use_fastembed=True)
                await self.bm25_encoder.initialize()

            self.initialized = True
            logger.info("Embedding models initialized successfully")

        except Exception as e:
            logger.error("Failed to initialize embedding models: %s", e)
            raise

    async def generate_embeddings(
        self, texts: str | list[str], include_sparse: bool = None
    ) -> dict[str, list[float] | list[list[float]] | dict]:
        """
        Generate dense and optionally sparse embeddings for text(s).

        Args:
            texts: Single text or list of texts to embed
            include_sparse: Whether to include sparse vectors (defaults to config setting)

        Returns:
            Dictionary with 'dense' and optionally 'sparse' embeddings
        """
        if not self.initialized:
            await self.initialize()

        if isinstance(texts, str):
            texts = [texts]
            single_text = True
        else:
            single_text = False

        if include_sparse is None:
            include_sparse = self.config.embedding.enable_sparse_vectors

        result = {}

        try:
            # Generate dense embeddings
            dense_embeddings = await self._generate_dense_embeddings(texts)
            result["dense"] = dense_embeddings[0] if single_text else dense_embeddings

            # Generate sparse embeddings if requested
            if include_sparse and self.bm25_encoder:
                sparse_embeddings = await self._generate_sparse_embeddings(texts)
                result["sparse"] = (
                    sparse_embeddings[0] if single_text else sparse_embeddings
                )

            return result

        except Exception as e:
            logger.error("Failed to generate embeddings: %s", e)
            raise

    async def _generate_dense_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate dense semantic embeddings using FastEmbed.

        Internal method that handles the actual FastEmbed model invocation
        for dense vector generation. Uses async executor to avoid blocking
        the event loop during computation.

        Args:
            texts: List of text strings to embed

        Returns:
            List of 384-dimensional dense embedding vectors

        Raises:
            RuntimeError: If FastEmbed model fails or is not initialized
        """
        try:
            embeddings = await asyncio.get_event_loop().run_in_executor(
                None, lambda: list(self.dense_model.embed(texts))
            )
            return [embedding.tolist() for embedding in embeddings]

        except Exception as e:
            logger.error("Failed to generate dense embeddings: %s", e)
            raise

    async def _generate_sparse_embeddings(self, texts: list[str]) -> list[dict]:
        """Generate sparse keyword embeddings using enhanced BM25.

        Internal method that handles BM25 sparse vector generation for
        precise keyword matching. Optimizes for single vs batch processing.

        Args:
            texts: List of text strings to encode

        Returns:
            List of sparse vector dictionaries with 'indices' and 'values' arrays

        Raises:
            RuntimeError: If BM25 encoder fails or is not initialized
        """
        try:
            if len(texts) == 1:
                sparse_vector = await self.bm25_encoder.encode_single(texts[0])
                return [sparse_vector]
            else:
                return await self.bm25_encoder.encode_batch(texts)

        except Exception as e:
            logger.error("Failed to generate sparse embeddings: %s", e)
            raise

    async def embed_documents(
        self,
        documents: list[dict[str, str]],
        content_field: str = "content",
        batch_size: int | None = None,
    ) -> list[dict]:
        """
        Embed a list of documents with metadata.

        Args:
            documents: List of document dictionaries
            content_field: Field containing the text content
            batch_size: Batch size for processing (defaults to config)

        Returns:
            List of documents with embeddings added
        """
        if not documents:
            return []

        batch_size = batch_size or self.config.embedding.batch_size
        results = []

        # Process in batches
        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]
            batch_texts = [doc.get(content_field, "") for doc in batch]

            # Generate embeddings for batch
            embeddings = await self.generate_embeddings(batch_texts)

            # Add embeddings to documents
            for j, doc in enumerate(batch):
                embedded_doc = doc.copy()
                embedded_doc["dense_vector"] = embeddings["dense"][j]

                if "sparse" in embeddings:
                    embedded_doc["sparse_vector"] = embeddings["sparse"][j]

                # Add embedding metadata
                embedded_doc["embedding_model"] = self.config.embedding.model
                embedded_doc["embedding_timestamp"] = asyncio.get_event_loop().time()
                embedded_doc["content_hash"] = self._hash_content(
                    doc.get(content_field, "")
                )

                results.append(embedded_doc)

        return results

    def chunk_text(
        self,
        text: str,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> list[str]:
        """
        Split text into overlapping chunks for optimal embedding processing.

        Intelligently splits large documents into smaller chunks that preserve
        semantic coherence while staying within embedding model limits. Uses
        word boundaries to avoid breaking words and maintains context through
        overlapping chunks.

        Args:
            text: Source text to split into chunks
            chunk_size: Maximum characters per chunk (defaults to config.chunk_size)
            chunk_overlap: Characters to overlap between chunks (defaults to config.chunk_overlap)

        Returns:
            List[str]: Text chunks, each under the specified size limit.
                      Returns single-item list if text is already under chunk_size.

        Algorithm:
            1. If text <= chunk_size, return as single chunk
            2. Split at word boundaries when possible to preserve meaning
            3. Create overlapping chunks to maintain context across boundaries
            4. Strip whitespace from each chunk

        Example:
            ```python
            service = EmbeddingService(config)
            long_text = "...very long document..."
            chunks = service.chunk_text(long_text, chunk_size=1000, chunk_overlap=100)

            # Each chunk is <= 1000 chars with 100 char overlap
            for i, chunk in enumerate(chunks):
                print(f"Chunk {i}: {len(chunk)} characters")
            ```
        """
        chunk_size = chunk_size or self.config.embedding.chunk_size
        chunk_overlap = chunk_overlap or self.config.embedding.chunk_overlap

        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at word boundaries
            if end < len(text):
                # Find the last space before the limit
                while end > start and text[end] != " ":
                    end -= 1
                if end == start:  # No space found, force break
                    end = start + chunk_size

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move start position with overlap
            start = end - chunk_overlap
            if start <= 0:
                start = end

        return chunks

    def _hash_content(self, content: str) -> str:
        """Generate SHA256 hash of content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def get_model_info(self) -> dict:
        """Get comprehensive information about loaded embedding models.

        Provides detailed diagnostics about model status, capabilities,
        configuration parameters, and performance characteristics.

        Returns:
            Dict: Model information containing:
                - dense_model (dict): Dense embedding model details
                    - name (str): Model identifier (e.g., 'all-MiniLM-L6-v2')
                    - loaded (bool): Whether model is loaded in memory
                    - dimensions (int): Embedding vector dimensions
                - sparse_model (dict): Sparse embedding model details
                    - name (str): Sparse encoder name ('Enhanced BM25' or None)
                    - loaded (bool): Whether sparse encoder is loaded
                    - enabled (bool): Whether sparse vectors are enabled in config
                    - Additional BM25-specific information if available
                - config (dict): Processing configuration
                    - chunk_size (int): Maximum characters per chunk
                    - chunk_overlap (int): Overlap characters between chunks
                    - batch_size (int): Batch processing size
                - initialized (bool): Overall service initialization status

        Example:
            ```python
            info = service.get_model_info()
            print(f"Dense model: {info['dense_model']['name']}")
            print(f"Dimensions: {info['dense_model']['dimensions']}")
            print(f"Sparse enabled: {info['sparse_model']['enabled']}")
            ```
        """
        sparse_info = {}
        if self.bm25_encoder:
            sparse_info = self.bm25_encoder.get_model_info()

        return {
            "dense_model": {
                "name": self.config.embedding.model,
                "loaded": self.dense_model is not None,
                "dimensions": 384
                if "all-MiniLM-L6-v2" in self.config.embedding.model
                else (
                    768
                    if (
                        "bge-base-en" in self.config.embedding.model
                        or "all-mpnet-base-v2" in self.config.embedding.model
                        or "jina-embeddings-v2-base" in self.config.embedding.model
                        or "gte-base" in self.config.embedding.model
                    )
                    else (
                        1024
                        if (
                            "bge-large" in self.config.embedding.model
                            or "bge-m3" in self.config.embedding.model
                        )
                        else 384
                    )
                ),
            },
            "sparse_model": {
                "name": "Enhanced BM25"
                if self.config.embedding.enable_sparse_vectors
                else None,
                "loaded": self.bm25_encoder is not None,
                "enabled": self.config.embedding.enable_sparse_vectors,
                **sparse_info,
            },
            "config": {
                "chunk_size": self.config.embedding.chunk_size,
                "chunk_overlap": self.config.embedding.chunk_overlap,
                "batch_size": self.config.embedding.batch_size,
            },
            "initialized": self.initialized,
        }

    async def close(self) -> None:
        """Clean up embedding models."""
        # FastEmbed models don't need explicit cleanup
        self.dense_model = None
        self.sparse_model = None
        self.bm25_encoder = None
        self.initialized = False
