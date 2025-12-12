"""
LLM Client Module for TestGen AI.

This module provides a unified interface to interact with various LLM providers
(OpenAI, Anthropic, Gemini, Ollama) using LiteLLM.
"""

import os
from typing import Optional, Dict, Any, List
from enum import Enum

import litellm
from litellm import completion
from pydantic import BaseModel, Field

from testgen.config import config, LLMProvider


class LLMResponse(BaseModel):
    """Response from LLM with metadata."""
    
    content: str = Field(..., description="Generated text content")
    model: str = Field(..., description="Model that generated the response")
    provider: str = Field(..., description="Provider used")
    tokens_used: int = Field(0, description="Total tokens used")
    input_tokens: int = Field(0, description="Input tokens")
    output_tokens: int = Field(0, description="Output tokens")
    cost: float = Field(0.0, description="Estimated cost in USD")
    
    class Config:
        arbitrary_types_allowed = True


class LLMClient:
    """
    Unified LLM client supporting multiple providers.
    
    Uses LiteLLM to provide a consistent interface across:
    - OpenAI (GPT-3.5, GPT-4)
    - Anthropic (Claude)
    - Google (Gemini)
    - Ollama (local models)
    
    Example:
        client = LLMClient()
        response = client.generate("Write a test for this function")
        print(response.content)
    """
    
    def __init__(
        self,
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """
        Initialize LLM client.
        
        Args:
            provider: LLM provider to use (defaults to config)
            model: Specific model to use (defaults to config)
            api_key: API key (defaults to config-based key)
            temperature: Generation temperature (defaults to config)
            max_tokens: Maximum tokens to generate (defaults to config)
        """
        # Use provided values or fall back to config
        self.provider = provider or config.llm_provider
        self.model = model or config.llm_model
        self.temperature = temperature or config.llm_temperature
        self.max_tokens = max_tokens or config.max_context_tokens
        
        # Set up API key
        self._setup_api_key(api_key)
        
        # Configure LiteLLM
        self._configure_litellm()
        
        # Validate setup
        config.validate_api_keys()
    
    def _setup_api_key(self, api_key: Optional[str] = None) -> None:
        """Set up API key for the selected provider."""
        if api_key:
            # Use provided key
            self.api_key = api_key
        else:
            # Get from config
            self.api_key = config.get_api_key()
        
        # Set environment variables for LiteLLM
        if self.provider == LLMProvider.OPENAI and self.api_key:
            os.environ["OPENAI_API_KEY"] = self.api_key
        elif self.provider == LLMProvider.ANTHROPIC and self.api_key:
            os.environ["ANTHROPIC_API_KEY"] = self.api_key
        elif self.provider == LLMProvider.GEMINI and self.api_key:
            # For Google AI Studio (not Vertex AI)
            os.environ["GEMINI_API_KEY"] = self.api_key
            os.environ["GOOGLE_API_KEY"] = self.api_key  # LiteLLM also checks this
        # Ollama doesn't need API key
    
    def _configure_litellm(self) -> None:
        """Configure LiteLLM settings."""
        # Disable verbose logging in production
        litellm.set_verbose = False
        
        # Set telemetry (can be disabled for privacy)
        litellm.telemetry = False
        
        # Set timeout
        litellm.request_timeout = 60
    
    def _format_model_name(self) -> str:
        """
        Format model name for LiteLLM.
        
        LiteLLM uses specific prefixes for different providers:
        - OpenAI: "gpt-4", "gpt-3.5-turbo" (no prefix)
        - Anthropic: "claude-3-..." (no prefix)
        - Gemini: "gemini/gemini-1.5-flash" (needs gemini/ for Google AI Studio)
        - Ollama: "ollama/codellama:7b"
        """
        if self.provider == LLMProvider.GEMINI:
            # Gemini models need "gemini/" prefix for Google AI Studio
            if not self.model.startswith("gemini/"):
                return f"gemini/{self.model}"
        elif self.provider == LLMProvider.OLLAMA:
            # Ollama models need "ollama/" prefix
            if not self.model.startswith("ollama/"):
                return f"ollama/{self.model}"
        
        # OpenAI and Anthropic don't need prefixes
        return self.model
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
    ) -> LLMResponse:
        """
        Generate text completion from LLM.
        
        Args:
            prompt: The user prompt/instruction
            system_prompt: Optional system message
            temperature: Override default temperature
            max_tokens: Override default max tokens
            stop: Stop sequences for generation
            
        Returns:
            LLMResponse with generated content and metadata
            
        Raises:
            ValueError: If generation fails
        """
        # Use direct SDK for Gemini, LiteLLM for others
        if self.provider == LLMProvider.GEMINI:
            return self._generate_gemini(prompt, system_prompt, temperature, max_tokens)
        else:
            return self._generate_litellm(prompt, system_prompt, temperature, max_tokens, stop)
    
    def _generate_gemini(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate using Google GenAI SDK directly."""
        try:
            import google.generativeai as genai
            
            # Configure with API key
            genai.configure(api_key=self.api_key)
            
            # Create model - add "models/" prefix if not present
            model_name = self.model
            if not model_name.startswith("models/"):
                model_name = f"models/{model_name}"
            
            model = genai.GenerativeModel(model_name)
            
            # Build prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Configure generation
            generation_config = {
                "temperature": temperature or self.temperature,
                "max_output_tokens": max_tokens or self.max_tokens,
            }
            
            # Generate
            response = model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            # Extract content
            content = response.text
            
            # Estimate tokens (Gemini doesn't always provide usage)
            input_tokens = len(full_prompt.split()) * 1.3  # rough estimate
            output_tokens = len(content.split()) * 1.3
            
            return LLMResponse(
                content=content,
                model=self.model,
                provider=self.provider.value,
                tokens_used=int(input_tokens + output_tokens),
                input_tokens=int(input_tokens),
                output_tokens=int(output_tokens),
                cost=0.0  # Gemini is free
            )
            
        except Exception as e:
            raise ValueError(f"Gemini generation failed: {str(e)}") from e
    
    def _generate_litellm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
    ) -> LLMResponse:
        """Generate using LiteLLM for OpenAI/Claude/Ollama."""
        # Build messages
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Prepare parameters
        params = {
            "model": self._format_model_name(),
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }
        
        if stop:
            params["stop"] = stop
        
        try:
            # Call LiteLLM
            response = completion(**params)
            
            # Extract data
            content = response.choices[0].message.content
            usage = response.usage if hasattr(response, 'usage') else None
            
            # Build response
            return LLMResponse(
                content=content,
                model=self.model,
                provider=self.provider.value,
                tokens_used=usage.total_tokens if usage else 0,
                input_tokens=usage.prompt_tokens if usage else 0,
                output_tokens=usage.completion_tokens if usage else 0,
                cost=self._estimate_cost(usage) if usage else 0.0
            )
            
        except Exception as e:
            raise ValueError(f"LLM generation failed: {str(e)}") from e
    
    async def generate_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
    ) -> LLMResponse:
        """
        Async version of generate().
        
        Args:
            Same as generate()
            
        Returns:
            LLMResponse with generated content
        """
        # Build messages
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Prepare parameters
        params = {
            "model": self._format_model_name(),
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }
        
        if stop:
            params["stop"] = stop
        
        try:
            from litellm import acompletion
            
            # Call LiteLLM async
            response = await acompletion(**params)
            
            # Extract data
            content = response.choices[0].message.content
            usage = response.usage if hasattr(response, 'usage') else None
            
            # Build response
            return LLMResponse(
                content=content,
                model=self.model,
                provider=self.provider.value,
                tokens_used=usage.total_tokens if usage else 0,
                input_tokens=usage.prompt_tokens if usage else 0,
                output_tokens=usage.completion_tokens if usage else 0,
                cost=self._estimate_cost(usage) if usage else 0.0
            )
            
        except Exception as e:
            raise ValueError(f"LLM generation failed: {str(e)}") from e
    
    def _estimate_cost(self, usage: Any) -> float:
        """
        Estimate cost based on token usage.
        
        Rough estimates (per 1M tokens):
        - GPT-3.5-turbo: $0.5 input, $1.5 output
        - GPT-4-turbo: $10 input, $30 output
        - Claude Haiku: $0.25 input, $1.25 output
        - Claude Sonnet: $3 input, $15 output
        - Gemini Flash: FREE
        - Ollama: FREE
        """
        if not usage or not hasattr(usage, 'prompt_tokens'):
            return 0.0
        
        input_tokens = usage.prompt_tokens
        output_tokens = usage.completion_tokens
        
        # Cost per 1M tokens
        costs = {
            "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
            "gpt-4": {"input": 10, "output": 30},
            "gpt-4-turbo": {"input": 10, "output": 30},
            "claude-3-5-haiku": {"input": 0.25, "output": 1.25},
            "claude-3-5-sonnet": {"input": 3, "output": 15},
            "claude-3": {"input": 3, "output": 15},
            "gemini": {"input": 0, "output": 0},  # Free tier
            "ollama": {"input": 0, "output": 0},  # Local/free
        }
        
        # Find matching model
        model_lower = self.model.lower()
        cost_data = None
        
        for model_prefix, cost in costs.items():
            if model_prefix in model_lower:
                cost_data = cost
                break
        
        if not cost_data:
            return 0.0
        
        # Calculate cost (per million tokens)
        input_cost = (input_tokens / 1_000_000) * cost_data["input"]
        output_cost = (output_tokens / 1_000_000) * cost_data["output"]
        
        return round(input_cost + output_cost, 6)
    
    def test_connection(self) -> bool:
        """
        Test connection to LLM provider.
        
        Returns:
            True if connection works, False otherwise
        """
        try:
            response = self.generate(
                prompt="Say 'OK' if you can read this.",
                max_tokens=10
            )
            return len(response.content) > 0
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model configuration.
        
        Returns:
            Dictionary with model information
        """
        return {
            "provider": self.provider.value,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "has_api_key": self.api_key is not None,
        }


# Convenience instance with default configuration
llm_client = LLMClient()
