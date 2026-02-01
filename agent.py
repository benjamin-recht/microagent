"""
The core agent loop - the heart of this teaching tool.

This module implements the classic agent loop:
    perceive → think → act → observe → repeat

The agent receives a task, uses an LLM to decide what to do,
executes tools as needed, and continues until the task is complete.
"""

from __future__ import annotations

from providers.base import Provider, Response, ToolCall
from tools.base import Tool
from display import Display


class Agent:
    """
    A simple agent that uses an LLM to complete tasks.

    The agent follows a loop:
    1. THINK - Ask the LLM what to do next
    2. CHECK - Is the task complete? If so, stop
    3. ACT - Execute any tool calls the LLM requested
    4. OBSERVE - Add results to conversation and loop back
    """

    def __init__(self, provider: Provider, tools: list[Tool]):
        """
        Initialize the agent.

        Args:
            provider: The LLM provider to use (e.g., ClaudeProvider)
            tools: List of tools the agent can use
        """
        self.provider = provider
        self.tools = tools
        self.display = Display()

        # Create a lookup dict for quick tool access
        self._tool_map = {tool.name: tool for tool in tools}

    def run(self, task: str) -> str:
        """
        Run the agent on a task until completion.

        Args:
            task: The user's task description

        Returns:
            The agent's final response
        """
        # Show the task to the user
        self.display.show_task(task)

        # Initialize the conversation with the user's task
        messages = [{"role": "user", "content": task}]

        # The main agent loop
        while True:
            # ============================================
            # STEP 1: THINK - Ask the LLM what to do next
            # ============================================
            # Show what we're sending to the LLM
            self.display.show_llm_request(messages, self.tools)

            self.display.show_thinking()

            try:
                response = self.provider.chat(messages, self.tools)
            except Exception as e:
                self.display.show_error(f"LLM error: {e}")
                return f"Error: {e}"

            self.display.hide_thinking()

            # Show what the LLM returned
            self.display.show_llm_response(response)

            # ============================================
            # STEP 2: CHECK - Is the task complete?
            # ============================================
            # If the LLM didn't request any tool calls, we're done
            if response.is_final:
                self.display.show_answer(response.content)
                return response.content

            # ============================================
            # STEP 3: ACT - Execute the tool calls
            # ============================================
            # Add the assistant's response to the conversation
            # (This preserves any text content plus the tool calls)
            messages.append({
                "role": "assistant",
                "content": response.content,
                "tool_calls": [
                    {"id": tc.id, "name": tc.name, "parameters": tc.parameters}
                    for tc in response.tool_calls
                ],
            })

            # Execute each tool call
            for tool_call in response.tool_calls:
                self.display.show_tool_call(tool_call)

                # Find and execute the tool
                result = self._execute_tool(tool_call)

                self.display.show_tool_result(result)

                # ============================================
                # STEP 4: OBSERVE - Add result to conversation
                # ============================================
                # The result becomes part of the conversation,
                # so the LLM can see what happened
                messages.append({
                    "role": "tool",
                    "tool_use_id": tool_call.id,
                    "content": result,
                })

            # Loop back to THINK with the new information

    def _execute_tool(self, tool_call: ToolCall) -> str:
        """
        Execute a single tool call.

        Args:
            tool_call: The tool call to execute

        Returns:
            The result as a string
        """
        tool = self._tool_map.get(tool_call.name)

        if tool is None:
            return f"Error: Unknown tool '{tool_call.name}'"

        try:
            return tool.execute(**tool_call.parameters)
        except TypeError as e:
            return f"Error: Invalid parameters for {tool_call.name}: {e}"
        except Exception as e:
            return f"Error executing {tool_call.name}: {e}"
