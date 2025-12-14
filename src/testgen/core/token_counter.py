"""
Token Counting and Cost Estimation for TestGen AI.

This module handles token counting, cost estimation, and context management
for LLM API calls.
"""

from typing import Optional, Dict, Tuple
from dataclasses import dataclass
import tiktoken


@dataclass
class TokenEstimate:
    """Token count estimation result."""
    
    prompt_tokens: int
    estimated_completion_tokens: int
    total_tokens: int
    estimated_cost: float
    within_limit: bool
    model: str
    warning: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation."""
        status = "[OK]" if self.within_limit else "[WARNING]"
        return (
            f"{status} Tokens: {self.total_tokens} "
            f"(prompt: {self.prompt_tokens}, est. completion: {self.estimated_completion_tokens}) "
            f"Cost: ${self.estimated_cost:.4f}"
        )


class TokenCounter:
    """
    Counts tokens and estimates costs for LLM API calls.
    
    Implements Task 43 requirements:
    - Estimate tokens before API call
    - Warn if context too large
    - Implement context truncation if needed
    
    Example:
        >>> counter = TokenCounter(model="gpt-4")
        >>> estimate = counter.count_tokens(prompt_text)
        >>> if not estimate.within_limit:
        ...     print(estimate.warning)
    """
    
    # Token limits per model
    MODEL_LIMITS = {
        "gpt-4": 8192,
        "gpt-4-32k": 32768,
        "gpt-3.5-turbo": 4096,
        "gpt-3.5-turbo-16k": 16384,
        "gemini-pro": 30720,  # 30k tokens
        "gemini-1.5-pro": 1000000,  # 1M tokens
        "gemini-2.0-flash-exp": 1000000,
        "gemini-2.5-flash": 1000000,
        "claude-3-opus": 200000,
        "claude-3-sonnet": 200000,
        "claude-3-haiku": 200000,
    }
    
    # Cost per 1K tokens (approximate, as of Dec 2024)
    MODEL_COSTS = {
        "gpt-4": {"prompt": 0.03, "completion": 0.06},
        "gpt-4-32k": {"prompt": 0.06, "completion": 0.12},
        "gpt-3.5-turbo": {"prompt": 0.001, "completion": 0.002},
        "gpt-3.5-turbo-16k": {"prompt": 0.003, "completion": 0.004},
        "gemini-pro": {"prompt": 0.0, "completion": 0.0},  # Free tier
        "gemini-1.5-pro": {"prompt": 0.00125, "completion": 0.005},
        "gemini-2.0-flash-exp": {"prompt": 0.0, "completion": 0.0},  # Free during preview
        "gemini-2.5-flash": {"prompt": 0.0, "completion": 0.0},  # Free tier
        "claude-3-opus": {"prompt": 0.015, "completion": 0.075},
        "claude-3-sonnet": {"prompt": 0.003, "completion": 0.015},
        "claude-3-haiku": {"prompt": 0.00025, "completion": 0.00125},
    }
    
    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        safety_margin: float = 0.9
    ):
        """
        Initialize token counter.
        
        Args:
            model: LLM model name
            safety_margin: Use 90% of limit to leave room for completion
        """
        self.model = model
        self.safety_margin = safety_margin
        self.limit = self.MODEL_LIMITS.get(model, 8192)
        
        # Try to load tokenizer for accurate counting
        try:
            # For OpenAI models
            if model.startswith("gpt"):
                self.tokenizer = tiktoken.encoding_for_model(model)
            else:
                # Use cl100k_base as fallback (GPT-4 encoding)
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except:
            self.tokenizer = None
    
    def count_tokens(
        self,
        text: str,
        expected_completion_tokens: int = 1000
    ) -> TokenEstimate:
        """
        Count tokens in text (Task 43 requirement).
        
        Args:
            text: Text to count tokens for
            expected_completion_tokens: Expected response length
            
        Returns:
            TokenEstimate with count and cost
            
        Example:
            >>> counter = TokenCounter("gpt-4")
            >>> estimate = counter.count_tokens(prompt)
            >>> print(f"Tokens: {estimate.total_tokens}")
        """
        # Count prompt tokens
        if self.tokenizer:
            prompt_tokens = len(self.tokenizer.encode(text))
        else:
            # Rough estimate: ~4 chars per token
            prompt_tokens = len(text) // 4
        
        total_tokens = prompt_tokens + expected_completion_tokens
        
        # Check if within limit
        safe_limit = int(self.limit * self.safety_margin)
        within_limit = total_tokens <= safe_limit
        
        # Calculate cost
        cost = self._calculate_cost(prompt_tokens, expected_completion_tokens)
        
        # Generate warning if needed
        warning = None
        if not within_limit:
            warning = (
                f"Context too large! {total_tokens} tokens exceeds "
                f"safe limit of {safe_limit} (max: {self.limit}). "
                f"Consider truncation."
            )
        elif total_tokens > safe_limit * 0.8:
            warning = (
                f"Context approaching limit: {total_tokens}/{safe_limit} tokens. "
                f"May want to optimize."
            )
        
        return TokenEstimate(
            prompt_tokens=prompt_tokens,
            estimated_completion_tokens=expected_completion_tokens,
            total_tokens=total_tokens,
            estimated_cost=cost,
            within_limit=within_limit,
            model=self.model,
            warning=warning
        )
    
    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Calculate estimated cost.
        
        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            
        Returns:
            Estimated cost in USD
        """
        costs = self.MODEL_COSTS.get(self.model, {"prompt": 0.0, "completion": 0.0})
        
        prompt_cost = (prompt_tokens / 1000) * costs["prompt"]
        completion_cost = (completion_tokens / 1000) * costs["completion"]
        
        return prompt_cost + completion_cost
    
    def truncate_to_limit(
        self,
        text: str,
        preserve_end: bool = False
    ) -> str:
        """
        Truncate text to fit within token limit (Task 43 requirement).
        
        Args:
            text: Text to truncate
            preserve_end: If True, keep end of text instead of beginning
            
        Returns:
            Truncated text
            
        Example:
            >>> counter = TokenCounter("gpt-4")
            >>> truncated = counter.truncate_to_limit(long_text)
        """
        estimate = self.count_tokens(text)
        
        if estimate.within_limit:
            return text
        
        # Calculate how much to keep
        safe_limit = int(self.limit * self.safety_margin)
        reduction_ratio = safe_limit / estimate.prompt_tokens
        
        if self.tokenizer:
            # Use tokenizer for accurate truncation
            tokens = self.tokenizer.encode(text)
            target_tokens = int(len(tokens) * reduction_ratio)
            
            if preserve_end:
                tokens = tokens[-target_tokens:]
            else:
                tokens = tokens[:target_tokens]
            
            return self.tokenizer.decode(tokens)
        else:
            # Rough truncation by characters
            target_chars = int(len(text) * reduction_ratio)
            
            if preserve_end:
                return "..." + text[-target_chars:]
            else:
                return text[:target_chars] + "..."
    
    def estimate_batch_cost(
        self,
        prompts: list[str],
        expected_completion_per_prompt: int = 1000
    ) -> Dict[str, any]:
        """
        Estimate cost for batch of prompts.
        
        Args:
            prompts: List of prompt texts
            expected_completion_per_prompt: Expected tokens per response
            
        Returns:
            Dictionary with cost statistics
        """
        estimates = [
            self.count_tokens(p, expected_completion_per_prompt)
            for p in prompts
        ]
        
        total_cost = sum(e.estimated_cost for e in estimates)
        total_tokens = sum(e.total_tokens for e in estimates)
        over_limit = sum(1 for e in estimates if not e.within_limit)
        
        return {
            "batch_size": len(prompts),
            "total_cost": total_cost,
            "avg_cost_per_prompt": total_cost / len(prompts) if prompts else 0,
            "total_tokens": total_tokens,
            "avg_tokens_per_prompt": total_tokens / len(prompts) if prompts else 0,
            "prompts_over_limit": over_limit,
            "model": self.model
        }
    
    def get_model_info(self) -> Dict[str, any]:
        """
        Get information about current model.
        
        Returns:
            Model information dictionary
        """
        costs = self.MODEL_COSTS.get(self.model, {"prompt": 0.0, "completion": 0.0})
        
        return {
            "model": self.model,
            "token_limit": self.limit,
            "safe_limit": int(self.limit * self.safety_margin),
            "cost_per_1k_prompt": costs["prompt"],
            "cost_per_1k_completion": costs["completion"],
            "is_free": costs["prompt"] == 0.0 and costs["completion"] == 0.0
        }


def estimate_tokens(
    text: str,
    model: str = "gemini-2.5-flash"
) -> TokenEstimate:
    """
    Quick function to estimate tokens.
    
    Args:
        text: Text to estimate
        model: Model name
        
    Returns:
        TokenEstimate
        
    Example:
        >>> est = estimate_tokens(my_prompt, "gpt-4")
        >>> print(f"Cost: ${est.estimated_cost:.4f}")
    """
    counter = TokenCounter(model=model)
    return counter.count_tokens(text)
