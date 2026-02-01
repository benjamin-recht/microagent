# microagent

A minimalist coding agent that exposes the agent loop to help understand how LLM-based agents work.

## What This Is

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

## License

MIT
