"""
Unit test to verify lazy initialization of LLMClient and prevent module-level import crashes.
"""
import os
import pytest
from testgen.config import config, LLMProvider


class TestLLMLazyInit:
    def test_import_without_api_key_does_not_crash(self, monkeypatch):
        """Verify that importing testgen.core.llm and testgen.manager does not crash when no API key is set."""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        # Force provider to GEMINI with no key
        monkeypatch.setattr(config, "gemini_api_key", None)
        monkeypatch.setattr(config, "llm_provider", LLMProvider.GEMINI)

        # Importing should succeed cleanly without raising ValueError
        import testgen.core.llm as llm_module
        from testgen.core.llm import LLMClient
        from testgen.manager import WorkflowManager

        assert LLMClient is not None
        assert WorkflowManager is not None

    def test_accessing_llm_client_without_key_raises_value_error(self, monkeypatch):
        """Verify that accessing llm_client lazily raises ValueError when API key is missing."""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.setattr(config, "gemini_api_key", None)
        monkeypatch.setattr(config, "llm_provider", LLMProvider.GEMINI)

        # Reset singleton cache for test
        import testgen.core.llm as llm_module
        llm_module._default_llm_client = None

        with pytest.raises(ValueError, match="Gemini API key not found"):
            _ = llm_module.llm_client
