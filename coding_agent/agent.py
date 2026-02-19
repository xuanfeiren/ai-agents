"""
Core agent loop using litellm for provider-agnostic LLM calls.
"""

import json
import os
from typing import Any, Dict, List, Optional

import litellm
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from tools import TOOL_DEFINITIONS, execute_tool

# Suppress litellm's verbose success messages
litellm.suppress_debug_info = True

SYSTEM_PROMPT = """\
You are an expert coding agent with access to file-system and shell tools.
Help the user accomplish programming tasks by:

1. Reading existing code before making changes.
2. Writing clean, well-commented, idiomatic code.
3. Running commands to install dependencies and test your work.
4. Explaining your reasoning concisely.
5. Handling edge cases and errors gracefully.

Always think step by step. When asked to build something, plan first, then
implement incrementally, verifying each step with execute_bash when useful.\
"""

# Icons for each tool (used in the CLI display)
TOOL_ICONS: Dict[str, str] = {
    "read_file": "📖",
    "write_file": "✍️ ",
    "create_directory": "📁",
    "list_directory": "📂",
    "execute_bash": "⚡",
    "search_files": "🔍",
    "grep_search": "🔎",
}


class CodingAgent:
    def __init__(self, model: str = "claude-3-5-sonnet-20241022", cwd: str = "."):
        self.model = model
        self.cwd = os.path.abspath(cwd)
        self.messages: List[Dict[str, Any]] = []
        self.console = Console()

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Start the interactive REPL."""
        self._print_welcome()
        while True:
            try:
                user_input = self._get_user_input()
                if not user_input.strip():
                    continue

                cmd = user_input.strip().lower()
                if cmd in {"exit", "quit", "bye", "/exit", "/quit"}:
                    self.console.print("\n[dim]Goodbye! 👋[/dim]\n")
                    break
                elif cmd in {"/clear", "/reset"}:
                    self.messages = []
                    self.console.print("[dim]Conversation cleared.[/dim]\n")
                    continue
                elif cmd == "/help":
                    self._print_help()
                    continue

                self.messages.append({"role": "user", "content": user_input})
                self._run_agent_loop()

            except KeyboardInterrupt:
                self.console.print("\n\n[dim]Interrupted. Type 'exit' to quit.[/dim]\n")
            except EOFError:
                self.console.print("\n[dim]Goodbye! 👋[/dim]\n")
                break

    # ------------------------------------------------------------------
    # Agent loop
    # ------------------------------------------------------------------

    def _run_agent_loop(self, max_iterations: int = 50) -> None:
        """Call the LLM repeatedly until it stops requesting tool calls."""
        for _ in range(max_iterations):
            with self.console.status(
                "[bold blue]◉  Thinking…[/bold blue]", spinner="dots", spinner_style="bold blue"
            ):
                try:
                    response = litellm.completion(
                        model=self.model,
                        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + self.messages,
                        tools=TOOL_DEFINITIONS,
                        tool_choice="auto",
                        max_tokens=8096,
                    )
                except Exception as exc:
                    self.console.print(f"\n[bold red]LLM error:[/bold red] {exc}\n")
                    return

            message = response.choices[0].message
            finish_reason = response.choices[0].finish_reason

            # Persist the assistant turn (serialise to plain dict for history)
            self.messages.append(self._serialise_message(message))

            # ---- Final text response ----
            if finish_reason != "tool_calls" or not message.tool_calls:
                if message.content:
                    self._display_response(message.content)
                return

            # ---- Display any prose before tool calls ----
            if message.content:
                self._display_thinking(message.content)

            # ---- Execute each requested tool call ----
            tool_result_messages: List[Dict[str, Any]] = []
            for tc in message.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    args = {}
                result = self._execute_tool(tc.function.name, args, tc.id)
                tool_result_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": tc.function.name,
                        "content": result,
                    }
                )

            self.messages.extend(tool_result_messages)

        self.console.print("[yellow]Warning: reached maximum tool-call iterations.[/yellow]")

    # ------------------------------------------------------------------
    # Tool execution
    # ------------------------------------------------------------------

    def _execute_tool(self, name: str, args: Dict[str, Any], call_id: str) -> str:
        self._display_tool_call(name, args)
        try:
            result = execute_tool(name, args, self.cwd)
        except Exception as exc:
            result = f"Error: {exc}"
        self._display_tool_result(result)
        return result

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def _display_tool_call(self, name: str, args: Dict[str, Any]) -> None:
        icon = TOOL_ICONS.get(name, "🔧")

        # Build a short human-readable description of the call
        if name == "read_file":
            desc = f"[cyan]{args.get('path', '')}[/cyan]"
        elif name == "write_file":
            path = args.get("path", "")
            lines = len(args.get("content", "").splitlines())
            desc = f"[cyan]{path}[/cyan] [dim]({lines} lines)[/dim]"
        elif name == "create_directory":
            desc = f"[cyan]{args.get('path', '')}[/cyan]"
        elif name == "list_directory":
            desc = f"[cyan]{args.get('path', '.')}[/cyan]"
        elif name == "execute_bash":
            cmd = args.get("command", "")
            truncated = cmd[:90] + ("…" if len(cmd) > 90 else "")
            desc = f"[bold yellow]{truncated}[/bold yellow]"
        elif name == "search_files":
            desc = (
                f"[cyan]{args.get('pattern', '')}[/cyan]"
                f" in [cyan]{args.get('directory', '.')}[/cyan]"
            )
        elif name == "grep_search":
            desc = (
                f"[cyan]{args.get('pattern', '')}[/cyan]"
                f" in [cyan]{args.get('path', '.')}[/cyan]"
            )
        else:
            desc = " ".join(f"{k}={v!r}" for k, v in args.items())

        self.console.print(f"  {icon} [bold]{name}[/bold]  {desc}")

    def _display_tool_result(self, result: str) -> None:
        MAX_LINES = 20
        MAX_CHARS = 1200
        lines = result.split("\n")
        display = "\n".join(lines[:MAX_LINES])
        if len(display) > MAX_CHARS:
            display = display[:MAX_CHARS] + "…"
        extra = len(lines) - MAX_LINES
        self.console.print(f"  [dim]{display}[/dim]")
        if extra > 0:
            self.console.print(f"  [dim]… ({extra} more lines)[/dim]")
        self.console.print()

    def _display_thinking(self, text: str) -> None:
        if text.strip():
            self.console.print(f"\n[dim]{text.strip()}[/dim]\n")

    def _display_response(self, text: str) -> None:
        self.console.print()
        self.console.print(
            Panel(Markdown(text), border_style="blue", padding=(1, 2))
        )
        self.console.print()

    def _get_user_input(self) -> str:
        self.console.print("[bold cyan]❯[/bold cyan] ", end="")
        return input()

    def _print_welcome(self) -> None:
        self.console.print()
        self.console.print(
            Panel(
                Text.assemble(
                    ("  🤖  Coding Agent\n", "bold white"),
                    (
                        "  Powered by litellm  ·  type '/help' for commands  ·  'exit' to quit",
                        "dim",
                    ),
                ),
                border_style="blue",
                padding=(0, 2),
            )
        )
        self.console.print(f"  [dim]Model  :[/dim]  [bold]{self.model}[/bold]")
        self.console.print(f"  [dim]Workdir:[/dim]  {self.cwd}")
        self.console.print()

    def _print_help(self) -> None:
        table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        table.add_column("Command", style="cyan bold")
        table.add_column("Description", style="dim")
        table.add_row("/clear, /reset", "Clear conversation history")
        table.add_row("/help", "Show this help")
        table.add_row("exit, quit", "Exit the agent")
        self.console.print(Panel(table, title="[bold]Commands[/bold]", border_style="dim"))
        self.console.print()

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _serialise_message(message: Any) -> Dict[str, Any]:
        """Convert a litellm/openai Message object to a plain dict."""
        d: Dict[str, Any] = {"role": message.role}
        if message.content:
            d["content"] = message.content
        if message.tool_calls:
            d["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in message.tool_calls
            ]
        return d
