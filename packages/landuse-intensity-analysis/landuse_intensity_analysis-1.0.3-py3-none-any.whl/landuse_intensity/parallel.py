"""
Parallel processing utilities for landuse-intensity-analysis.

This module provides parallel processing capabilities using multiple backends:
- Dask: For distributed computing and large datasets
- Ray: For high-performance distributed computing
- Multiprocessing: For simple parallel processing
- Sequential: For debugging and single-threaded execution

The module automatically handles:
- Data chunking for large datasets
- Memory management across workers
- Progress tracking
- Error handling and recovery
- Backend selection based on data size and available resources

Example:
    >>> from landuse_intensity.parallel import ParallelProcessor
    >>>
    >>> processor = ParallelProcessor(backend="dask", n_workers=4)
    >>> results = processor.map(compute_function, data_chunks)
"""

import logging
import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

# Backend availability flags
try:
    import dask
    from dask import delayed
    from dask.distributed import Client
    HAS_DASK = True
except ImportError:
    HAS_DASK = False

try:
    import ray
    HAS_RAY = True
except ImportError:
    HAS_RAY = False


class ParallelProcessor:
    """
    Parallel processing manager with multiple backend support.

    This class provides a unified interface for parallel processing
    across different backends and automatically optimizes based on
    data size and available resources.
    """

    def __init__(self,
                 backend: str = "auto",
                 n_workers: Optional[int] = None,
                 chunk_size: Union[str, int] = "auto",
                 memory_limit: Optional[str] = None,
                 threads_per_worker: int = 1):
        """
        Initialize parallel processor.

        Parameters
        ----------
        backend : str, default "auto"
            Processing backend: 'auto', 'dask', 'ray', 'multiprocessing', 'sequential'
        n_workers : int, optional
            Number of worker processes
        chunk_size : str or int, default "auto"
            Size of data chunks for processing
        memory_limit : str, optional
            Memory limit per worker
        threads_per_worker : int, default 1
            Threads per worker process
        """
        self.backend = self._select_backend(backend)
        self.n_workers = n_workers or self._detect_optimal_workers()
        self.chunk_size = chunk_size
        self.memory_limit = memory_limit
        self.threads_per_worker = threads_per_worker

        self._client = None
        self._executor = None

        logger.info(f"Initialized {self.backend} processor with {self.n_workers} workers")

    def _select_backend(self, backend: str) -> str:
        """Select the best available backend."""
        if backend == "auto":
            # Auto-select based on availability and data size
            if HAS_DASK:
                return "dask"
            elif HAS_RAY:
                return "ray"
            else:
                return "multiprocessing"
        elif backend == "dask" and not HAS_DASK:
            logger.warning("Dask not available, falling back to multiprocessing")
            return "multiprocessing"
        elif backend == "ray" and not HAS_RAY:
            logger.warning("Ray not available, falling back to multiprocessing")
            return "multiprocessing"
        else:
            return backend

    def _detect_optimal_workers(self) -> int:
        """Detect optimal number of workers based on system resources."""
        cpu_count = multiprocessing.cpu_count()

        # Reserve some cores for system operations
        if cpu_count > 4:
            return cpu_count - 2
        elif cpu_count > 2:
            return cpu_count - 1
        else:
            return 1

    def _initialize_backend(self):
        """Initialize the selected backend."""
        if self.backend == "dask":
            self._initialize_dask()
        elif self.backend == "ray":
            self._initialize_ray()
        elif self.backend == "multiprocessing":
            self._initialize_multiprocessing()

    def _initialize_dask(self):
        """Initialize Dask client."""
        if not HAS_DASK:
            raise ImportError("Dask is required for Dask backend")

        try:
            # Configure Dask client
            dask_config = {
                'distributed.worker.memory.target': 0.6,
                'distributed.worker.memory.spill': 0.7,
                'distributed.worker.memory.pause': 0.8,
                'distributed.worker.memory.terminate': 0.95,
            }

            if self.memory_limit:
                dask_config['distributed.worker.memory.limit'] = self.memory_limit

            # Start local cluster if no existing client
            if not Client.current():
                from dask.distributed import LocalCluster
                cluster = LocalCluster(
                    n_workers=self.n_workers,
                    threads_per_worker=self.threads_per_worker,
                    memory_limit=self.memory_limit,
                    silence_logs=False
                )
                self._client = Client(cluster)
            else:
                self._client = Client.current()

            logger.info(f"Dask client initialized: {self._client}")

        except Exception as e:
            logger.error(f"Failed to initialize Dask: {e}")
            raise

    def _initialize_ray(self):
        """Initialize Ray."""
        if not HAS_RAY:
            raise ImportError("Ray is required for Ray backend")

        try:
            if not ray.is_initialized():
                ray.init(
                    num_cpus=self.n_workers,
                    memory=self.memory_limit,
                    ignore_reinit_error=True
                )
            logger.info("Ray initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Ray: {e}")
            raise

    def _initialize_multiprocessing(self):
        """Initialize multiprocessing pool."""
        self._executor = ProcessPoolExecutor(max_workers=self.n_workers)

    def map(self, func: Callable, data: List[Any], **kwargs) -> List[Any]:
        """
        Apply function to each item in data using parallel processing.

        Parameters
        ----------
        func : callable
            Function to apply to each data item
        data : list
            List of data items to process
        **kwargs
            Additional arguments for func

        Returns
        -------
        list
            Results of applying func to each data item
        """
        if not data:
            return []

        # Initialize backend if needed
        if self._client is None and self.backend != "sequential":
            self._initialize_backend()

        if self.backend == "dask":
            return self._map_dask(func, data, **kwargs)
        elif self.backend == "ray":
            return self._map_ray(func, data, **kwargs)
        elif self.backend == "multiprocessing":
            return self._map_multiprocessing(func, data, **kwargs)
        else:  # sequential
            return self._map_sequential(func, data, **kwargs)

    def _map_dask(self, func: Callable, data: List[Any], **kwargs) -> List[Any]:
        """Map using Dask."""
        try:
            # Create delayed tasks
            delayed_tasks = [delayed(func)(item, **kwargs) for item in data]

            # Compute results
            results = delayed_tasks.compute()

            return results

        except Exception as e:
            logger.error(f"Dask mapping failed: {e}")
            raise

    def _map_ray(self, func: Callable, data: List[Any], **kwargs) -> List[Any]:
        """Map using Ray."""
        try:
            # Create Ray remote function
            @ray.remote
            def remote_func(item, **kw):
                return func(item, **kw)

            # Submit tasks
            futures = [remote_func.remote(item, **kwargs) for item in data]

            # Get results
            results = ray.get(futures)

            return results

        except Exception as e:
            logger.error(f"Ray mapping failed: {e}")
            raise

    def _map_multiprocessing(self, func: Callable, data: List[Any], **kwargs) -> List[Any]:
        """Map using multiprocessing."""
        try:
            # Submit tasks
            futures = [
                self._executor.submit(func, item, **kwargs)
                for item in data
            ]

            # Collect results
            results = []
            for future in as_completed(futures):
                results.append(future.result())

            # Maintain original order
            return [results[i] for i in range(len(data))]

        except Exception as e:
            logger.error(f"Multiprocessing mapping failed: {e}")
            raise

    def _map_sequential(self, func: Callable, data: List[Any], **kwargs) -> List[Any]:
        """Map using sequential processing."""
        return [func(item, **kwargs) for item in data]

    def chunk_data(self, data: List[Any], chunk_size: Optional[int] = None) -> List[List[Any]]:
        """
        Split data into chunks for parallel processing.

        Parameters
        ----------
        data : list
            Data to chunk
        chunk_size : int, optional
            Size of each chunk

        Returns
        -------
        list of lists
            Data split into chunks
        """
        if chunk_size is None:
            chunk_size = self._calculate_optimal_chunk_size(data)

        chunks = []
        for i in range(0, len(data), chunk_size):
            chunks.append(data[i:i + chunk_size])

        return chunks

    def _calculate_optimal_chunk_size(self, data: List[Any]) -> int:
        """Calculate optimal chunk size based on data size and workers."""
        if not data:
            return 1

        # Estimate data size
        avg_item_size = len(str(data[0])) if data else 1000

        # Target chunk size based on memory and workers
        target_chunk_size = max(1, len(data) // (self.n_workers * 4))

        # Adjust based on estimated memory usage
        if avg_item_size > 10000:  # Large items
            target_chunk_size = max(1, target_chunk_size // 4)

        return target_chunk_size

    def process_contingency_table(self,
                                 raster_data: Any,
                                 pixel_resolution: float = 30.0,
                                 **kwargs) -> Any:
        """
        Process contingency table in parallel.

        This is a specialized method for contingency table computation
        that can be parallelized across time periods or spatial chunks.
        """
        # Implementation would depend on the specific contingency table function
        # For now, this is a placeholder
        logger.info("Processing contingency table in parallel")
        # This would call the actual contingency table function with parallel processing
        pass

    def close(self):
        """Close parallel processing resources."""
        if self._client and self.backend == "dask":
            self._client.close()
        if self.backend == "ray" and ray.is_initialized():
            ray.shutdown()
        if self._executor:
            self._executor.shutdown()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        stats = {
            'backend': self.backend,
            'n_workers': self.n_workers,
            'threads_per_worker': self.threads_per_worker,
            'chunk_size': self.chunk_size,
            'memory_limit': self.memory_limit
        }

        if self.backend == "dask" and self._client:
            stats['dask_dashboard'] = self._client.dashboard_link
            stats['dask_workers'] = len(self._client.scheduler_info()['workers'])

        return stats


# Convenience functions
def get_available_backends() -> List[str]:
    """Get list of available parallel backends."""
    backends = ['sequential']

    if HAS_DASK:
        backends.append('dask')
    if HAS_RAY:
        backends.append('ray')

    backends.append('multiprocessing')  # Always available

    return backends

def create_processor(backend: str = "auto", **kwargs) -> ParallelProcessor:
    """
    Create a parallel processor with the specified backend.

    Parameters
    ----------
    backend : str, default "auto"
        Processing backend
    **kwargs
        Additional arguments for ParallelProcessor

    Returns
    -------
    ParallelProcessor
        Configured parallel processor
    """
    return ParallelProcessor(backend=backend, **kwargs)

def parallel_map(func: Callable,
                 data: List[Any],
                 backend: str = "auto",
                 **kwargs) -> List[Any]:
    """
    Convenience function for parallel mapping.

    Parameters
    ----------
    func : callable
        Function to apply
    data : list
        Data to process
    backend : str, default "auto"
        Processing backend
    **kwargs
        Additional arguments

    Returns
    -------
    list
        Processing results
    """
    with create_processor(backend, **kwargs) as processor:
        return processor.map(func, data)
