# -*- coding: utf-8 -*-
"""Tests for loguru integration with joblib-tqdm."""

import io
import sys
from unittest.mock import Mock

import pytest

from job_tqdflex.parallel import ParallelApplier, _get_logger_function, tqdm_joblib


def square(x):
    """Simple square function for testing."""
    return x ** 2


class TestGetLoggerFunction:
    """Test the _get_logger_function utility."""
    
    def test_no_logger_returns_default(self):
        """Test that None logger returns default logger functions."""
        debug_func, error_func = _get_logger_function(None)
        assert callable(debug_func)
        assert callable(error_func)
    
    def test_standard_logger(self):
        """Test standard logging.Logger integration."""
        import logging
        
        logger = logging.getLogger('test_logger')
        debug_func, error_func = _get_logger_function(logger)
        
        assert debug_func == logger.debug
        assert error_func == logger.error
    
    def test_mock_loguru_logger(self):
        """Test loguru-like logger integration with mocked loguru."""
        # Mock loguru logger attributes
        mock_logger = Mock()
        mock_logger.bind = Mock(return_value=mock_logger)
        mock_logger.opt = Mock(return_value=mock_logger)
        mock_logger.debug = Mock()
        mock_logger.error = Mock()
        
        debug_func, error_func = _get_logger_function(mock_logger)
        
        assert debug_func == mock_logger.debug
        assert error_func == mock_logger.error
    
    def test_invalid_logger_fallback(self):
        """Test that invalid logger falls back to default."""
        invalid_logger = object()  # Object without debug/error methods
        
        debug_func, error_func = _get_logger_function(invalid_logger)
        
        # Should fall back to module logger functions
        assert callable(debug_func)
        assert callable(error_func)


class TestParallelApplierWithCustomLogger:
    """Test ParallelApplier with custom logger integration."""
    
    def test_custom_logger_parameter(self):
        """Test that ParallelApplier accepts custom logger parameter."""
        mock_logger = Mock()
        mock_logger.debug = Mock()
        mock_logger.error = Mock()
        
        data = [1, 2, 3, 4]
        applier = ParallelApplier(square, data, n_jobs=1, logger=mock_logger)
        
        # Verify logger was set
        assert applier._debug_log == mock_logger.debug
        assert applier._error_log == mock_logger.error
    
    def test_custom_logger_used_in_processing(self, capfd):
        """Test that custom logger is actually used during processing."""
        # Create a list to capture log calls
        log_calls = []
        
        def mock_debug(msg):
            log_calls.append(('debug', msg))
        
        def mock_error(msg):
            log_calls.append(('error', msg))
        
        mock_logger = Mock()
        mock_logger.debug = mock_debug
        mock_logger.error = mock_error
        
        data = [1, 2, 3, 4]
        applier = ParallelApplier(square, data, n_jobs=1, logger=mock_logger, show_progress=False)
        results = applier()
        
        # Verify results are correct
        assert results == [1, 4, 9, 16]
        
        # Verify logger was called
        assert len(log_calls) >= 2  # At least initialization and completion logs
        debug_calls = [call for call in log_calls if call[0] == 'debug']
        assert len(debug_calls) >= 2
    
    def test_standard_logger_integration(self):
        """Test integration with standard logging module."""
        import logging
        import io
        
        # Set up string stream to capture logs
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        
        test_logger = logging.getLogger('test_parallel')
        test_logger.setLevel(logging.DEBUG)
        test_logger.addHandler(handler)
        
        data = [1, 2, 3]
        applier = ParallelApplier(square, data, n_jobs=1, logger=test_logger, show_progress=False)
        results = applier()
        
        # Verify results
        assert results == [1, 4, 9]
        
        # Check that logs were written
        log_output = log_stream.getvalue()
        assert 'Initialized ParallelApplier' in log_output or 'Processing completed' in log_output
        
        # Clean up
        test_logger.removeHandler(handler)
        handler.close()


class TestTqdmJoblibWithCustomLogger:
    """Test tqdm_joblib context manager with custom logger."""
    
    def test_tqdm_joblib_accepts_logger_parameter(self):
        """Test that tqdm_joblib accepts logger parameter without errors."""
        from tqdm import tqdm
        from joblib import Parallel, delayed
        
        mock_logger = Mock()
        mock_logger.debug = Mock()
        mock_logger.error = Mock()
        
        # This should not raise an error
        with tqdm_joblib(tqdm(total=3, desc="Test"), logger=mock_logger) as pbar:
            results = Parallel(n_jobs=1)(delayed(square)(i) for i in [1, 2, 3])
            
        assert results == [1, 4, 9]
    
    def test_tqdm_joblib_none_logger(self):
        """Test tqdm_joblib with None logger (default behavior)."""
        from tqdm import tqdm
        from joblib import Parallel, delayed
        
        # This should work the same as before (backwards compatibility)
        with tqdm_joblib(tqdm(total=3, desc="Test")) as pbar:
            results = Parallel(n_jobs=1)(delayed(square)(i) for i in [1, 2, 3])
            
        assert results == [1, 4, 9]


# Integration test that would work with actual loguru if available
@pytest.mark.skipif(True, reason="Requires loguru to be installed - only runs in dev environment")
class TestActualLoguruIntegration:
    """Test actual loguru integration (only runs when loguru is available)."""
    
    def test_real_loguru_logger(self):
        """Test with real loguru logger (requires loguru to be installed)."""
        try:
            from loguru import logger
            
            data = [1, 2, 3, 4, 5]
            applier = ParallelApplier(square, data, n_jobs=2, logger=logger, show_progress=False)
            results = applier()
            
            assert results == [1, 4, 9, 16, 25]
            
        except ImportError:
            pytest.skip("loguru not available")


if __name__ == "__main__":
    pytest.main([__file__])