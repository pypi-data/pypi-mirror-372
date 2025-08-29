"""
Base model class for NovaEval.

This module defines the abstract base class for all model implementations.
"""

import functools
import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, Union

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create module-level logger
logger = logging.getLogger(__name__)

NOVEUM_TRACE_AVAILABLE = False


# Fallback implementation that mimics trace_llm decorator signature but doesn't use tracing params
# The noqa: ARG001 directives are justified here because this function maintains interface compatibility
# with the real trace_llm decorator while providing a no-op implementation when tracing is unavailable
def _trace_llm_noop(
    func: Optional[Callable] = None,
    *,
    name: Optional[str] = None,  # noqa: ARG001
    provider: Optional[str] = None,  # noqa: ARG001
    capture_prompts: bool = True,  # noqa: ARG001
    capture_completions: bool = True,  # noqa: ARG001
    capture_tokens: bool = True,  # noqa: ARG001
    estimate_costs: bool = True,  # noqa: ARG001
    redact_pii: bool = False,  # noqa: ARG001
    metadata: Optional[dict[str, Any]] = None,  # noqa: ARG001
    tags: Optional[dict[str, str]] = None,  # noqa: ARG001
    **kwargs: Any,  # noqa: ARG001
) -> Any:
    # runtime no-op that behaves like the real decorator factory
    if func is None:
        # Called as @trace_llm(...) - return a decorator
        def deco(f: Callable) -> Callable:
            return functools.wraps(f)(lambda *args, **kwargs: f(*args, **kwargs))

        return deco
    # Called as @trace_llm - return the function unchanged
    return func


try:
    from noveum_trace import trace_llm  # types come from stub

    NOVEUM_TRACE_AVAILABLE = True
except ImportError:
    trace_llm = _trace_llm_noop  # type: ignore[assignment]


class BaseModel(ABC):
    """
    Abstract base class for all model implementations.

    This class defines the interface that all models must implement.
    """

    def __init__(
        self,
        name: str,
        model_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs: Any,
    ):
        """
        Initialize the model.

        Args:
            name: Human-readable name for this model instance
            model_name: Specific model identifier (e.g., "gpt-4", "claude-3-opus")
            api_key: API key for authentication
            base_url: Base URL for API requests
            **kwargs: Additional model-specific parameters
        """
        self.name = name
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self.kwargs = kwargs

        # Statistics tracking
        self.total_requests = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.errors: list[str] = []

        if os.getenv("NOVEUM_API_KEY"):
            # if ENABLE_TRACING is set to true or unset, we trace, we stop tracing only if set to False
            # for starting tracing, we do this - get the variables from the env
            enable_tracing = os.getenv("ENABLE_TRACING", "true").lower()
            if enable_tracing != "false":
                try:
                    import noveum_trace

                    noveum_trace.init(
                        api_key=os.getenv("NOVEUM_API_KEY"),
                        project=os.getenv("NOVEUM_PROJECT", "example-project"),
                        environment=os.getenv("NOVEUM_ENVIRONMENT", "development"),
                    )
                    logger.info("Noveum tracing initialized successfully")
                except ImportError:
                    logger.warning("noveum_trace not available, tracing disabled")
                except Exception as e:
                    logger.error(f"Failed to initialize Noveum tracing: {e}")

    @abstractmethod
    @trace_llm
    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop: Optional[Union[str, list[str]]] = None,
        **kwargs: Any,
    ) -> str:
        """
        Generate text from the model.

        Args:
            prompt: Input prompt for the model
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            stop: Stop sequences for generation
            **kwargs: Additional generation parameters

        Returns:
            Generated text response
        """
        pass

    @abstractmethod
    def generate_batch(
        self,
        prompts: list[str],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop: Optional[Union[str, list[str]]] = None,
        **kwargs: Any,
    ) -> list[str]:
        """
        Generate text for multiple prompts in batch.

        Args:
            prompts: List of input prompts
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            stop: Stop sequences for generation
            **kwargs: Additional generation parameters

        Returns:
            List of generated text responses
        """
        pass

    def get_info(self) -> dict[str, Any]:
        """
        Get information about the model.

        Returns:
            Dictionary containing model metadata
        """
        return {
            "name": self.name,
            "model_name": self.model_name,
            "type": self.__class__.__name__,
            "provider": self.get_provider(),
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "error_count": len(self.errors),
        }

    @abstractmethod
    def get_provider(self) -> str:
        """
        Get the provider name for this model.

        Returns:
            Provider name (e.g., "openai", "anthropic")
        """
        pass

    def validate_connection(self) -> bool:
        """
        Validate that the model can be accessed.

        Returns:
            True if connection is valid, False otherwise
        """
        try:
            # Try a simple generation to test connectivity
            response = self.generate("Hello", max_tokens=1)
            return response is not None
        except Exception as e:
            self.errors.append(f"Connection validation failed: {e}")
            return False

    def estimate_cost(self, prompt: str, response: str = "") -> float:
        """
        Estimate the cost for a generation request.

        Args:
            prompt: Input prompt
            response: Generated response

        Returns:
            Estimated cost in USD
        """
        # Default implementation returns 0
        # Subclasses should implement provider-specific cost calculation
        return 0.0

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        # Simple approximation: 1 token ≈ 4 characters
        # Subclasses should implement more accurate token counting
        return len(text) // 4

    def _track_request(
        self, prompt: str, response: str, tokens_used: int = 0, cost: float = 0.0
    ) -> None:
        """
        Track request statistics.

        Args:
            prompt: Input prompt
            response: Generated response
            tokens_used: Number of tokens used
            cost: Cost of the request
        """
        self.total_requests += 1
        self.total_tokens += tokens_used
        self.total_cost += cost

    def _handle_error(self, error: Exception, context: str = "") -> None:
        """
        Handle and log errors.

        Args:
            error: The exception that occurred
            context: Additional context about the error
        """
        logger.error("Error: %s", error)
        error_msg = f"{context}: {error!s}" if context else str(error)
        self.errors.append(error_msg)

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "BaseModel":
        """
        Create a model from configuration.

        Args:
            config: Configuration dictionary

        Returns:
            Configured model instance
        """
        return cls(**config)

    def __str__(self) -> str:
        """String representation of the model."""
        return (
            f"{self.__class__.__name__}(name='{self.name}', model='{self.model_name}')"
        )

    def __repr__(self) -> str:
        """Detailed string representation of the model."""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"model_name='{self.model_name}', "
            f"provider='{self.get_provider()}'"
            f")"
        )
