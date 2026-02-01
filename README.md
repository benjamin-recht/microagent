# microagent

A minimalist coding agent that exposes the agent loop for teaching. Designed to help undergraduates understand how LLM-based agents work.

## What This Is

This is a simple, readable Python implementation of an LLM agent. It demonstrates the core **agent loop**:

```
perceive → think → act → observe → repeat
```

The agent receives a task, uses an LLM to decide what to do, executes tools, and continues until complete. All steps are displayed with colored output so you can see exactly what's happening.

## Installation

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-api-key
```

## Usage

```bash
python main.py "Create a file called hello.py that prints Hello World"
```

## Example Output

```
╭─ Task ──────────────────────────────────────────╮
│ Create a file called hello.py that prints      │
│ Hello World                                     │
╰─────────────────────────────────────────────────╯

╭─ LLM Request ───────────────────────────────────╮
│ {                                               │
│   "messages": [{"role": "user", "content":...}],│
│   "tools": ["read_file", "write_file", "shell"] │
│ }                                               │
╰─────────────────────────────────────────────────╯

⠋ Thinking...

╭─ LLM Response ──────────────────────────────────╮
│ {                                               │
│   "tool_calls": [{                              │
│     "name": "write_file",                       │
│     "parameters": {"path": "hello.py", ...}     │
│   }]                                            │
│ }                                               │
╰─────────────────────────────────────────────────╯

╭─ Tool Call ─────────────────────────────────────╮
│ write_file                                      │
│ path: "hello.py"                                │
│ content: "print(\"Hello World\")"               │
╰─────────────────────────────────────────────────╯

╭─ Result ────────────────────────────────────────╮
│ ✓ Wrote 20 bytes to hello.py                   │
╰─────────────────────────────────────────────────╯

╭─ Answer ────────────────────────────────────────╮
│ I've created hello.py. Run it with:            │
│ python hello.py                                 │
╰─────────────────────────────────────────────────╯
```

## Architecture

```
microagent/
├── main.py           # Entry point
├── agent.py          # Core agent loop (start here!)
├── display.py        # Colored terminal output
├── providers/
│   ├── base.py       # Provider protocol
│   └── claude.py     # Claude API implementation
└── tools/
    ├── base.py       # Tool base class
    ├── read_file.py  # Read file contents
    ├── write_file.py # Write/create files
    └── shell.py      # Execute shell commands
```

## The Agent Loop

The heart of this project is in `agent.py`. Here's the simplified loop:

```python
def run(self, task: str):
    messages = [{"role": "user", "content": task}]

    while True:
        # 1. THINK - Ask the LLM what to do
        response = self.provider.chat(messages, self.tools)

        # 2. CHECK - Is the task complete?
        if response.is_final:
            return response.content

        # 3. ACT - Execute tool calls
        for tool_call in response.tool_calls:
            result = self.execute_tool(tool_call)
            messages.append(tool_result)

        # 4. OBSERVE - Loop back with results
```

## Exercises for Students

1. **Add a new tool**: Create `tools/list_dir.py` that lists directory contents
2. **Add a new provider**: Implement `providers/openai.py` using the OpenAI API
3. **Add memory**: Modify the agent to remember previous conversations
4. **Add cost tracking**: Track and display API token usage
5. **Add streaming**: Show the LLM's response as it's generated

## Key Concepts

- **Provider**: Interface to an LLM (Claude, OpenAI, Ollama, etc.)
- **Tool**: An action the agent can take (read files, run commands, etc.)
- **Agent Loop**: The cycle of thinking, acting, and observing
- **Messages**: The conversation history sent to the LLM

## License

MIT
