# -*- coding: utf-8 -*-
"""Tests for the parallel module."""

import contextlib
import io
import time
from functools import partial
from unittest.mock import Mock

import pytest
from joblib import delayed, Parallel

from job_tqdflex.parallel import ParallelApplier, tqdm_joblib


# Module-level functions for multiprocessing tests (must be pickleable)
def square_func(x):
    return x * x


class TestTqdmJoblib:
    """Tests for the tqdm_joblib context manager."""
    
    def test_tqdm_joblib_context_manager(self):
        """Test that tqdm_joblib works as a context manager."""
        mock_tqdm = Mock()
        mock_tqdm.close = Mock()
        
        with tqdm_joblib(mock_tqdm) as progress_bar:
            assert progress_bar is mock_tqdm
        
        mock_tqdm.close.assert_called_once()
    
    def test_tqdm_joblib_integration(self):
        """Test tqdm_joblib with actual joblib parallel execution."""
        from tqdm import tqdm
        
        def simple_func(x):
            time.sleep(0.01)  # Small delay to make progress visible
            return x * 2
        
        # Capture tqdm output
        with contextlib.redirect_stderr(io.StringIO()) as captured:
            with tqdm_joblib(tqdm(total=5, desc="Test")) as pbar:
                results = Parallel(n_jobs=2)(delayed(simple_func)(i) for i in range(5))
        
        assert results == [0, 2, 4, 6, 8]
        # Check that some progress output was captured
        output = captured.getvalue()
        assert "Test" in output or "%" in output


class TestParallelApplier:
    """Tests for the ParallelApplier class."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        def square(x):
            return x * x
        
        data = [1, 2, 3, 4, 5]
        applier = ParallelApplier(square, data)
        
        assert applier.func is square
        assert applier.total_items == 5
        assert applier.func_name == "square"
        assert applier.show_progress is True
        assert applier.n_jobs == 8
        assert applier.backend == "loky"
    
    def test_init_with_generator(self):
        """Test initialization with a generator."""
        def square(x):
            return x * x
        
        def data_generator():
            for i in range(10):
                yield i
        
        applier = ParallelApplier(square, data_generator())
        assert applier.total_items == 10
    
    def test_init_empty_iterable(self):
        """Test initialization with empty iterable raises ValueError."""
        def square(x):
            return x * x
        
        with pytest.raises(ValueError, match="Empty iterable provided"):
            ParallelApplier(square, [])
    
    def test_init_invalid_func(self):
        """Test initialization with non-callable raises TypeError."""
        with pytest.raises(TypeError, match="func should be a callable"):
            ParallelApplier("not_a_function", [1, 2, 3])
    
    def test_init_lambda_restriction(self):
        """Test that lambda functions are rejected."""
        with pytest.raises(TypeError, match="does not support lambda functions"):
            ParallelApplier(lambda x: x * 2, [1, 2, 3])
    
    def test_init_invalid_backend(self):
        """Test initialization with invalid backend raises ValueError."""
        def square(x):
            return x * x
        
        with pytest.raises(ValueError, match="Invalid backend"):
            ParallelApplier(square, [1, 2, 3], backend="invalid")
    
    def test_func_name_detection(self):
        """Test function name detection for different function types."""
        def named_func(x):
            return x
        
        partial_func = partial(pow, exp=2)
        
        class CallableClass:
            def __call__(self, x):
                return x
        
        callable_obj = CallableClass()
        
        # Named function
        applier1 = ParallelApplier(named_func, [1])
        assert applier1.func_name == "named_func"
        
        # Partial function
        applier2 = ParallelApplier(partial_func, [1])
        assert applier2.func_name == "pow"
        
        # Callable object
        applier3 = ParallelApplier(callable_obj, [1])
        assert applier3.func_name == "CallableClass"
    
    def test_chunk_size_calculation(self):
        """Test chunk size calculation logic."""
        def dummy(x):
            return x
        
        # Small dataset (items <= n_jobs)
        applier1 = ParallelApplier(dummy, [1, 2], n_jobs=4)
        assert applier1.chunk_size == 1
        
        # Large dataset with automatic chunk size
        applier2 = ParallelApplier(dummy, list(range(100)), n_jobs=4)
        assert applier2.chunk_size >= 1
        
        # Custom chunk size
        applier3 = ParallelApplier(dummy, list(range(100)), n_jobs=4, chunk_size=10)
        assert applier3.chunk_size == 10
    
    def test_basic_parallel_execution(self):
        """Test basic parallel execution."""
        def square(x):
            return x * x
        
        data = [1, 2, 3, 4, 5]
        applier = ParallelApplier(square, data, show_progress=False, n_jobs=2)
        results = applier()
        
        assert results == [1, 4, 9, 16, 25]
    
    def test_parallel_execution_with_kwargs(self):
        """Test parallel execution with keyword arguments."""
        def power(x, exponent=2):
            return x ** exponent
        
        data = [1, 2, 3, 4]
        applier = ParallelApplier(power, data, show_progress=False, n_jobs=2)
        results = applier(exponent=3)
        
        assert results == [1, 8, 27, 64]
    
    def test_partial_function_with_kwargs_error(self):
        """Test that partial functions with kwargs raise ValueError."""
        partial_func = partial(pow, exp=2)
        applier = ParallelApplier(partial_func, [1, 2, 3], show_progress=False)
        
        with pytest.raises(RuntimeError, match="Parallel processing failed.*Cannot pass keyword arguments when using a partial function"):
            applier(some_arg=1)
    
    def test_progress_bar_disabled(self):
        """Test execution without progress bar."""
        def square(x):
            return x * x
        
        data = [1, 2, 3, 4, 5]
        applier = ParallelApplier(square, data, show_progress=False, n_jobs=2)
        
        # Should not raise any errors and still return correct results
        results = applier()
        assert results == [1, 4, 9, 16, 25]
    
    def test_different_backends(self):
        """Test execution with different backends."""
        data = [1, 2, 3]
        
        for backend in ["loky", "threading", "multiprocessing"]:
            applier = ParallelApplier(square_func, data, show_progress=False, backend=backend)
            results = applier()
            assert results == [1, 4, 9]
    
    def test_context_manager(self):
        """Test ParallelApplier as context manager."""
        def square(x):
            return x * x
        
        data = [1, 2, 3, 4]
        
        with ParallelApplier(square, data, show_progress=False) as applier:
            results = applier()
        
        assert results == [1, 4, 9, 16]
        # Check that items cache is cleared
        assert not applier._items_loaded or applier._items_cache is None
    
    def test_large_dataset_chunking(self):
        """Test chunking with larger dataset."""
        def identity(x):
            return x
        
        data = list(range(1000))
        applier = ParallelApplier(identity, data, show_progress=False, n_jobs=4, chunk_size=50)
        results = applier()
        
        assert len(results) == 1000
        assert results == data
    
    def test_error_handling_in_function(self):
        """Test error handling when the applied function raises an exception."""
        def error_func(x):
            if x == 3:
                raise ValueError(f"Error with value {x}")
            return x * 2
        
        data = [1, 2, 3, 4]
        applier = ParallelApplier(error_func, data, show_progress=False, n_jobs=1)
        
        with pytest.raises(RuntimeError, match="Parallel processing failed"):
            applier()
    
    def test_logging_configuration(self):
        """Test that logging works correctly."""
        # Test that custom logger is properly set up
        import logging
        custom_logger = logging.getLogger("test_logger")
        
        data = [1, 2, 3, 4]
        applier = ParallelApplier(square_func, data, show_progress=False, n_jobs=1, logger=custom_logger)
        
        # Test should not raise any errors - successful execution means logging setup worked
        results = applier()
        assert results == [1, 4, 9, 16]
        
        # Verify the logger functions are properly assigned
        assert hasattr(applier, '_debug_log')
        assert hasattr(applier, '_error_log')
    
    def test_n_jobs_all_cores(self):
        """Test n_jobs=-1 uses all cores."""
        def square(x):
            return x * x
        
        data = [1, 2, 3, 4]
        applier = ParallelApplier(square, data, show_progress=False, n_jobs=-1)
        
        assert applier.n_jobs is None  # None means all cores in joblib
    
    def test_iterator_support(self):
        """Test that iterators are properly handled."""
        def square(x):
            return x * x
        
        # Test with an iterator that can only be consumed once
        data_iter = iter([1, 2, 3, 4, 5])
        applier = ParallelApplier(square, data_iter, show_progress=False)
        results = applier()
        
        assert results == [1, 4, 9, 16, 25]
    
    def test_single_item_processing(self):
        """Test processing of a single item."""
        def square(x):
            return x * x
        
        data = [5]
        applier = ParallelApplier(square, data, show_progress=False)
        results = applier()
        
        assert results == [25]
    
    @pytest.mark.parametrize("n_jobs", [1, 2, 4, 8])
    def test_different_n_jobs(self, n_jobs):
        """Test with different numbers of jobs."""
        def square(x):
            return x * x
        
        data = list(range(20))
        expected = [x * x for x in data]
        
        applier = ParallelApplier(square, data, show_progress=False, n_jobs=n_jobs)
        results = applier()
        
        assert results == expected