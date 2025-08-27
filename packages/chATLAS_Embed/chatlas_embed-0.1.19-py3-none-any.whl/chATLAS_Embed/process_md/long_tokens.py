import re
import urllib.parse

from chATLAS_Embed.process_md.data_structures import PlaceholderDict


def replace_urls(text: str) -> tuple[str, PlaceholderDict]:
    """Replace URLs with placeholders."""
    modified_text = text
    placeholder_dict = {}
    counter = 0

    # Pattern to match potential URLs - includes schemes and www patterns
    # Excludes closing brackets/parens at the end to avoid breaking markdown links
    url_pattern = r"\b(?:(?:https?|ftp|ftps|file|mailto)://|www\.)[^\s)]+"

    matches = list(re.finditer(url_pattern, modified_text, re.IGNORECASE))
    replacements = {}

    for match in matches:
        url = match.group(0)
        if url not in replacements:
            placeholder = f"[URL-{counter}]"
            placeholder_dict[placeholder] = url
            replacements[url] = placeholder
            counter += 1

    # Apply replacements
    for original, placeholder in replacements.items():
        modified_text = modified_text.replace(original, placeholder)

    return modified_text, placeholder_dict


def replace_paths(text: str) -> tuple[str, PlaceholderDict]:
    """Replace file paths with placeholders."""
    modified_text = text
    placeholder_dict = {}
    counter = 0

    # Pattern to match paths - strings with at least two / characters
    # Exclude square brackets and parentheses from the path content to avoid breaking markdown links
    path_pattern = r"(?:^|\s|`|\()((?:[^\s`\[\]()]*/){2,}[^\s`\[\]()]*)(?=\s|`|$|\))"

    matches = list(re.finditer(path_pattern, modified_text))
    replacements = {}

    for match in matches:
        potential_path = match.group(1)
        # Count path separators
        separator_count = potential_path.count("/") + potential_path.count("\\")
        if separator_count >= 2 and potential_path not in replacements:
            placeholder = f"[PATH-{counter}]"
            placeholder_dict[placeholder] = potential_path
            replacements[potential_path] = placeholder
            counter += 1

    # Apply replacements
    for original, placeholder in replacements.items():
        modified_text = modified_text.replace(original, placeholder)

    return modified_text, placeholder_dict


def replace_dataset_ids(text: str) -> tuple[str, PlaceholderDict]:
    """Replace dataset IDs with placeholders."""
    modified_text = text
    placeholder_dict = {}
    counter = 0

    # Pattern to match dataset IDs - strings with at least three dots
    # Must have alphanumeric characters (not just dots) to avoid matching ellipses
    dsid_pattern = r"(?:^|\s|`)((?:[a-zA-Z0-9_-]+\.){3,}[a-zA-Z0-9_-]+)(?=\s|`|$)"

    matches = list(re.finditer(dsid_pattern, modified_text))
    replacements = {}

    for match in matches:
        potential_dsid = match.group(1)
        if potential_dsid.count(".") >= 3 and potential_dsid not in replacements:
            placeholder = f"[DSID-{counter}]"
            placeholder_dict[placeholder] = potential_dsid
            replacements[potential_dsid] = placeholder
            counter += 1

    # Apply replacements
    for original, placeholder in replacements.items():
        modified_text = modified_text.replace(original, placeholder)

    return modified_text, placeholder_dict


def replace_long_tokens_only(text: str, long_token_threshold: int) -> tuple[str, PlaceholderDict]:
    """Replace long tokens with placeholders."""
    modified_text = text
    placeholder_dict = {}
    counter = 0

    # Pattern to match any continuous non-whitespace string
    long_token_pattern = r"\S+"

    tokens = re.findall(long_token_pattern, modified_text)
    replacements = {}

    for token in tokens:
        if len(token) > long_token_threshold and token not in replacements:
            placeholder = f"[LONG-TOKEN-{counter}]"
            placeholder_dict[placeholder] = token
            replacements[token] = placeholder
            counter += 1

    # Apply replacements
    for original, placeholder in replacements.items():
        modified_text = modified_text.replace(original, placeholder)

    return modified_text, placeholder_dict


def replace_long_tokens(text: str, long_token_threshold: int = 50) -> tuple[str, PlaceholderDict]:
    """
    Detects and replaces certain tokens in markdown strings with placeholders.

    Args:
        text: The input markdown text to process
        long_token_threshold: Maximum length for tokens before they're considered "long"

    Returns:
        A tuple containing (modified_text, placeholder_dictionary)
    """
    placeholder_dict = {}
    modified_text = text

    # Replace each type of token in order
    # 1. Replace URLs first
    modified_text, url_placeholders = replace_urls(modified_text)
    placeholder_dict.update(url_placeholders)

    # 2. Replace Paths (after URLs are removed)
    modified_text, path_placeholders = replace_paths(modified_text)
    placeholder_dict.update(path_placeholders)

    # 3. Replace Dataset IDs
    modified_text, dsid_placeholders = replace_dataset_ids(modified_text)
    placeholder_dict.update(dsid_placeholders)

    # 4. Replace Long Tokens (any continuous non-whitespace string longer than threshold)
    modified_text, long_token_placeholders = replace_long_tokens_only(modified_text, long_token_threshold)
    placeholder_dict.update(long_token_placeholders)

    return modified_text, placeholder_dict
