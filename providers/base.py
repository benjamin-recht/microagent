"""
Base types and protocols for LLM providers.

This module defines the interface that any LLM provider must implement.
Students can create new providers (OpenAI, Ollama, etc.) by implementing
the Provider protocol.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from tools.base import Tool


@dataclass
class ToolCall:
    """Represents a single tool call requested by the LLM."""

    name: str  # Name of the tool to execute (e.g., "read_file")
    parameters: dict[str, Any]  # Arguments to pass to the tool
    id: str  # Unique ID for this tool call (used to match results)


@dataclass
class Response:
    """Response from an LLM provider."""

    content: str = ""  # Text content of the response
    tool_calls: list[ToolCall] = field(default_factory=list)  # Tools the LLM wants to use

    @property
    def is_final(self) -> bool:
        """Check if this is a final response (no more tool calls needed)."""
        return len(self.tool_calls) == 0


class Provider(Protocol):
    """
    Protocol defining the interface for LLM providers.

    To add a new provider (e.g., OpenAI), create a class that implements
    this protocol with a chat() method matching this signature.
    """

    def chat(self, messages: list[dict], tools: list["Tool"]) -> Response:
        """
        Send messages to the LLM and get a response.

        Args:
            messages: Conversation history in the format:
                      [{"role": "user"|"assistant"|"tool", "content": "..."}]
            tools: List of available tools the LLM can use

        Returns:
            Response object containing the LLM's reply and any tool calls
        """
        ...
