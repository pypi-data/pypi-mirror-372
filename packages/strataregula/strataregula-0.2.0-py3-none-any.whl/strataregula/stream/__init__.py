"""
Stream processing module for strataregula.
Handles chunked data processing, real-time streaming, and memory-efficient large file processing.
"""

from .processor import StreamProcessor, ChunkProcessor
from .chunker import Chunker, ChunkConfig

__all__ = ["StreamProcessor", "ChunkProcessor", "Chunker", "ChunkConfig"]
__version__ = "0.0.1"