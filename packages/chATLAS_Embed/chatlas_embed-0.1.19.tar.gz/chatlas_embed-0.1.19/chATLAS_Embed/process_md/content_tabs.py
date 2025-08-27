import re


def replace_content_tabs(markdown_text):
    """
    Detects and replaces MkDocs Material content tabs in markdown text.

    Args:
        markdown_text: A string containing the markdown content.

    Returns:
        A string with content tabs replaced by plain paragraph format,
        with separate paragraphs for each tab.
    """
    # Process content tabs one by one using a simpler approach
    lines = markdown_text.split("\n")
    result_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this line is a content tab declaration
        tab_match = re.match(r'^[ \t]*===[ \t]+"([^"]+)"[ \t]*$', line)

        if tab_match:
            title = tab_match.group(1)
            i += 1

            # Collect indented content following the tab declaration
            content_lines = []
            while i < len(lines):
                next_line = lines[i]

                # If we hit another tab declaration or non-indented content, stop
                if re.match(r"^[ \t]*===[ \t]+", next_line) or (
                    next_line.strip() and not next_line.startswith("    ") and not next_line.startswith("\t")
                ):
                    break

                # If it's indented content or empty line, include it
                if next_line.startswith("    ") or next_line.startswith("\t") or not next_line.strip():
                    content_lines.append(next_line)
                    i += 1
                else:
                    break

            # Format the tab content
            cleaned_content = " ".join(line.lstrip() for line in content_lines if line.strip())
            formatted_tab = f"{title}: {cleaned_content}" if cleaned_content else title

            # Add the formatted tab as a separate paragraph
            result_lines.append(formatted_tab)
            result_lines.append("")  # Add blank line for paragraph separation
        else:
            result_lines.append(line)
            i += 1

    return "\n".join(result_lines)
