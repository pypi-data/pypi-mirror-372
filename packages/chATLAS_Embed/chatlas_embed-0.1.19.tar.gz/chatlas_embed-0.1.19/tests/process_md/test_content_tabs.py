from chATLAS_Embed.process_md import content_tabs


def test_simple_content_tab():
    """Test processing of a simple content tab to plain paragraph."""
    markdown_text = """This is a regular paragraph.

=== "Tab Title"

    This is content inside the tab.
    It has multiple lines.

Another paragraph."""

    result = content_tabs.replace_content_tabs(markdown_text)

    assert "Tab Title: This is content inside the tab. It has multiple lines." in result
    assert "This is a regular paragraph." in result
    assert "Another paragraph." in result


def test_multiple_content_tabs():
    """Test processing of multiple content tabs in one text."""
    markdown_text = """Regular text before tabs.

=== "First Tab"

    Content of the first tab.
    Multiple lines here.

=== "Second Tab"

    Content of the second tab.
    More content here.

Text after tabs."""

    result = content_tabs.replace_content_tabs(markdown_text)

    # Check that both tabs are present as separate paragraphs
    assert "First Tab: Content of the first tab. Multiple lines here." in result
    assert "Second Tab: Content of the second tab. More content here." in result
    assert "Regular text before tabs." in result
    assert "Text after tabs." in result

    # Check that tabs are separated by blank lines (paragraph separation)
    lines = result.split("\n")
    first_tab_idx = next(i for i, line in enumerate(lines) if "First Tab:" in line)
    second_tab_idx = next(i for i, line in enumerate(lines) if "Second Tab:" in line)

    # There should be a blank line between the two tabs
    assert lines[first_tab_idx + 1] == ""
    assert second_tab_idx == first_tab_idx + 2


def test_content_tab_with_code_block():
    """Test processing of content tab containing code block."""
    markdown_text = """=== "Code Example"

    Here's some code:
    
        def hello():
            print("Hello, world!")
    
    End of tab content."""

    result = content_tabs.replace_content_tabs(markdown_text)

    expected = 'Code Example: Here\'s some code: def hello(): print("Hello, world!") End of tab content.'
    assert expected in result


def test_content_tab_with_markdown():
    """Test processing of content tab with markdown content."""
    markdown_text = """=== "Markdown Content"

    This tab contains **bold text** and *italic text*.
    It also has a [link](http://example.com).
    
    - List item 1
    - List item 2"""

    result = content_tabs.replace_content_tabs(markdown_text)

    expected = "Markdown Content: This tab contains **bold text** and *italic text*. It also has a [link](http://example.com). - List item 1 - List item 2"
    assert expected in result


def test_empty_content_tab():
    """Test processing of content tab with no content."""
    markdown_text = """=== "Empty Tab"

Text after tab."""

    result = content_tabs.replace_content_tabs(markdown_text)

    assert "Empty Tab" in result
    assert "Text after tab." in result


def test_content_tab_with_blank_lines():
    """Test processing of content tab with blank lines in content."""
    markdown_text = """=== "Tab with Spaces"

    First line of content.
    
    
    Second line after blank lines."""

    result = content_tabs.replace_content_tabs(markdown_text)

    expected = "Tab with Spaces: First line of content. Second line after blank lines."
    assert expected in result


def test_nested_content_tabs():
    """Test processing of content tabs that might contain tab-like syntax."""
    markdown_text = """=== "Outer Tab"

    This tab mentions another tab syntax: === "Inner" but it's just text.
    More content here."""

    result = content_tabs.replace_content_tabs(markdown_text)

    expected = 'Outer Tab: This tab mentions another tab syntax: === "Inner" but it\'s just text. More content here.'
    assert expected in result


def test_no_content_tabs():
    """Test text with no content tabs remains unchanged."""
    markdown_text = """This is just regular markdown text.

# A heading

Some more text without any content tabs."""

    result = content_tabs.replace_content_tabs(markdown_text)

    # Text should remain exactly the same
    assert result == markdown_text


def test_content_tab_with_special_characters():
    """Test processing of content tab with special characters in title."""
    markdown_text = """=== "Tab with Special & Characters!"

    Content with special characters: @#$%^&*()
    More content here."""

    result = content_tabs.replace_content_tabs(markdown_text)

    expected = "Tab with Special & Characters!: Content with special characters: @#$%^&*() More content here."
    assert expected in result


def test_content_tab_indented():
    """Test processing of indented content tab."""
    markdown_text = """Some text before.

    === "Indented Tab"

        This is content inside an indented tab.
        More indented content.

Text after."""

    result = content_tabs.replace_content_tabs(markdown_text)

    expected = "Indented Tab: This is content inside an indented tab. More indented content."
    assert expected in result
    assert "Some text before." in result
    assert "Text after." in result


def test_mixed_content_tabs_and_regular_text():
    """Test processing of mixed content with tabs and regular markdown."""
    markdown_text = """# Main Heading

This is regular text.

=== "Configuration"

    Here's how to configure the system:
    
    1. Step one
    2. Step two
    3. Step three

## Another Section

=== "Usage Example"

    Usage instructions here.
    With multiple lines.

Final paragraph."""

    result = content_tabs.replace_content_tabs(markdown_text)

    assert "Configuration: Here's how to configure the system: 1. Step one 2. Step two 3. Step three" in result
    assert "Usage Example: Usage instructions here. With multiple lines." in result
    assert "# Main Heading" in result
    assert "## Another Section" in result
    assert "Final paragraph." in result

    # Check that tabs are separated as paragraphs
    lines = result.split("\n")
    config_idx = next(i for i, line in enumerate(lines) if "Configuration:" in line)

    # Configuration tab should be followed by a blank line
    assert lines[config_idx + 1] == ""


def test_content_tab_only_title():
    """Test processing of content tab with only title and no content."""
    markdown_text = """=== "Title Only"
Text immediately after."""

    result = content_tabs.replace_content_tabs(markdown_text)

    assert "Title Only" in result
    assert "Text immediately after." in result
