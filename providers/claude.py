"""
Claude API provider implementation.

This module shows how to integrate with Anthropic's Claude API.
Students can use this as a reference for implementing other providers.
"""

from __future__ import annotations

import anthropic

from .base import Provider, Response, ToolCall
from tools.base import Tool


class ClaudeProvider:
    """
    Provider implementation for Anthropic's Claude API.

    Uses the official anthropic SDK to communicate with Claude models.
    """

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        """
        Initialize the Claude provider.

        Args:
            api_key: Your Anthropic API key
            model: Model to use (default: claude-sonnet-4-20250514)
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def chat(self, messages: list[dict], tools: list[Tool]) -> Response:
        """
        Send messages to Claude and get a response.

        This method:
        1. Converts our tool format to Claude's expected format
        2. Sends the request to the API
        3. Parses the response into our Response type
        """
        # Convert tools to Claude's format
        claude_tools = [self._convert_tool(tool) for tool in tools]

        # Convert messages to Claude's format
        claude_messages = self._convert_messages(messages)

        # Make the API call
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=claude_messages,
            tools=claude_tools,
        )

        # Parse the response
        return self._parse_response(response)

    def _convert_tool(self, tool: Tool) -> dict:
        """Convert a Tool to Claude's tool format."""
        return {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.get_schema(),
        }

    def _convert_messages(self, messages: list[dict]) -> list[dict]:
        """
        Convert our message format to Claude's format.

        Claude expects tool results in a specific format with content blocks.
        """
        claude_messages = []

        for msg in messages:
            if msg["role"] == "tool":
                # Claude expects tool results as user messages with tool_result content
                claude_messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": msg["tool_use_id"],
                            "content": msg["content"],
                        }
                    ],
                })
            elif msg["role"] == "assistant" and "tool_calls" in msg:
                # Convert assistant messages with tool calls
                content = []
                if msg.get("content"):
                    content.append({"type": "text", "text": msg["content"]})
                for tc in msg["tool_calls"]:
                    content.append({
                        "type": "tool_use",
                        "id": tc["id"],
                        "name": tc["name"],
                        "input": tc["parameters"],
                    })
                claude_messages.append({"role": "assistant", "content": content})
            else:
                claude_messages.append(msg)

        return claude_messages

    def _parse_response(self, response) -> Response:
        """Parse Claude's response into our Response type."""
        content = ""
        tool_calls = []

        for block in response.content:
            if block.type == "text":
                content = block.text
            elif block.type == "tool_use":
                tool_calls.append(
                    ToolCall(
                        name=block.name,
                        parameters=block.input,
                        id=block.id,
                    )
                )

        return Response(content=content, tool_calls=tool_calls)
