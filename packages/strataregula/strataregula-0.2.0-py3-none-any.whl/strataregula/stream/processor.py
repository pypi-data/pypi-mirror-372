"""
Stream processor with chunk processing capabilities.
Handles real-time streaming, memory-efficient processing, and async operations.
"""

import asyncio
from typing import Iterator, AsyncIterator, Callable, Optional, Union, Any, Dict, List
from dataclasses import dataclass
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from .chunker import Chunker, ChunkConfig


@dataclass
class ProcessingStats:
    """Statistics for stream processing operations."""
    chunks_processed: int = 0
    bytes_processed: int = 0
    processing_time: float = 0.0
    errors: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    @property
    def throughput(self) -> float:
        """Calculate throughput in bytes per second."""
        if self.processing_time > 0:
            return self.bytes_processed / self.processing_time
        return 0.0


class ChunkProcessor:
    """Processes data chunks with configurable processing functions."""
    
    def __init__(self, chunk_config: Optional[ChunkConfig] = None):
        self.chunker = Chunker(chunk_config or ChunkConfig())
        self.stats = ProcessingStats()
        self._processors: Dict[str, Callable] = {}
    
    def register_processor(self, name: str, processor: Callable[[Any], Any]) -> None:
        """Register a processing function for chunks."""
        self._processors[name] = processor
    
    def process_chunks(self, data: Union[str, bytes], processor_name: str, **kwargs) -> Iterator[Any]:
        """Process data in chunks using registered processor."""
        if processor_name not in self._processors:
            raise ValueError(f"Processor '{processor_name}' not registered")
        
        processor = self._processors[processor_name]
        self.stats = ProcessingStats()
        self.stats.start_time = time.time()
        
        try:
            if isinstance(data, str):
                chunks = self.chunker.chunk_text(data)
            else:
                chunks = self.chunker.chunk_bytes(data)
            
            for chunk in chunks:
                try:
                    result = processor(chunk, **kwargs)
                    self.stats.chunks_processed += 1
                    self.stats.bytes_processed += len(chunk)
                    yield result
                except Exception as e:
                    self.stats.errors += 1
                    yield {'error': str(e), 'chunk': chunk[:100]}  # Include first 100 chars for debugging
        
        finally:
            self.stats.end_time = time.time()
            if self.stats.start_time:
                self.stats.processing_time = self.stats.end_time - self.stats.start_time
    
    def process_file_chunks(self, file_path: str, processor_name: str, **kwargs) -> Iterator[Any]:
        """Process file in chunks using registered processor."""
        if processor_name not in self._processors:
            raise ValueError(f"Processor '{processor_name}' not registered")
        
        processor = self._processors[processor_name]
        self.stats = ProcessingStats()
        self.stats.start_time = time.time()
        
        try:
            for chunk in self.chunker.chunk_file(file_path):
                try:
                    result = processor(chunk, **kwargs)
                    self.stats.chunks_processed += 1
                    self.stats.bytes_processed += len(chunk)
                    yield result
                except Exception as e:
                    self.stats.errors += 1
                    yield {'error': str(e), 'file': file_path}
        
        finally:
            self.stats.end_time = time.time()
            if self.stats.start_time:
                self.stats.processing_time = self.stats.end_time - self.stats.start_time


class StreamProcessor:
    """Advanced stream processor with real-time capabilities and async support."""
    
    def __init__(self, chunk_config: Optional[ChunkConfig] = None, max_workers: int = 4):
        self.chunk_processor = ChunkProcessor(chunk_config)
        self.max_workers = max_workers
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._active_streams: Dict[str, bool] = {}
        self._stream_stats: Dict[str, ProcessingStats] = {}
    
    def register_processor(self, name: str, processor: Callable[[Any], Any]) -> None:
        """Register a processing function."""
        self.chunk_processor.register_processor(name, processor)
    
    def process_stream_sync(self, data_stream: Iterator[Any], processor_name: str, 
                           stream_id: Optional[str] = None, **kwargs) -> Iterator[Any]:
        """Process a data stream synchronously with chunks."""
        stream_id = stream_id or f"stream_{int(time.time())}"
        self._active_streams[stream_id] = True
        stats = ProcessingStats()
        stats.start_time = time.time()
        self._stream_stats[stream_id] = stats
        
        try:
            for data in data_stream:
                if not self._active_streams.get(stream_id, False):
                    break
                
                # Process data in chunks
                for result in self.chunk_processor.process_chunks(data, processor_name, **kwargs):
                    yield result
                    stats.chunks_processed += 1
                    stats.bytes_processed += len(str(data))
        
        finally:
            self._active_streams[stream_id] = False
            stats.end_time = time.time()
            if stats.start_time:
                stats.processing_time = stats.end_time - stats.start_time
    
    async def process_stream_async(self, data_stream: AsyncIterator[Any], processor_name: str,
                                  stream_id: Optional[str] = None, **kwargs) -> AsyncIterator[Any]:
        """Process an async data stream with chunks."""
        stream_id = stream_id or f"async_stream_{int(time.time())}"
        self._active_streams[stream_id] = True
        stats = ProcessingStats()
        stats.start_time = time.time()
        self._stream_stats[stream_id] = stats
        
        try:
            async for data in data_stream:
                if not self._active_streams.get(stream_id, False):
                    break
                
                # Process data in chunks asynchronously
                loop = asyncio.get_event_loop()
                results = await loop.run_in_executor(
                    self._executor, 
                    lambda: list(self.chunk_processor.process_chunks(data, processor_name, **kwargs))
                )
                
                for result in results:
                    yield result
                    stats.chunks_processed += 1
                    stats.bytes_processed += len(str(data))
        
        finally:
            self._active_streams[stream_id] = False
            stats.end_time = time.time()
            if stats.start_time:
                stats.processing_time = stats.end_time - stats.start_time
    
    def process_parallel(self, data_list: List[Any], processor_name: str, **kwargs) -> List[Any]:
        """Process multiple data items in parallel using thread pool."""
        if processor_name not in self.chunk_processor._processors:
            raise ValueError(f"Processor '{processor_name}' not registered")
        
        processor = self.chunk_processor._processors[processor_name]
        
        # Submit all processing tasks
        futures = []
        for data in data_list:
            future = self._executor.submit(
                lambda d: list(self.chunk_processor.process_chunks(d, processor_name, **kwargs)),
                data
            )
            futures.append(future)
        
        # Collect results
        results = []
        for future in futures:
            try:
                chunk_results = future.result()
                results.extend(chunk_results)
            except Exception as e:
                results.append({'error': str(e)})
        
        return results
    
    def stop_stream(self, stream_id: str) -> bool:
        """Stop an active stream."""
        if stream_id in self._active_streams:
            self._active_streams[stream_id] = False
            return True
        return False
    
    def get_stream_stats(self, stream_id: str) -> Optional[ProcessingStats]:
        """Get statistics for a specific stream."""
        return self._stream_stats.get(stream_id)
    
    def get_all_stats(self) -> Dict[str, ProcessingStats]:
        """Get statistics for all streams."""
        return self._stream_stats.copy()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        for stream_id in list(self._active_streams.keys()):
            self._active_streams[stream_id] = False
        self._executor.shutdown(wait=True)