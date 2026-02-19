"""
Tool implementations and OpenAI-compatible definitions for the coding agent.
All tools accept a `cwd` parameter to resolve relative paths correctly.
"""

import os
import subprocess
import fnmatch
from typing import Any, Dict


# ---------------------------------------------------------------------------
# Implementations
# ---------------------------------------------------------------------------

def read_file(path: str, cwd: str = ".") -> str:
    full_path = path if os.path.isabs(path) else os.path.join(cwd, path)
    if not os.path.exists(full_path):
        return f"Error: '{path}' does not exist"
    if not os.path.isfile(full_path):
        return f"Error: '{path}' is not a file"
    try:
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"


def write_file(path: str, content: str, cwd: str = ".") -> str:
    full_path = path if os.path.isabs(path) else os.path.join(cwd, path)
    try:
        os.makedirs(os.path.dirname(os.path.abspath(full_path)), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to '{path}'"
    except Exception as e:
        return f"Error writing file: {e}"


def create_directory(path: str, cwd: str = ".") -> str:
    full_path = path if os.path.isabs(path) else os.path.join(cwd, path)
    try:
        os.makedirs(full_path, exist_ok=True)
        return f"Successfully created directory '{path}'"
    except Exception as e:
        return f"Error creating directory: {e}"


def list_directory(path: str = ".", cwd: str = ".") -> str:
    full_path = path if os.path.isabs(path) else os.path.join(cwd, path)
    if not os.path.exists(full_path):
        return f"Error: '{path}' does not exist"
    try:
        entries = []
        for entry in sorted(os.scandir(full_path), key=lambda e: (not e.is_dir(), e.name)):
            if entry.is_dir():
                entries.append(f"📁 {entry.name}/")
            else:
                size = entry.stat().st_size
                if size < 1024:
                    size_str = f"{size}B"
                elif size < 1024 * 1024:
                    size_str = f"{size / 1024:.1f}KB"
                else:
                    size_str = f"{size / (1024 * 1024):.1f}MB"
                entries.append(f"📄 {entry.name} ({size_str})")
        return "\n".join(entries) if entries else "(empty directory)"
    except Exception as e:
        return f"Error listing directory: {e}"


def execute_bash(command: str, cwd: str = ".") -> str:
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        parts = []
        if result.stdout:
            parts.append(result.stdout.rstrip())
        if result.stderr:
            parts.append(f"[stderr]\n{result.stderr.rstrip()}")
        parts.append(f"[exit code: {result.returncode}]")
        return "\n".join(parts)
    except subprocess.TimeoutExpired:
        return "Error: command timed out after 120 seconds"
    except Exception as e:
        return f"Error executing command: {e}"


def search_files(pattern: str, directory: str = ".", cwd: str = ".") -> str:
    full_dir = directory if os.path.isabs(directory) else os.path.join(cwd, directory)
    try:
        matches = []
        skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "env", "dist", "build"}
        for root, dirs, files in os.walk(full_dir):
            dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith(".")]
            for filename in files:
                if fnmatch.fnmatch(filename, pattern):
                    matches.append(os.path.relpath(os.path.join(root, filename), cwd))
        if not matches:
            return f"No files found matching '{pattern}' in '{directory}'"
        return "\n".join(sorted(matches))
    except Exception as e:
        return f"Error searching files: {e}"


def grep_search(pattern: str, path: str = ".", recursive: bool = True, cwd: str = ".") -> str:
    full_path = path if os.path.isabs(path) else os.path.join(cwd, path)
    try:
        flags = ["-rn"] if recursive else ["-n"]
        result = subprocess.run(
            ["grep"] + flags + ["--include=*.*", "-I", pattern, full_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            rel_lines = []
            for line in lines:
                if ":" in line:
                    file_part, rest = line.split(":", 1)
                    try:
                        rel_file = os.path.relpath(file_part, cwd)
                        rel_lines.append(f"{rel_file}:{rest}")
                    except ValueError:
                        rel_lines.append(line)
                else:
                    rel_lines.append(line)
            capped = rel_lines[:100]
            suffix = f"\n... ({len(rel_lines) - 100} more results)" if len(rel_lines) > 100 else ""
            return "\n".join(capped) + suffix
        elif result.returncode == 1:
            return f"No matches found for '{pattern}'"
        else:
            return f"grep error: {result.stderr.strip()}"
    except Exception as e:
        return f"Error searching: {e}"


# ---------------------------------------------------------------------------
# OpenAI-compatible tool definitions (works with litellm for all providers)
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file. Use to view existing source code, configs, or text files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file (relative to the working directory)",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write (create or overwrite) a file with the given content. Parent directories are created automatically.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Destination file path (relative to the working directory)",
                    },
                    "content": {
                        "type": "string",
                        "description": "Full content to write to the file",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_directory",
            "description": "Create a new directory, including any necessary parent directories.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to create",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List the contents of a directory to understand project structure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory to list (default: working directory)",
                        "default": ".",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "execute_bash",
            "description": "Execute a bash command and return stdout, stderr, and exit code. Use for running scripts, tests, installs, or git operations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to execute",
                    }
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "Find files by name using a glob pattern (e.g. '*.py', 'test_*.js').",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern to match filenames",
                    },
                    "directory": {
                        "type": "string",
                        "description": "Directory to search in (default: working directory)",
                        "default": ".",
                    },
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep_search",
            "description": "Search for a text pattern inside files. Supports regex. Use to find usages of functions, variables, or any text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Text or regex pattern to search for",
                    },
                    "path": {
                        "type": "string",
                        "description": "File or directory to search in (default: working directory)",
                        "default": ".",
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Search subdirectories recursively (default: true)",
                        "default": True,
                    },
                },
                "required": ["pattern"],
            },
        },
    },
]


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def execute_tool(name: str, args: Dict[str, Any], cwd: str = ".") -> str:
    """Dispatch a tool call by name."""
    if name == "read_file":
        return read_file(args["path"], cwd)
    elif name == "write_file":
        return write_file(args["path"], args["content"], cwd)
    elif name == "create_directory":
        return create_directory(args["path"], cwd)
    elif name == "list_directory":
        return list_directory(args.get("path", "."), cwd)
    elif name == "execute_bash":
        return execute_bash(args["command"], cwd)
    elif name == "search_files":
        return search_files(args["pattern"], args.get("directory", "."), cwd)
    elif name == "grep_search":
        return grep_search(args["pattern"], args.get("path", "."), args.get("recursive", True), cwd)
    else:
        return f"Error: unknown tool '{name}'"
