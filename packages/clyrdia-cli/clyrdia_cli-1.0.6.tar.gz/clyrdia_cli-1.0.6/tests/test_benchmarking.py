"""
Test suite for benchmarking modules
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from clyrdia.benchmarking.engine import BenchmarkEngine
from clyrdia.benchmarking.interface import ModelInterface
from clyrdia.benchmarking.evaluator import QualityEvaluator
from clyrdia.models.config import ModelConfig, ClyrdiaConfig
from clyrdia.models.results import BenchmarkResult, TestCase

class TestModelInterface:
    """Test model interface functionality"""

    def test_model_interface_initialization(self):
        """Test ModelInterface initializes correctly"""
        api_keys = {'openai': 'sk-test123', 'anthropic': 'sk-ant-test123'}
        interface = ModelInterface(api_keys)
        
        assert interface.api_keys == api_keys
        assert hasattr(interface, 'openai_client')
        assert hasattr(interface, 'anthropic_client')

    def test_model_interface_openai_only(self):
        """Test ModelInterface with OpenAI only"""
        api_keys = {'openai': 'sk-test123'}
        interface = ModelInterface(api_keys)
        
        assert hasattr(interface, 'openai_client')
        assert not hasattr(interface, 'anthropic_client')

    def test_model_interface_anthropic_only(self):
        """Test ModelInterface with Anthropic only"""
        api_keys = {'anthropic': 'sk-ant-test123'}
        interface = ModelInterface(api_keys)
        
        assert hasattr(interface, 'anthropic_client')
        assert not hasattr(interface, 'openai_client')

    @patch('clyrdia.benchmarking.interface.AsyncOpenAI')
    def test_openai_client_setup(self, mock_openai):
        """Test OpenAI client setup"""
        api_keys = {'openai': 'sk-test123'}
        interface = ModelInterface(api_keys)
        
        mock_openai.assert_called_once_with(api_key='sk-test123')

    @patch('clyrdia.benchmarking.interface.anthropic.Anthropic')
    def test_anthropic_client_setup(self, mock_anthropic):
        """Test Anthropic client setup"""
        api_keys = {'anthropic': 'sk-ant-test123'}
        interface = ModelInterface(api_keys)
        
        mock_anthropic.assert_called_once_with(api_key='sk-ant-test123')

class TestQualityEvaluator:
    """Test quality evaluator functionality"""

    def test_quality_evaluator_initialization(self):
        """Test QualityEvaluator initializes correctly"""
        evaluator = QualityEvaluator()
        assert evaluator is not None

    def test_evaluate_response_basic(self):
        """Test basic response evaluation"""
        evaluator = QualityEvaluator()
        
        prompt = "What is 2+2?"
        response = "2+2 equals 4"
        expected = "The answer should be 4"
        
        score = evaluator.evaluate_response(prompt, response, expected)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_evaluate_response_empty(self):
        """Test evaluation with empty response"""
        evaluator = QualityEvaluator()
        
        prompt = "What is 2+2?"
        response = ""
        expected = "The answer should be 4"
        
        score = evaluator.evaluate_response(prompt, response, expected)
        
        assert score == 0.0

    def test_evaluate_response_exact_match(self):
        """Test evaluation with exact match"""
        evaluator = QualityEvaluator()
        
        prompt = "What is 2+2?"
        response = "4"
        expected = "4"
        
        score = evaluator.evaluate_response(prompt, response, expected)
        
        assert score == 1.0

class TestBenchmarkEngine:
    """Test benchmark engine functionality"""

    def test_benchmark_engine_initialization(self):
        """Test BenchmarkEngine initializes correctly"""
        engine = BenchmarkEngine()
        assert engine is not None

    def test_load_benchmark_config(self):
        """Test loading benchmark configuration"""
        engine = BenchmarkEngine()
        
        # Test with valid YAML structure
        config_data = {
            'name': 'Test Benchmark',
            'description': 'Test description',
            'version': '1.0.0',
            'models': ['gpt-4o-mini'],
            'tests': [
                {
                    'name': 'Test Case',
                    'prompt': 'Test prompt',
                    'expected_output': 'Expected output',
                    'max_tokens': 100,
                    'temperature': 0.3,
                    'tags': ['test'],
                    'weight': 1.0
                }
            ]
        }
        
        # This should not raise an error
        try:
            engine._validate_config(config_data)
        except Exception as e:
            pytest.fail(f"Config validation failed: {e}")

    def test_validate_config_missing_required(self):
        """Test config validation with missing required fields"""
        engine = BenchmarkEngine()
        
        config_data = {
            'name': 'Test Benchmark',
            # Missing required fields
        }
        
        with pytest.raises(ValueError):
            engine._validate_config(config_data)

    def test_validate_config_valid(self):
        """Test valid config validation"""
        engine = BenchmarkEngine()
        
        config_data = {
            'name': 'Test Benchmark',
            'description': 'Test description',
            'version': '1.0.0',
            'models': ['gpt-4o-mini'],
            'tests': [
                {
                    'name': 'Test Case',
                    'prompt': 'Test prompt',
                    'expected_output': 'Expected output',
                    'max_tokens': 100,
                    'temperature': 0.3,
                    'tags': ['test'],
                    'weight': 1.0
                }
            ]
        }
        
        # Should not raise an error
        engine._validate_config(config_data)

class TestBenchmarkResult:
    """Test benchmark result models"""

    def test_benchmark_result_creation(self):
        """Test creating BenchmarkResult"""
        result = BenchmarkResult(
            model="gpt-4o-mini",
            test_name="Test Case",
            prompt="Test prompt",
            response="Test response",
            latency_ms=1000,
            cost=0.001,
            success=True,
            quality_score=0.8,
            input_tokens=50,
            output_tokens=25
        )
        
        assert result.model == "gpt-4o-mini"
        assert result.test_name == "Test Case"
        assert result.latency_ms == 1000
        assert result.cost == 0.001
        assert result.success is True
        assert result.quality_score == 0.8

    def test_test_case_creation(self):
        """Test creating TestCase"""
        test_case = TestCase(
            name="Test Case",
            prompt="Test prompt",
            expected_output="Expected output",
            max_tokens=100,
            temperature=0.3,
            tags=["test"],
            weight=1.0
        )
        
        assert test_case.name == "Test Case"
        assert test_case.prompt == "Test prompt"
        assert test_case.max_tokens == 100
        assert test_case.temperature == 0.3
        assert test_case.tags == ["test"]
        assert test_case.weight == 1.0

class TestModelConfig:
    """Test model configuration"""

    def test_model_config_creation(self):
        """Test creating ModelConfig"""
        config = ModelConfig(
            name="gpt-4o-mini",
            provider="openai",
            input_cost_per_1m=0.15,
            output_cost_per_1m=0.6,
            max_tokens=128000,
            capabilities=["chat", "code"]
        )
        
        assert config.name == "gpt-4o-mini"
        assert config.provider == "openai"
        assert config.input_cost_per_1m == 0.15
        assert config.output_cost_per_1m == 0.6
        assert config.max_tokens == 128000
        assert config.capabilities == ["chat", "code"]

    def test_calculate_cost(self):
        """Test cost calculation"""
        config = ModelConfig(
            name="gpt-4o-mini",
            provider="openai",
            input_cost_per_1m=0.15,
            output_cost_per_1m=0.6,
            max_tokens=128000,
            capabilities=["chat", "code"]
        )
        
        # Test with 1000 input tokens and 500 output tokens
        cost = config.calculate_cost(1000, 500)
        expected_cost = (1000 * 0.15 / 1_000_000) + (500 * 0.6 / 1_000_000)
        
        assert abs(cost - expected_cost) < 0.000001
