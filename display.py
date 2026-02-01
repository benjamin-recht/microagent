"""
Terminal display using the rich library.

This module handles all the colored output to make the agent's
behavior visible and easy to follow.

Color scheme:
- Blue: User input / task
- Yellow: Agent thinking indicator
- Cyan: Tool calls (name + parameters)
- Green: Tool results
- White: Final answer
- Red: Errors
"""

from __future__ import annotations

import json

from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from rich.syntax import Syntax

from providers.base import ToolCall, Response
from transcript import Transcript


class Display:
    """Handles all terminal output with colors and formatting."""

    def __init__(self, transcript_path: str | None = None):
        self.console = Console()
        self._live = None
        self.transcript = Transcript(transcript_path) if transcript_path else None

    def show_task(self, task: str) -> None:
        """Display the user's task in a blue panel."""
        self.console.print(Panel(task, title="Task", border_style="blue"))
        self.console.print()
        if self.transcript:
            self.transcript.write_task(task)

    def show_thinking(self) -> None:
        """Show a spinner while the agent is thinking."""
        self._live = Live(
            Spinner("dots", text="Thinking...", style="yellow"),
            console=self.console,
            refresh_per_second=10,
        )
        self._live.start()

    def hide_thinking(self) -> None:
        """Hide the thinking spinner."""
        if self._live:
            self._live.stop()
            self._live = None

    def show_llm_request(self, messages: list[dict], tools: list) -> None:
        """Display what we're sending to the LLM."""
        # Format messages for display
        formatted_messages = []
        for msg in messages:
            formatted_msg = {"role": msg["role"]}
            if "content" in msg and msg["content"]:
                content = msg["content"]
                # Truncate long content
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

        # Format tools list (just names)
        tool_names = [t.name for t in tools]

        request_info = {
            "messages": formatted_messages,
            "tools": tool_names,
        }

        json_str = json.dumps(request_info, indent=2)
        syntax = Syntax(json_str, "json", theme="monokai", word_wrap=True)
        self.console.print(Panel(syntax, title="LLM Request", border_style="yellow"))
        if self.transcript:
            self.transcript.write_llm_request(messages, tools)

    def show_llm_response(self, response: Response) -> None:
        """Display what the LLM returned."""
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
        syntax = Syntax(json_str, "json", theme="monokai", word_wrap=True)
        self.console.print(Panel(syntax, title="LLM Response", border_style="magenta"))
        self.console.print()
        if self.transcript:
            self.transcript.write_llm_response(response)

    def show_tool_call(self, tool_call: ToolCall) -> None:
        """Display a tool call with its parameters."""
        self.hide_thinking()

        # Format parameters as readable key-value pairs
        params_lines = []
        for key, value in tool_call.parameters.items():
            # For long strings, show preview
            if isinstance(value, str) and len(value) > 50:
                display_value = json.dumps(value[:50] + "...")
            else:
                display_value = json.dumps(value)
            params_lines.append(f"{key}: {display_value}")

        content = tool_call.name + "\n" + "\n".join(params_lines)
        self.console.print(Panel(content, title="Tool Call", border_style="cyan"))
        if self.transcript:
            self.transcript.write_tool_call(tool_call)

    def show_tool_result(self, result: str) -> None:
        """Display the result from a tool execution."""
        # Truncate very long results
        if len(result) > 500:
            display_result = result[:500] + "\n... (truncated)"
        else:
            display_result = result

        self.console.print(Panel(display_result, title="Result", border_style="green"))
        self.console.print()
        if self.transcript:
            self.transcript.write_tool_result(result)

    def show_answer(self, answer: str) -> None:
        """Display the agent's final answer."""
        self.hide_thinking()
        self.console.print(Panel(answer, title="Answer", border_style="white"))
        if self.transcript:
            self.transcript.write_answer(answer)
            self.transcript.save()

    def show_error(self, error: str) -> None:
        """Display an error message."""
        self.hide_thinking()
        self.console.print(Panel(error, title="Error", border_style="red"))
        if self.transcript:
            self.transcript.write_error(error)
            self.transcript.save()
