"""
Test suite for caching modules
"""
import pytest
from unittest.mock import patch, MagicMock
from clyrdia.caching.manager import CacheManager
from clyrdia.caching.models import CachedResult

class TestCachedResult:
    """Test CachedResult model"""

    def test_cached_result_creation(self):
        """Test creating CachedResult"""
        cached_result = CachedResult(
            cache_key="test_key_123",
            model="gpt-4o-mini",
            test_name="Test Case",
            response="Test response",
            latency_ms=1000,
            cost=0.001,
            quality_score=0.8,
            input_tokens=50,
            output_tokens=25,
            timestamp=1234567890
        )
        
        assert cached_result.cache_key == "test_key_123"
        assert cached_result.model == "gpt-4o-mini"
        assert cached_result.test_name == "Test Case"
        assert cached_result.latency_ms == 1000
        assert cached_result.cost == 0.001
        assert cached_result.quality_score == 0.8

class TestCacheManager:
    """Test CacheManager functionality"""

    def test_cache_manager_initialization(self):
        """Test CacheManager initializes correctly"""
        manager = CacheManager()
        assert manager is not None
        assert hasattr(manager, 'db_path')

    @patch('clyrdia.caching.manager.sqlite3.connect')
    def test_initialize_database(self, mock_connect):
        """Test database initialization"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        manager = CacheManager()
        manager._initialize_database()
        
        # Verify table creation
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()
        mock_conn.close.assert_called()

    def test_generate_cache_key(self):
        """Test cache key generation"""
        manager = CacheManager()
        
        key1 = manager._generate_cache_key("gpt-4o-mini", "Test Case", "Test prompt")
        key2 = manager._generate_cache_key("gpt-4o-mini", "Test Case", "Test prompt")
        key3 = manager._generate_cache_key("gpt-4o-mini", "Test Case", "Different prompt")
        
        # Same inputs should generate same key
        assert key1 == key2
        # Different inputs should generate different keys
        assert key1 != key3
        
        # Key should be a string
        assert isinstance(key1, str)
        assert len(key1) > 0

    @patch('clyrdia.caching.manager.sqlite3.connect')
    def test_get_cached_result(self, mock_connect):
        """Test getting cached result"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock a cached result
        mock_cursor.fetchone.return_value = (
            "test_key", "gpt-4o-mini", "Test Case", "Test response",
            1000, 0.001, 0.8, 50, 25, 1234567890
        )
        
        mock_connect.return_value = mock_conn
        
        manager = CacheManager()
        result = manager.get_cached_result("test_key")
        
        assert result is not None
        assert result.cache_key == "test_key"
        assert result.model == "gpt-4o-mini"

    @patch('clyrdia.caching.manager.sqlite3.connect')
    def test_get_cached_result_not_found(self, mock_connect):
        """Test getting non-existent cached result"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock no result found
        mock_cursor.fetchone.return_value = None
        
        mock_connect.return_value = mock_conn
        
        manager = CacheManager()
        result = manager.get_cached_result("nonexistent_key")
        
        assert result is None

    @patch('clyrdia.caching.manager.sqlite3.connect')
    def test_cache_result(self, mock_connect):
        """Test caching a result"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        manager = CacheManager()
        
        cached_result = CachedResult(
            cache_key="test_key_123",
            model="gpt-4o-mini",
            test_name="Test Case",
            response="Test response",
            latency_ms=1000,
            cost=0.001,
            quality_score=0.8,
            input_tokens=50,
            output_tokens=25,
            timestamp=1234567890
        )
        
        manager.cache_result(cached_result)
        
        # Verify insert was called
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()
        mock_conn.close.assert_called()

    @patch('clyrdia.caching.manager.sqlite3.connect')
    def test_get_cache_stats(self, mock_connect):
        """Test getting cache statistics"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock stats results
        mock_cursor.fetchall.side_effect = [
            [("gpt-4o-mini", 5)],  # Model counts
            [(1000,)],  # Total size
            [(5,)]  # Total entries
        ]
        
        mock_connect.return_value = mock_conn
        
        manager = CacheManager()
        stats = manager.get_cache_stats()
        
        assert 'models' in stats
        assert 'total_size_mb' in stats
        assert 'total_entries' in stats
        assert stats['total_entries'] == 5

    @patch('clyrdia.caching.manager.sqlite3.connect')
    def test_clear_cache(self, mock_connect):
        """Test clearing entire cache"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        manager = CacheManager()
        manager.clear_cache()
        
        # Verify delete was called
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()
        mock_conn.close.assert_called()

    @patch('clyrdia.caching.manager.sqlite3.connect')
    def test_clear_model_cache(self, mock_connect):
        """Test clearing cache for specific model"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        manager = CacheManager()
        manager.clear_model_cache("gpt-4o-mini")
        
        # Verify delete was called with model filter
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()
        mock_conn.close.assert_called()

    def test_cache_key_uniqueness(self):
        """Test that cache keys are unique for different inputs"""
        manager = CacheManager()
        
        # Test different models
        key1 = manager._generate_cache_key("gpt-4o-mini", "Test Case", "Test prompt")
        key2 = manager._generate_cache_key("gpt-4o", "Test Case", "Test prompt")
        assert key1 != key2
        
        # Test different test cases
        key3 = manager._generate_cache_key("gpt-4o-mini", "Different Case", "Test prompt")
        assert key1 != key3
        
        # Test different prompts
        key4 = manager._generate_cache_key("gpt-4o-mini", "Test Case", "Different prompt")
        assert key1 != key4

    def test_cache_key_consistency(self):
        """Test that cache keys are consistent for same inputs"""
        manager = CacheManager()
        
        prompt = "This is a test prompt with special characters: !@#$%^&*()"
        
        # Generate same key multiple times
        key1 = manager._generate_cache_key("gpt-4o-mini", "Test Case", prompt)
        key2 = manager._generate_cache_key("gpt-4o-mini", "Test Case", prompt)
        key3 = manager._generate_cache_key("gpt-4o-mini", "Test Case", prompt)
        
        assert key1 == key2 == key3
