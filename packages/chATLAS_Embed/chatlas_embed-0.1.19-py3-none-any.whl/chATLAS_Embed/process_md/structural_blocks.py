import re
from typing import Optional

from chATLAS_Embed.process_md.data_structures import PlaceholderDict


def replace_structural_blocks(text: str) -> tuple[str, PlaceholderDict]:
    """
    Detects and replaces markdown code blocks and tables with unique placeholders.

    Args:
        text: A string containing the markdown content.

    Returns:
        A tuple containing:
        - Modified text with structural blocks replaced by placeholders
        - Dictionary mapping placeholders to their metadata and content:
          For code blocks: {"type": "code", "language": "python", "lines": "5", "content": "..."}
          For tables: {"type": "table", "columns": "Name,Age,City", "content": "..."}
    """
    placeholders = {}
    modified_text = text

    # Replace code blocks first
    modified_text, code_placeholders = _replace_code_blocks(modified_text)
    placeholders.update(code_placeholders)

    # Replace tables second
    modified_text, table_placeholders = _replace_tables(modified_text)
    placeholders.update(table_placeholders)

    return modified_text, placeholders


def _replace_code_blocks(text: str) -> tuple[str, PlaceholderDict]:
    """
    Detects and replaces markdown code blocks with unique placeholders.

    Args:
        text: The input text containing potential code blocks.

    Returns:
        Tuple of modified text and placeholder dictionary.
    """
    placeholders = {}
    code_block_counter = 1

    # Pattern to match code blocks with capture groups for language and content
    # Group 1: language specifier (optional)
    # Group 2: code content
    # Updated pattern to handle indented code blocks (for admonitions and content tabs)
    pattern = re.compile(r"^([ \t]*)```([^\n]*)\n(.*?)^\1```$", re.MULTILINE | re.DOTALL)

    def replace_code_block(match):
        nonlocal code_block_counter
        indent = match.group(1)
        language = match.group(2).strip() if match.group(2) else ""
        content = match.group(3)
        full_block = match.group(0)

        # Count the number of lines in the code block
        content_lines = content.rstrip("\n")
        line_count = 1 if content_lines == "" else content_lines.count("\n") + 1

        # Only replace multi-line code blocks with placeholders
        if line_count > 1:
            placeholder = f"[CODE-BLOCK-{code_block_counter}]"
            placeholders[placeholder] = {
                "type": "code",
                "language": language,
                "lines": str(line_count),
                "content": full_block,
            }
            code_block_counter += 1
            return indent + placeholder
        else:
            # Leave single-line code blocks as-is
            return full_block

    modified_text = pattern.sub(replace_code_block, text)
    return modified_text, placeholders


def _replace_tables(text: str) -> tuple[str, PlaceholderDict]:
    """
    Detects and replaces markdown tables with unique placeholders.

    Args:
        text: The input text containing potential tables.

    Returns:
        Tuple of modified text and placeholder dictionary.
    """
    placeholders = {}
    table_counter = 1

    # Use regex pattern to match complete tables including indentation
    # This pattern matches:
    # 1. Optional indentation
    # 2. Header row (contains |)
    # 3. Separator row (contains | and -)
    # 4. One or more data rows (contains |)
    pattern = re.compile(
        r"^([ \t]*)\|[^\n]*\|[ \t]*\n"  # Header row with optional indentation
        r"\1\|[^\n]*[-:][^\n]*\|[ \t]*\n"  # Separator row with same indentation
        r"(?:\1\|[^\n]*\|[ \t]*\n?)*",  # Data rows with same indentation
        re.MULTILINE,
    )

    def replace_table(match):
        nonlocal table_counter
        placeholder = f"[TABLE-{table_counter}]"

        indent = match.group(1)
        full_match = match.group(0)
        table_content = full_match.rstrip()

        # Extract column names from the header row
        lines = table_content.split("\n")
        header_row = lines[0] if lines else ""
        column_names = _extract_column_names(header_row)

        placeholders[placeholder] = {
            "type": "table",
            "columns": column_names,
            "content": table_content,
        }

        table_counter += 1

        # Check if the original match ended with a newline and preserve it
        replacement = indent + placeholder
        if full_match.endswith("\n"):
            replacement += "\n"

        return replacement

    modified_text = pattern.sub(replace_table, text)
    return modified_text, placeholders


def _extract_column_names(header_row: str) -> str:
    """
    Extract column names from a markdown table header row.

    Args:
        header_row: The header row string.

    Returns:
        A comma-separated string of column names.
    """
    # Remove leading and trailing pipes and whitespace
    cleaned_row = header_row.strip().strip("|")

    # Split by pipe and strip whitespace from each column name
    column_names = [col.strip() for col in cleaned_row.split("|")]

    # Join column names with comma
    return ",".join(column_names)


def _is_table_separator(line: str) -> bool:
    """
    Check if a line is a markdown table separator row.

    Args:
        line: The line to check.

    Returns:
        True if the line is a table separator, False otherwise.
    """
    # Remove leading/trailing whitespace
    stripped = line.strip()

    # Must start and end with |
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return False

    # Check that line contains only |, -, :, and whitespace characters
    allowed_chars = set("|-: ")
    if not all(c in allowed_chars for c in stripped):
        return False

    # Must contain at least one dash
    if "-" not in stripped:
        return False

    return True


def restore_structural_blocks(text: str, placeholders: PlaceholderDict) -> str:
    """
    Restore structural blocks from placeholders back to their original content.

    Args:
        text: Text containing placeholders.
        placeholders: Dictionary mapping placeholders to their metadata and content.

    Returns:
        Text with placeholders replaced by original content.
    """
    restored_text = text
    for placeholder, metadata in placeholders.items():
        restored_text = restored_text.replace(placeholder, metadata["content"])
    return restored_text


def get_code_language(placeholders: PlaceholderDict, placeholder: str) -> str | None:
    """
    Get the language specifier for a code block placeholder.

    Args:
        placeholders: Dictionary mapping placeholders to their metadata.
        placeholder: The placeholder key to look up.

    Returns:
        The language specifier if it exists and the placeholder is a code block, None otherwise.
    """
    if placeholder in placeholders:
        metadata = placeholders[placeholder]
        if metadata.get("type") == "code":
            language = metadata.get("language", "")
            return language if language else None
    return None


def get_placeholder_type(placeholders: PlaceholderDict, placeholder: str) -> str | None:
    """
    Get the type of a placeholder (code or table).

    Args:
        placeholders: Dictionary mapping placeholders to their metadata.
        placeholder: The placeholder key to look up.

    Returns:
        The type ("code" or "table") if the placeholder exists, None otherwise.
    """
    if placeholder in placeholders:
        return placeholders[placeholder].get("type")
    return None


def get_code_lines(placeholders: PlaceholderDict, placeholder: str) -> int | None:
    """
    Get the number of lines for a code block placeholder.

    Args:
        placeholders: Dictionary mapping placeholders to their metadata.
        placeholder: The placeholder key to look up.

    Returns:
        The number of lines if the placeholder is a code block, None otherwise.
    """
    if placeholder in placeholders:
        metadata = placeholders[placeholder]
        if metadata.get("type") == "code":
            lines_str = metadata.get("lines", "")
            try:
                return int(lines_str)
            except ValueError:
                return None
    return None


def get_table_columns(placeholders: PlaceholderDict, placeholder: str) -> list[str] | None:
    """
    Get the column names for a table placeholder.

    Args:
        placeholders: Dictionary mapping placeholders to their metadata.
        placeholder: The placeholder key to look up.

    Returns:
        A list of column names if the placeholder is a table, None otherwise.
    """
    if placeholder in placeholders:
        metadata = placeholders[placeholder]
        if metadata.get("type") == "table":
            columns_str = metadata.get("columns", "")
            return columns_str.split(",") if columns_str else []
    return None
