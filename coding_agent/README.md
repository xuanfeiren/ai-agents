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

Everything inside `example/snake/` was produced entirely through a multi-turn conversation with this coding agent using `gemini/gemini-2.5-flash-lite`. No code was written by hand.

### Turn-by-turn session

**Turn 1 — Initial build**
> *"Write a Snake game in Python using pygame. The snake should grow when it eats food, and the game should end when the snake hits a wall or itself. Show the score on screen."*

The agent planned the implementation, wrote `snake_game.py` (~160 lines), ran `pip install pygame` via `execute_bash`, reorganised files into `example/snake/` using `create_directory` + `write_file`, and added multiple food types (🍎 regular, ⭐ bonus, 💜 bad) unprompted as an improvement.

---

**Turn 2 — Bug fix: restart not working**
> *"press R but didn't restart"*

The agent read the source code, diagnosed that `game_over_screen()` returned correctly but `main()` had no outer loop to restart from, then rewrote the control flow: `game_over_screen()` now returns `True`/`False`, and `main()` wraps everything in a `while True` outer loop that re-initialises game state on restart.

---

**Turn 3 — Feature: multiple simultaneous food items**
> *"I want to add more features to this game, like there can be multiple and many food options at the same time"*

The agent refactored the food system from single variables to a `foods` list of dicts, introduced a `MAX_FOOD_ITEMS = 3` constant, and updated spawning and collision logic to manage multiple food items at once.

---

**Turn 4 — Feature: eating food spawns two more**
> *"every time the snake eat one food, there should be two more random food"*

The agent updated the food-eating logic so that whenever the snake consumes a food item, `spawn_food()` is called twice, placing two additional random food items on screen — making the game progressively more chaotic.

---

**Turn 5 — Update the game README**
> *"update the readme in snake folder"* → *"the up to date mechanism"*

The agent updated `example/snake/README.md` to document all new features including multiple food items and the dynamic spawning behaviour.

---

### Final game features
- 🍎 Red food: +1 point, snake grows
- ⭐ Blue bonus food: +3 points, snake grows
- 💜 Purple bad food: −1 point, snake shrinks
- Up to 3 food items on screen simultaneously
- Eating any food spawns 2 more random food items
- Tutorial screen on launch
- R to restart · Q to quit after game over

**To run:**
```bash
pip install pygame
python example/snake/snake_game.py
```

---
