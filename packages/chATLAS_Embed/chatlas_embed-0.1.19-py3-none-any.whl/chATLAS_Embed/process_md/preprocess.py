from chATLAS_Embed.process_md.admonitions import replace_admonitions
from chATLAS_Embed.process_md.content_tabs import replace_content_tabs
from chATLAS_Embed.process_md.data_structures import PlaceholderDict
from chATLAS_Embed.process_md.html_utils import remove_html_from_markdown
from chATLAS_Embed.process_md.long_tokens import replace_long_tokens
from chATLAS_Embed.process_md.structural_blocks import replace_structural_blocks


def preprocess_markdown(markdown_text: str) -> tuple[str, PlaceholderDict]:
    """
    Process markdown text by handling structural elements.

    This function:
    1. Extracts structural blocks (code blocks and tables) from the entire document,
       including those nested within admonitions and content tabs
    2. Processes admonitions and content tabs on the modified text
    3. Replaces long tokens, URLs, paths, and dataset IDs with placeholders
    4. Removes HTML tags from the markdown text
    5. Returns the processed markdown text and a dictionary of placeholders

    Args:
        markdown_text: The markdown text to process

    Returns:
        Tuple of (processed markdown text, placeholder dictionary)
    """
    text_with_placeholders, placeholders = replace_structural_blocks(markdown_text)
    processed_text = replace_admonitions(text_with_placeholders)
    processed_text = replace_content_tabs(processed_text)
    processed_text, token_placeholders = replace_long_tokens(processed_text)
    placeholders.update(token_placeholders)
    processed_text = remove_html_from_markdown(processed_text)

    return processed_text, placeholders
