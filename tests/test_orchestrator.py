"""
Unit tests for IGRIS orchestrator and routing logic.
"""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from orchestrator import fast_route, CODE_KEYWORDS, NON_CODE_INDICATORS


class TestFastRouting:
    """Test heuristic-based routing."""
    
    def test_explicit_code_requests(self):
        assert fast_route("write a python script to sort a list") == "code"
        assert fast_route("debug this function") == "code"
        assert fast_route("implement a binary search algorithm") == "code"
        assert fast_route("fix the syntax error in this code") == "code"
    
    def test_explicit_general_requests(self):
        assert fast_route("explain what machine learning is") == "general"
        assert fast_route("what is the difference between TCP and UDP") == "general"
        assert fast_route("help me understand recursion") == "general"
        assert fast_route("describe how HTTP works") == "general"
    
    def test_ambiguous_requests(self):
        # Single code keyword without non-code indicator
        assert fast_route("something about python") == "ambiguous"
    
    def test_non_code_overrides_code(self):
        # Even with code keywords, explanation requests go to general
        assert fast_route("explain how python functions work") == "general"
        assert fast_route("what is a database index") == "general"
    
    def test_casual_chat(self):
        assert fast_route("hello") == "general"
        assert fast_route("how are you") == "general"
        assert fast_route("thanks for your help") == "general"


class TestKeywordSets:
    """Test keyword configuration."""
    
    def test_code_keywords_exist(self):
        assert len(CODE_KEYWORDS) > 10
        assert "code" in CODE_KEYWORDS
        assert "python" in CODE_KEYWORDS
        assert "debug" in CODE_KEYWORDS
    
    def test_non_code_indicators_exist(self):
        assert len(NON_CODE_INDICATORS) > 5
        assert "explain" in NON_CODE_INDICATORS
        assert "what is" in NON_CODE_INDICATORS


class TestModelConfig:
    """Test model configuration."""
    
    def test_required_models_configured(self):
        from base import MODELS
        assert "qwen" in MODELS
        assert "deepseek" in MODELS
    
    def test_model_urls_are_valid(self):
        from base import MODELS
        for name in ["qwen", "deepseek"]:
            config = MODELS[name]
            assert config.url.startswith("http://127.0.0.1:")
            assert "/completion" in config.url


class TestFallbackBehavior:
    """Test that ambiguous routes default safely."""
    
    def test_empty_input(self):
        assert fast_route("") == "general"
    
    def test_unknown_topic(self):
        assert fast_route("random gibberish xyz") == "general"
    
    def test_mixed_signals(self):
        # Non-code indicator should win
        result = fast_route("explain the code for sorting")
        assert result == "general"


class TestLogger:
    """Test logging infrastructure."""
    
    def test_log_dir_creation(self):
        from logger import ensure_log_dir, LOG_DIR
        ensure_log_dir()
        assert LOG_DIR.exists()
    
    def test_get_log_file_format(self):
        from logger import get_log_file
        from datetime import datetime
        log_file = get_log_file()
        today = datetime.now().strftime('%Y-%m-%d')
        assert today in str(log_file)
        assert str(log_file).endswith(".jsonl")
