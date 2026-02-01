"""
Base class for tools.

Tools are actions the agent can take to interact with the environment.
Each tool has a name, description, and can be executed with parameters.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    """
    Abstract base class for all tools.

    To create a new tool:
    1. Inherit from this class
    2. Set the 'name' and 'description' class attributes
    3. Implement get_schema() to define the parameters
    4. Implement execute() to perform the action
    """

    name: str  # Unique identifier for the tool (e.g., "read_file")
    description: str  # Human-readable description of what the tool does

    @abstractmethod
    def get_schema(self) -> dict:
        """
        Return the JSON schema for this tool's parameters.

        The schema tells the LLM what parameters the tool accepts.
        Example:
            {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to read"}
                },
                "required": ["path"]
            }
        """
        pass

    @abstractmethod
    def execute(self, **params: Any) -> str:
        """
        Execute the tool with the given parameters.

        Args:
            **params: Parameters as defined by get_schema()

        Returns:
            A string describing the result (shown to the LLM)
        """
        pass
