"""
Chunker module for dividing large data streams into manageable chunks.
Provides memory-efficient processing of large files and real-time data streams.
"""

from typing import Iterator, Optional, Union, BinaryIO, TextIO, Any
from dataclasses import dataclass
import io
from pathlib import Path


@dataclass
class ChunkConfig:
    """Configuration for chunk processing."""
    chunk_size: int = 8192  # Default 8KB chunks
    overlap_size: int = 0  # Overlap between chunks for context preservation
    encoding: Optional[str] = None  # Text encoding, None for binary
    line_based: bool = False  # Split on line boundaries for text processing
    preserve_boundaries: bool = True  # Don't split in middle of boundaries


class Chunker:
    """Handles chunking of data streams with various strategies."""
    
    def __init__(self, config: Optional[ChunkConfig] = None):
        self.config = config or ChunkConfig()
    
    def chunk_bytes(self, data: Union[bytes, BinaryIO], chunk_size: Optional[int] = None) -> Iterator[bytes]:
        """Chunk binary data into fixed-size pieces."""
        size = chunk_size or self.config.chunk_size
        
        if isinstance(data, bytes):
            # Chunk from bytes object
            for i in range(0, len(data), size):
                yield data[i:i + size]
        else:
            # Chunk from file-like object
            while True:
                chunk = data.read(size)
                if not chunk:
                    break
                yield chunk
    
    def chunk_text(self, data: Union[str, TextIO], chunk_size: Optional[int] = None) -> Iterator[str]:
        """Chunk text data with optional line boundary preservation."""
        size = chunk_size or self.config.chunk_size
        
        if isinstance(data, str):
            # Chunk from string
            if self.config.line_based:
                yield from self._chunk_lines(data.splitlines(), size)
            else:
                for i in range(0, len(data), size):
                    yield data[i:i + size]
        else:
            # Chunk from file-like object
            if self.config.line_based:
                yield from self._chunk_lines_from_file(data, size)
            else:
                while True:
                    chunk = data.read(size)
                    if not chunk:
                        break
                    yield chunk
    
    def chunk_file(self, file_path: Union[str, Path]) -> Iterator[Union[str, bytes]]:
        """Chunk a file efficiently without loading it entirely into memory."""
        path = Path(file_path)
        
        if self.config.encoding:
            # Text mode
            with path.open('r', encoding=self.config.encoding) as f:
                yield from self.chunk_text(f)
        else:
            # Binary mode
            with path.open('rb') as f:
                yield from self.chunk_bytes(f)
    
    def chunk_with_overlap(self, data: Union[str, bytes], chunk_size: Optional[int] = None) -> Iterator[Union[str, bytes]]:
        """Chunk data with overlap between chunks for context preservation."""
        size = chunk_size or self.config.chunk_size
        overlap = self.config.overlap_size
        
        if overlap >= size:
            raise ValueError("Overlap size must be smaller than chunk size")
        
        if not data:
            return
        
        start = 0
        while start < len(data):
            end = min(start + size, len(data))
            chunk = data[start:end]
            yield chunk
            
            # Move start position considering overlap
            if end == len(data):
                break
            start = end - overlap
    
    def _chunk_lines(self, lines: list[str], approximate_chunk_size: int) -> Iterator[str]:
        """Chunk lines to approximate the given size while preserving line boundaries."""
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line)
            
            # If adding this line would exceed chunk size and we already have content
            if current_size + line_size > approximate_chunk_size and current_chunk:
                yield '\n'.join(current_chunk) + '\n'
                current_chunk = []
                current_size = 0
            
            current_chunk.append(line)
            current_size += line_size + 1  # +1 for newline
        
        # Yield remaining lines
        if current_chunk:
            yield '\n'.join(current_chunk) + '\n'
    
    def _chunk_lines_from_file(self, file: TextIO, approximate_chunk_size: int) -> Iterator[str]:
        """Chunk lines from a file object to approximate the given size."""
        current_chunk = []
        current_size = 0
        
        for line in file:
            line_size = len(line)
            
            # If adding this line would exceed chunk size and we already have content
            if current_size + line_size > approximate_chunk_size and current_chunk:
                yield ''.join(current_chunk)
                current_chunk = []
                current_size = 0
            
            current_chunk.append(line)
            current_size += line_size
        
        # Yield remaining lines
        if current_chunk:
            yield ''.join(current_chunk)
    
    def estimate_chunks(self, data_size: int, chunk_size: Optional[int] = None) -> int:
        """Estimate the number of chunks for given data size."""
        size = chunk_size or self.config.chunk_size
        return (data_size + size - 1) // size  # Ceiling division
    
    def chunk_iterable(self, iterable: Iterator[Any], chunk_size: Optional[int] = None) -> Iterator[list[Any]]:
        """Chunk any iterable into lists of specified size."""
        size = chunk_size or self.config.chunk_size
        chunk = []
        
        for item in iterable:
            chunk.append(item)
            if len(chunk) >= size:
                yield chunk
                chunk = []
        
        # Yield remaining items
        if chunk:
            yield chunk