"""
Write file tool - allows the agent to create or overwrite files.
"""

from pathlib import Path

from .base import Tool


class WriteFileTool(Tool):
    """Tool for writing content to a file."""

    name = "write_file"
    description = "Write content to a file at the given path. Creates the file if it doesn't exist, or overwrites if it does."

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file to write",
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file",
                },
            },
            "required": ["path", "content"],
        }

    def execute(self, path: str, content: str) -> str:
        """Write content to the specified file."""
        try:
            file_path = Path(path)
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            return f"✓ Wrote {len(content)} bytes to {path}"
        except PermissionError:
            return f"Error: Permission denied writing to '{path}'"
        except Exception as e:
            return f"Error writing file: {e}"
