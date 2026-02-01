"""
Transcript writer for saving agent sessions to file.

Writes the actual messages sent to the LLM and responses received,
formatted cleanly without terminal colors or boxes.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from providers.base import ToolCall, Response


class Transcript:
    """Writes agent activity to a file for sharing."""

    def __init__(self, output_path: str):
        """
        Initialize the transcript writer.

        Args:
            output_path: Path to write the transcript (.md or .txt)
        """
        self.path = Path(output_path)
        self.is_markdown = self.path.suffix.lower() == ".md"
        self._lines: list[str] = []

        # Write header
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.is_markdown:
            self._lines.append(f"# Agent Transcript")
            self._lines.append(f"*Generated: {timestamp}*")
            self._lines.append("")
        else:
            self._lines.append("AGENT TRANSCRIPT")
            self._lines.append(f"Generated: {timestamp}")
            self._lines.append("=" * 60)
            self._lines.append("")

    def write_task(self, task: str) -> None:
        """Record the user's task."""
        if self.is_markdown:
            self._lines.append("## Task")
            self._lines.append("")
            self._lines.append(task)
            self._lines.append("")
        else:
            self._lines.append("TASK")
            self._lines.append("-" * 60)
            self._lines.append(task)
            self._lines.append("")

    def write_llm_request(self, messages: list[dict], tools: list) -> None:
        """Record the actual messages sent to the LLM."""
        # Build the same request info as display.py
        formatted_messages = []
        for msg in messages:
            formatted_msg = {"role": msg["role"]}
            if "content" in msg and msg["content"]:
                content = msg["content"]
                if isinstance(content, str) and len(content) > 200:
                    formatted_msg["content"] = content[:200] + "..."
                else:
                    formatted_msg["content"] = content
            if "tool_calls" in msg:
                formatted_msg["tool_calls"] = [
                    {"name": tc["name"], "id": tc["id"][:8] + "..."}
                    for tc in msg["tool_calls"]
                ]
            if "tool_use_id" in msg:
                formatted_msg["tool_use_id"] = msg["tool_use_id"][:8] + "..."
            formatted_messages.append(formatted_msg)

        tool_names = [t.name for t in tools]

        request_info = {
            "messages": formatted_messages,
            "tools": tool_names,
        }

        json_str = json.dumps(request_info, indent=2)

        if self.is_markdown:
            self._lines.append("## LLM Request")
            self._lines.append("")
            self._lines.append("```json")
            self._lines.append(json_str)
            self._lines.append("```")
            self._lines.append("")
        else:
            self._lines.append("LLM REQUEST")
            self._lines.append("-" * 60)
            self._lines.append(json_str)
            self._lines.append("")

    def write_llm_response(self, response: Response) -> None:
        """Record the actual response from the LLM."""
        response_info = {}

        if response.content:
            content = response.content
            if len(content) > 300:
                response_info["content"] = content[:300] + "..."
            else:
                response_info["content"] = content

        if response.tool_calls:
            response_info["tool_calls"] = [
                {
                    "name": tc.name,
                    "parameters": tc.parameters,
                    "id": tc.id[:8] + "...",
                }
                for tc in response.tool_calls
            ]

        if response.is_final:
            response_info["is_final"] = True

        json_str = json.dumps(response_info, indent=2)

        if self.is_markdown:
            self._lines.append("## LLM Response")
            self._lines.append("")
            self._lines.append("```json")
            self._lines.append(json_str)
            self._lines.append("```")
            self._lines.append("")
        else:
            self._lines.append("LLM RESPONSE")
            self._lines.append("-" * 60)
            self._lines.append(json_str)
            self._lines.append("")

    def write_tool_call(self, tool_call: ToolCall) -> None:
        """Record a tool being called."""
        # Format parameters as key: value pairs like display.py
        params_lines = []
        for key, value in tool_call.parameters.items():
            if isinstance(value, str) and len(value) > 50:
                display_value = json.dumps(value[:50] + "...")
            else:
                display_value = json.dumps(value)
            params_lines.append(f"{key}: {display_value}")

        if self.is_markdown:
            self._lines.append(f"## Tool Call")
            self._lines.append("")
            self._lines.append(f"**{tool_call.name}**")
            self._lines.append("")
            for line in params_lines:
                self._lines.append(line)
            self._lines.append("")
        else:
            self._lines.append("TOOL CALL")
            self._lines.append("-" * 60)
            self._lines.append(tool_call.name)
            for line in params_lines:
                self._lines.append(line)
            self._lines.append("")

    def write_tool_result(self, result: str) -> None:
        """Record the result of a tool execution."""
        if len(result) > 500:
            display_result = result[:500] + "\n... (truncated)"
        else:
            display_result = result

        if self.is_markdown:
            self._lines.append("## Result")
            self._lines.append("")
            self._lines.append("```")
            self._lines.append(display_result)
            self._lines.append("```")
            self._lines.append("")
        else:
            self._lines.append("RESULT")
            self._lines.append("-" * 60)
            self._lines.append(display_result)
            self._lines.append("")

    def write_answer(self, answer: str) -> None:
        """Record the agent's final answer."""
        if self.is_markdown:
            self._lines.append("## Answer")
            self._lines.append("")
            self._lines.append(answer)
            self._lines.append("")
        else:
            self._lines.append("ANSWER")
            self._lines.append("-" * 60)
            self._lines.append(answer)
            self._lines.append("")

    def write_error(self, error: str) -> None:
        """Record an error."""
        if self.is_markdown:
            self._lines.append("## Error")
            self._lines.append("")
            self._lines.append(error)
            self._lines.append("")
        else:
            self._lines.append("ERROR")
            self._lines.append("-" * 60)
            self._lines.append(error)
            self._lines.append("")

    def save(self) -> None:
        """Write the transcript to disk."""
        self.path.write_text("\n".join(self._lines))
