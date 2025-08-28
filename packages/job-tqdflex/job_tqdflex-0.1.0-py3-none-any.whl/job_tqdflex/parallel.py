# -*- coding: utf-8 -*-
"""Module for parallel processing of functions with joblib and tqdm for the progress bar

The tqdm_joblib context manager is based on the implementation by Louis Abraham:
https://github.com/louisabraham/tqdm_joblib

Original implementation distributed under CC BY-SA 4.0.
This adaptation maintains CC BY-SA 4.0 licensing requirements.

Attribution: Original tqdm_joblib context manager concept by Louis Abraham,
based on Stack Overflow solution.
"""

import contextlib
import logging
from functools import partial
from math import ceil
from typing import Any, Callable, Iterable, Iterator, List, TypeVar, Union, Optional

import joblib
from joblib import Parallel, delayed
from tqdm import tqdm

# Set up optional logging
logger = logging.getLogger(__name__)

T = TypeVar('T')


def _get_logger_function(custom_logger=None):
    """
    Get appropriate logging function based on logger type.
    
    Args:
        custom_logger: Optional custom logger instance (loguru, standard logging, etc.)
        
    Returns:
        tuple: (debug_func, error_func) logging functions
    """
    if custom_logger is None:
        # Use module's default logger
        return logger.debug, logger.error
    
    # Check if it's loguru logger (has bind method and different API)
    if hasattr(custom_logger, 'bind') and hasattr(custom_logger, 'opt'):
        # Loguru logger
        return custom_logger.debug, custom_logger.error
    
    # Check if it's standard logging.Logger
    elif hasattr(custom_logger, 'debug') and hasattr(custom_logger, 'error'):
        # Standard logging.Logger
        return custom_logger.debug, custom_logger.error
    
    # Fallback to module logger if custom logger doesn't have expected methods
    else:
        return logger.debug, logger.error

__all__ = ["ParallelApplier", "tqdm_joblib"]


@contextlib.contextmanager
def tqdm_joblib(tqdm_object, logger=None):
    """Context manager to patch joblib to report into tqdm progress bar given as argument
    
    Based on the original implementation by Louis Abraham:
    https://github.com/louisabraham/tqdm_joblib
    
    Original Stack Overflow source:
    https://stackoverflow.com/questions/24983493/tracking-progress-of-joblib-parallel-execution/58936697#comment95750316_49950707
    
    Args:
        tqdm_object: A tqdm progress bar instance
        logger: Optional logger instance (supports both standard logging and loguru)
        
    Yields:
        The tqdm progress bar object
        
    Example:
        >>> from tqdm import tqdm
        >>> from joblib import Parallel, delayed
        >>> import time
        >>> 
        >>> def slow_function(x):
        ...     time.sleep(0.1)
        ...     return x ** 2
        >>> 
        >>> with tqdm_joblib(tqdm(total=10, desc="Processing")) as progress_bar:
        ...     results = Parallel(n_jobs=2)(delayed(slow_function)(i) for i in range(10))
        >>>
        >>> # With custom logger (e.g., loguru)
        >>> from loguru import logger as loguru_logger
        >>> with tqdm_joblib(tqdm(total=10, desc="Processing"), logger=loguru_logger) as progress_bar:
        ...     results = Parallel(n_jobs=2)(delayed(slow_function)(i) for i in range(10))
    """

    class TqdmBatchCompletionCallback(joblib.parallel.BatchCompletionCallBack):
        def __call__(self, *args, **kwargs):
            tqdm_object.update(n=self.batch_size)
            return super().__call__(*args, **kwargs)

    old_batch_callback = joblib.parallel.BatchCompletionCallBack
    joblib.parallel.BatchCompletionCallBack = TqdmBatchCompletionCallback
    try:
        yield tqdm_object
    finally:
        joblib.parallel.BatchCompletionCallBack = old_batch_callback
        tqdm_object.close()


class ParallelApplier:
    """A parallel function applier with progress tracking and chunking support.
    
    This class provides a convenient interface for applying functions to iterables
    in parallel using joblib, with integrated tqdm progress bars and automatic
    chunking for optimal performance.
    
    Attributes:
        func: The function to apply to each element
        iterable: The input data to process
        show_progress: Whether to show progress bars
        n_jobs: Number of parallel jobs
        backend: Parallelization backend
        total_items: Total number of items to process
        chunk_size: Size of chunks to process
        func_name: Name of the function being applied
        
    Example:
        >>> def square(x):
        ...     return x ** 2
        >>> 
        >>> data = range(1000)
        >>> applier = ParallelApplier(square, data, n_jobs=4)
        >>> results = applier()
        >>> 
        >>> # With additional arguments
        >>> def power(x, exponent=2):
        ...     return x ** exponent
        >>> 
        >>> applier = ParallelApplier(power, data, n_jobs=4)
        >>> results = applier(exponent=3)
        >>>
        >>> # With custom logger (e.g., loguru)
        >>> from loguru import logger as loguru_logger
        >>> applier = ParallelApplier(square, data, n_jobs=4, logger=loguru_logger)
        >>> results = applier()
        >>>
        >>> # With custom progress bar description
        >>> applier = ParallelApplier(square, data, n_jobs=4, custom_desc="Processing data points")
        >>> results = applier()
    """
    
    def __init__(
        self,
        func: Callable,
        iterable: Union[Iterable[T], Iterator[T]],
        show_progress: bool = True,
        n_jobs: int = 8,
        backend: str = "loky",
        chunk_size: Optional[int] = None,
        custom_desc: Optional[str] = None,
        logger=None,
    ):
        """
        Initialize the parallel applier.

        Args:
            func: Function to apply to each element
            iterable: Input data to process (can be generator or iterable)
            show_progress: Whether to show progress bars
            n_jobs: Number of parallel jobs (-1 for all cores)
            backend: Parallelization backend ('loky', 'threading', or 'multiprocessing')
            chunk_size: Size of chunks to process (if None, calculated automatically)
            custom_desc: Custom description for the progress bar (if None, uses default)
            logger: Optional custom logger instance (supports standard logging and loguru)
            
        Raises:
            TypeError: If func is not callable or is a lambda function
            ValueError: If invalid backend is provided or iterable is empty
        """
        self.func = self._set_func(func)
        self.show_progress = show_progress
        self.n_jobs = n_jobs if n_jobs > 0 else None  # None means all cores in joblib
        self.backend = self._set_backend(backend)
        self.custom_desc = custom_desc
        
        # Set up logging functions
        self._debug_log, self._error_log = _get_logger_function(logger)
        
        # Handle generators and iterables efficiently
        self._original_iterable = iterable
        self._items_loaded = False
        self._items_cache = None
        
        # Load items to determine size
        self._load_items()
        self.chunk_size = self._set_chunk_size(chunk_size)
        
        self._debug_log(f"Initialized ParallelApplier with {self.total_items} items, "
                       f"chunk size: {self.chunk_size}, n_jobs: {self.n_jobs}")

    def _load_items(self) -> None:
        """Load items from iterable and cache them."""
        if not self._items_loaded:
            self._items_cache = list(self._original_iterable)
            self.total_items = len(self._items_cache)
            self._items_loaded = True
            
            if self.total_items == 0:
                raise ValueError("Empty iterable provided.")

    @property
    def iterable(self) -> List[T]:
        """Get the cached iterable items."""
        if not self._items_loaded:
            self._load_items()
        return self._items_cache

    def _set_chunk_size(self, chunk_size: Optional[int]) -> int:
        """Calculate optimal chunk size based on total items and number of jobs."""
        if self.n_jobs is None:
            # Use all available cores
            import os
            n_cores = os.cpu_count() or 1
        else:
            n_cores = self.n_jobs
            
        if self.total_items <= n_cores:
            return 1
        elif chunk_size is None:
            # Calculate chunk size with minimum of 1
            return max(1, ceil(self.total_items / (n_cores * 4)))  # 4x cores for better load balancing
        else:
            return max(1, chunk_size)

    def _set_func(self, func) -> Callable:
        """Set the function to be parallelized.

        Args:
            func: Function to apply to each element

        Raises:
            TypeError: if the provided input is not a callable or is a lambda

        Returns:
            Callable: The function to apply
        """
        if not callable(func):
            raise TypeError("func should be a callable function.")
            
        if hasattr(func, "__name__"):
            if func.__name__ == "<lambda>":
                raise TypeError("parallel_applier does not support lambda functions. "
                              "Please use a named function or functools.partial instead.")
            else:
                func_name = func.__name__
        else:
            if isinstance(func, partial):
                func_name = getattr(func.func, '__name__', 'partial_function')
            else:
                func_name = getattr(func, '__class__', type(func)).__name__
                
        self.func_name = func_name
        return func

    def _set_backend(self, backend: str) -> str:
        """Set the parallelization backend.

        Args:
            backend: Parallelization backend ('loky', 'threading', or 'multiprocessing')

        Raises:
            ValueError: If an invalid backend is provided

        Returns:
            str: Selected backend
        """
        valid_backends = ["loky", "threading", "multiprocessing"]
        if backend not in valid_backends:
            raise ValueError(
                f"Invalid backend '{backend}'. Choose from {valid_backends}."
            )
        return backend

    def _make_chunks(self) -> List[List[T]]:
        """Split the iterable into chunks for parallel processing."""
        chunks = []
        items = self.iterable
        
        for i in range(0, self.total_items, self.chunk_size):
            chunk = items[i : i + self.chunk_size]
            chunks.append(chunk)
            
        self.n_chunks = len(chunks)
        self._debug_log(f"Created {self.n_chunks} chunks with lengths: {[len(chunk) for chunk in chunks]}")
        return chunks

    def _process_chunk(self, chunk: List[T], **kwargs) -> List[Any]:
        """
        Process a single chunk.

        Args:
            chunk: Chunk of data to process
            **kwargs: Additional arguments to pass to the function

        Returns:
            List of processed results
        """
        try:
            return [self.func(item, **kwargs) for item in chunk]
        except Exception as e:
            self._error_log(f"Error processing chunk: {e}")
            raise

    def __call__(self, **kwargs) -> List[Any]:
        """
        Apply the function to all items in parallel.

        Args:
            **kwargs: Additional arguments to pass to the function

        Returns:
            List of results in the same order as input

        Raises:
            ValueError: If trying to pass kwargs to a partial function
            RuntimeError: If parallel processing fails
        """
        try:
            chunks = self._make_chunks()
            
            # Validate kwargs usage
            if kwargs:
                self._debug_log(f"Passing kwargs: {list(kwargs.keys())}")
                if isinstance(self.func, partial):
                    raise ValueError(
                        "Cannot pass keyword arguments when using a partial function. "
                        "Initialize the partial function with all required arguments."
                    )
                process_chunk = partial(self._process_chunk, **kwargs)
            else:
                process_chunk = self._process_chunk

            # Execute parallel processing
            if self.show_progress and self.n_chunks > 1:
                # Use progress bar for multi-chunk processing
                desc = self.custom_desc if self.custom_desc is not None else f"Applying {self.func_name} to chunks"
                with tqdm_joblib(
                    tqdm(
                        total=self.n_chunks,
                        desc=desc,
                        unit="chunk",
                        position=0,
                        leave=True,
                    )
                ) as progress_bar:  # noqa: F841
                    results = Parallel(n_jobs=self.n_jobs, backend=self.backend)(
                        delayed(process_chunk)(chunk) for chunk in chunks
                    )
            else:
                # No progress bar for single chunk or when disabled
                results = Parallel(n_jobs=self.n_jobs, backend=self.backend)(
                    delayed(process_chunk)(chunk) for chunk in chunks
                )

            # Flatten results while preserving order
            flattened_results = []
            for chunk_result in results:
                flattened_results.extend(chunk_result)
                
            self._debug_log(f"Processing completed. Input: {self.total_items}, Output: {len(flattened_results)}")
            return flattened_results
            
        except Exception as e:
            self._error_log(f"Parallel processing failed: {e}")
            raise RuntimeError(f"Parallel processing failed: {e}") from e

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        # Clear cached items to free memory
        if hasattr(self, '_items_cache'):
            self._items_cache = None
            self._items_loaded = False
        self._debug_log("ParallelApplier context cleanup completed")
        return False