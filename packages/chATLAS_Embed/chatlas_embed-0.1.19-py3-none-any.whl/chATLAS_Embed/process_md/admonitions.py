import re


def replace_admonitions(markdown_text):
    """
    Detects and replaces MkDocs Material admonitions in markdown text.

    Args:
        markdown_text: A string containing the markdown content.

    Returns:
        A string with admonitions replaced by a single-line format.
    """
    lines = markdown_text.split("\n")
    result_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this line starts an admonition
        admonition_match = re.match(r'^[ \t]*(?:!{3}|\?{3})\+?[ \t]+(\w+)[ \t]*(?:"([^"]*)")?', line)

        if admonition_match:
            admonition_type = admonition_match.group(1)
            title = admonition_match.group(2)
            i += 1

            # Collect the indented content
            content_lines = []
            while i < len(lines):
                next_line = lines[i]

                # If it's indented content (starts with 4+ spaces or tab)
                if next_line.startswith("    ") or next_line.startswith("\t"):
                    content_lines.append(next_line)
                    i += 1
                # If it's an empty line, check if the next line is still part of the admonition
                elif not next_line.strip():
                    # Look ahead to see if we have more indented content
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1

                    # If the next non-empty line is indented, this empty line is part of the admonition
                    if j < len(lines) and (lines[j].startswith("    ") or lines[j].startswith("\t")):
                        content_lines.append(next_line)
                        i += 1
                    else:
                        # Empty line marks the end of the admonition
                        break
                else:
                    # Non-empty, non-indented line marks the end of the admonition
                    break

            # Process the content - remove all empty lines and join with spaces
            cleaned_content = " ".join(line.lstrip() for line in content_lines if line.strip())

            # Format the admonition
            if title:
                formatted = f'{admonition_type}: "{title}"'
                if cleaned_content:
                    formatted += f". {cleaned_content}"
                else:
                    formatted += "."
            else:
                formatted = f"{admonition_type}:"
                if cleaned_content:
                    formatted += f" {cleaned_content}"

            result_lines.append(formatted)
        else:
            result_lines.append(line)
            i += 1

    return "\n".join(result_lines)
