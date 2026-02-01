"""
Read file tool - allows the agent to read file contents.
"""

from pathlib import Path

from .base import Tool


class ReadFileTool(Tool):
    """Tool for reading the contents of a file."""

    name = "read_file"
    description = "Read the contents of a file at the given path."

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file to read",
                }
            },
            "required": ["path"],
        }

    def execute(self, path: str) -> str:
        """Read and return the contents of the specified file."""
        try:
            file_path = Path(path)
            if not file_path.exists():
                return f"Error: File '{path}' does not exist"
            if not file_path.is_file():
                return f"Error: '{path}' is not a file"
            content = file_path.read_text()
            return content
        except PermissionError:
            return f"Error: Permission denied reading '{path}'"
        except Exception as e:
            return f"Error reading file: {e}"
