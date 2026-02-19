#!/usr/bin/env python3
"""
Coding Agent — entry point.

Usage:
    python main.py
    python main.py --model gpt-4o
    python main.py --model gemini/gemini-1.5-pro --cwd /path/to/project
"""

import argparse
import os
import sys


EXAMPLES = """
model strings (litellm format):
  Anthropic   claude-3-5-sonnet-20241022  claude-3-opus-20240229
  OpenAI      gpt-4o  gpt-4o-mini  o1-preview
  Gemini      gemini/gemini-1.5-pro  gemini/gemini-2.0-flash
  Ollama      ollama/llama3  ollama/codellama
  Groq        groq/llama-3.1-70b-versatile

required env vars (set the one matching your provider):
  ANTHROPIC_API_KEY
  OPENAI_API_KEY
  GEMINI_API_KEY
  GROQ_API_KEY
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="coding-agent",
        description="🤖  Coding Agent — AI-powered CLI coding assistant (powered by litellm)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EXAMPLES,
    )
    parser.add_argument(
        "--model",
        default="claude-3-5-sonnet-20241022",
        metavar="MODEL",
        help="litellm model string (default: claude-3-5-sonnet-20241022)",
    )
    parser.add_argument(
        "--cwd",
        default=".",
        metavar="DIR",
        help="working directory for the agent (default: current directory)",
    )
    return parser


def check_dependencies() -> None:
    missing = []
    for pkg in ("litellm", "rich"):
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Run:  pip install -r requirements.txt")
        sys.exit(1)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    check_dependencies()

    # Validate working directory
    cwd = os.path.abspath(args.cwd)
    if not os.path.isdir(cwd):
        print(f"Error: '{cwd}' is not a directory.")
        sys.exit(1)

    from agent import CodingAgent

    agent = CodingAgent(model=args.model, cwd=cwd)
    agent.run()


if __name__ == "__main__":
    main()
