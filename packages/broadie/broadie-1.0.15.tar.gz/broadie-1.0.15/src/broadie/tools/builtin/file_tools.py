"""
Built-in file system tools for agent operations.
Provides core file system functionality for mock environments.
"""

from typing import Annotated, List

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId
from langchain_core.tools import tool as langchain_tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from broadie.core.state import BroadieState, Todo

WRITE_TODOS_DESCRIPTION = """Create and manage a structured task list for your current work session. This helps you track progress, organize complex tasks, and demonstrate thoroughness to the user. Updates the agent's internal todo state."""

READ_FILE_DESCRIPTION = """Read file content from the mock filesystem. Results are returned using cat -n format, with line numbers starting at 1. Use this to examine file contents before making changes."""

EDIT_FILE_DESCRIPTION = """Perform exact string replacements in files. The edit will FAIL if `old_string` is not unique in the file. Use replace_all=True to replace all instances, or provide a more specific string for single replacements."""

WRITE_FILE_DESCRIPTION = """Write content to a file in the mock filesystem. This will overwrite the entire file with the new content. Use edit_file for partial changes."""

LS_FILES_DESCRIPTION = """List all files available in the mock filesystem. Use this to discover what files exist before reading or editing them."""


@langchain_tool(description=WRITE_TODOS_DESCRIPTION)
def write_todos(
    todos: List[Todo], tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Write/update todo list in agent state."""
    return Command(
        update={
            "todos": todos,
            "messages": [
                ToolMessage(
                    f"Updated todo list to {len(todos)} items",
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )


@langchain_tool(description=LS_FILES_DESCRIPTION)
def ls_files(state: Annotated[BroadieState, InjectedState]) -> List[str]:
    """List all files in the mock filesystem."""
    return list(state.get("files", {}).keys())


@langchain_tool(description=READ_FILE_DESCRIPTION)
def read_file(
    file_path: str,
    state: Annotated[BroadieState, InjectedState],
    offset: int = 0,
    limit: int = 2000,
) -> str:
    """Read file content from mock filesystem."""
    mock_filesystem = state.get("files", {})
    if file_path not in mock_filesystem:
        return f"Error: File '{file_path}' not found"

    content = mock_filesystem[file_path]

    if not content or content.strip() == "":
        return "System reminder: File exists but has empty contents"

    lines = content.splitlines()
    start_idx = offset
    end_idx = min(start_idx + limit, len(lines))

    if start_idx >= len(lines):
        return f"Error: Line offset {offset} exceeds file length ({len(lines)} lines)"

    result_lines = []
    for i in range(start_idx, end_idx):
        line_content = lines[i]
        if len(line_content) > 2000:
            line_content = line_content[:2000]

        line_number = i + 1
        result_lines.append(f"{line_number:6d}\t{line_content}")

    return "\n".join(result_lines)


@langchain_tool(description=WRITE_FILE_DESCRIPTION)
def write_file(
    file_path: str,
    content: str,
    state: Annotated[BroadieState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Write content to a file in the mock filesystem."""
    files = state.get("files", {})
    files[file_path] = content
    return Command(
        update={
            "files": files,
            "messages": [
                ToolMessage(f"Updated file {file_path}", tool_call_id=tool_call_id)
            ],
        }
    )


@langchain_tool(description=EDIT_FILE_DESCRIPTION)
def edit_file(
    file_path: str,
    old_string: str,
    new_string: str,
    state: Annotated[BroadieState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
    replace_all: bool = False,
) -> Command:
    """Edit file by replacing old_string with new_string."""
    mock_filesystem = state.get("files", {})

    if file_path not in mock_filesystem:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        f"Error: File '{file_path}' not found",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    content = mock_filesystem[file_path]

    if old_string not in content:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        f"Error: String not found in file: '{old_string}'",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    if not replace_all:
        occurrences = content.count(old_string)
        if occurrences > 1:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            f"Error: String '{old_string}' appears {occurrences} times in file. "
                            "Use replace_all=True to replace all instances, or provide a more specific string.",
                            tool_call_id=tool_call_id,
                        )
                    ]
                }
            )

    if replace_all:
        new_content = content.replace(old_string, new_string)
        replacement_count = content.count(old_string)
        result_msg = f"Successfully replaced {replacement_count} instance(s) of the string in '{file_path}'"
    else:
        new_content = content.replace(old_string, new_string, 1)
        result_msg = f"Successfully replaced string in '{file_path}'"

    mock_filesystem[file_path] = new_content
    return Command(
        update={
            "files": mock_filesystem,
            "messages": [ToolMessage(result_msg, tool_call_id=tool_call_id)],
        }
    )
