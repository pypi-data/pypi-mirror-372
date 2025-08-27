from bs4 import BeautifulSoup


def remove_html_from_markdown(markdown_string: str) -> str:
    """
    Removes HTML tags from a Markdown string while preserving the inner content.

    Args:
        markdown_string: A string containing text in Markdown format.

    Returns:
        A string with the HTML tags removed.
    """
    soup = BeautifulSoup(markdown_string, "html.parser")
    for tag in soup.find_all(True):
        if tag.name == "img":
            tag.replace_with(tag.get("src", ""))
        else:
            tag.replace_with(tag.get_text())
    return str(soup)
