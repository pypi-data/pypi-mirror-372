"""
Stream processing module for strataregula.
Handles chunked data processing, real-time streaming, and memory-efficient large file processing.
"""

from .chunker import ChunkConfig, Chunker
from .processor import ChunkProcessor, StreamProcessor

__all__ = ["ChunkConfig", "ChunkProcessor", "Chunker", "StreamProcessor"]
__version__ = "0.0.1"
