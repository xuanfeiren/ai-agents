# 🤖 Coding Agent

A CLI-based coding assistant — built for the *Build a Coding Agent* assignment.  
Powered by [litellm](https://github.com/BerriAI/litellm), it supports any LLM provider (Anthropic, OpenAI, Gemini, Ollama, Groq, and more) through a single unified interface, with **no agentic frameworks** — only raw LLM API calls.

---

## How It Works

The agent implements a standard **tool-calling loop**:

1. User types a request at the prompt.
2. The agent sends the conversation history + available tools to the LLM via `litellm.completion()`.
3. If the model requests tool calls (`finish_reason == "tool_calls"`), the agent executes each tool and appends the results back into the conversation.
4. Steps 2–3 repeat until the model returns a final text response with no tool calls.
5. The response is rendered as Markdown in the terminal.

All LLM communication goes through **litellm** (a thin, provider-agnostic wrapper over raw HTTP calls) — no LangChain, CrewAI, Strands, or similar frameworks are used.

---

## Features

- **Provider-agnostic** — switch models with a single `--model` flag (Anthropic, OpenAI, Gemini, Groq, Ollama, …)
- **File tools** — read, write, create files and directories
- **Shell execution** — run bash commands to install packages, execute scripts, run tests, use git
- **Search** — find files by name pattern or grep for text inside files
- **Conversation memory** — full multi-turn context within a session
- **Rich CLI** — animated spinner while thinking, markdown rendering, colour-coded tool calls, clean prompts

---

## Installation

```bash
cd coding_agent
pip install -r requirements.txt
```

**Dependencies** (`requirements.txt`):
```
litellm>=1.40.0
rich>=13.7.0
```

---

## Configuration

Set the API key for your chosen provider as an environment variable:

| Provider  | Environment Variable  |
|-----------|-----------------------|
| Anthropic | `ANTHROPIC_API_KEY`   |
| OpenAI    | `OPENAI_API_KEY`      |
| Gemini    | `GEMINI_API_KEY`      |
| Groq      | `GROQ_API_KEY`        |
| Ollama    | *(no key needed)*     |

```bash
export ANTHROPIC_API_KEY=sk-ant-...
# or
export OPENAI_API_KEY=sk-...
```

---

## Usage

```bash
# Default model (claude-3-5-sonnet-20241022), current directory
python main.py

# Choose a different model
python main.py --model gpt-4o
python main.py --model gemini/gemini-2.0-flash
python main.py --model ollama/llama3

# Set the working directory the agent operates in
python main.py --cwd /path/to/your/project

# Combine flags
python main.py --model gpt-4o --cwd ~/projects/my-app
```

### In-session commands

| Command           | Description                |
|-------------------|----------------------------|
| `/clear` `/reset` | Clear conversation history |
| `/help`           | Show available commands     |
| `exit` / `quit`   | Exit the agent             |

---

## Supported Models (litellm strings)

```
# Anthropic
claude-3-5-sonnet-20241022
claude-3-opus-20240229
claude-3-haiku-20240307

# OpenAI
gpt-4o
gpt-4o-mini
o1-preview

# Google
gemini/gemini-1.5-pro
gemini/gemini-2.0-flash
gemini/gemini-2.5-flash-lite

# Groq (fast inference)
groq/llama-3.1-70b-versatile
groq/mixtral-8x7b-32768

# Ollama (local, no key required)
ollama/llama3
ollama/codellama
ollama/deepseek-coder
```

Full provider list: https://docs.litellm.ai/docs/providers

---

## Available Tools

| Tool               | Description                                        |
|--------------------|----------------------------------------------------|
| `read_file`        | Read contents of any file                         |
| `write_file`       | Create or overwrite a file                        |
| `create_directory` | Create a directory (including parents)            |
| `list_directory`   | List directory contents with sizes                |
| `execute_bash`     | Run a shell command — stdout + stderr + exit code |
| `search_files`     | Find files by glob pattern (e.g. `*.py`)          |
| `grep_search`      | Search text/regex patterns inside files           |

---

## Project Structure

```
coding_agent/
├── main.py          # CLI entry point & argument parsing
├── agent.py         # Agent loop, LLM calls via litellm, rich display
├── tools.py         # Tool implementations + OpenAI-format definitions
├── requirements.txt
├── README.md
└── example/
    └── snake/       # Example project built entirely by this agent
        ├── snake_game.py
        └── README.md
```

---

## Example: Snake Game (built by this agent)

Everything inside `example/snake/` was written by this coding agent in a single session using `gemini/gemini-2.5-flash-lite`. No code was written by hand.

**Prompt given to the agent:**
> *"Write a Snake game in Python using pygame. The snake should grow when it eats food, and the game should end when the snake hits a wall or itself. Show the score on screen."*

The agent then autonomously:
1. Planned the implementation
2. Used `write_file` to create `snake_game.py`
3. Used `execute_bash` to run `pip install pygame`
4. Reorganised the files into `example/snake/` via `create_directory` + `write_file`
5. Wrote a full `README.md` for the game — including multiple food types (regular, bonus, bad) that it added unprompted as improvements

**To run the snake game:**
```bash
pip install pygame
python example/snake/snake_game.py
```

Controls: arrow keys to move · **R** to restart · **Q** to quit after game over.

---
