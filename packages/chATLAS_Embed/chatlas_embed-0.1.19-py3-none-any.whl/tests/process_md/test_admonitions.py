from chATLAS_Embed.process_md import admonitions


def test_simple_note_admonition():
    """Test processing of a simple note admonition to single line."""
    markdown_text = """This is a regular paragraph.

!!! note
    This is a simple note.
    It has multiple lines.

Another paragraph."""

    result = admonitions.replace_admonitions(markdown_text)

    assert "note: This is a simple note. It has multiple lines." in result
    assert "This is a regular paragraph." in result
    assert "Another paragraph." in result


def test_warning_with_custom_title():
    """Test processing of warning admonition with custom title to single line."""
    markdown_text = """??? warning "Custom Warning Title"
    This warning has a custom title.
    And some content.
    This is the third line of the warning."""

    result = admonitions.replace_admonitions(markdown_text)

    expected = 'warning: "Custom Warning Title". This warning has a custom title. And some content. This is the third line of the warning.'
    assert expected in result


def test_danger_admonition():
    """Test processing of danger admonition to single line."""
    markdown_text = """!!! danger "Proceed with Caution!"
    This is a danger admonition with a title."""

    result = admonitions.replace_admonitions(markdown_text)

    expected = 'danger: "Proceed with Caution!". This is a danger admonition with a title.'
    assert expected in result


def test_expanded_tip_admonition():
    """Test processing of initially expanded tip admonition to single line."""
    markdown_text = """???+ tip

    This is an initially expanded tip.
    Content follows.

    - Item 1
    - Item 2
    
Another paragraph after the tip."""

    result = admonitions.replace_admonitions(markdown_text)
    print("initial text:")
    print(markdown_text)
    print("result text:")
    print(result)
    expected = "tip: This is an initially expanded tip. Content follows. - Item 1 - Item 2"
    assert expected in result
    assert "Another paragraph after the tip." in result


def test_abstract_with_markdown():
    """Test processing of abstract admonition with markdown content to single line."""
    markdown_text = """!!! abstract "Summary of Points"
    This is an abstract/summary.
    It can contain Markdown like **bold text** or _italic_."""

    result = admonitions.replace_admonitions(markdown_text)

    expected = 'abstract: "Summary of Points". This is an abstract/summary. It can contain Markdown like **bold text** or _italic_.'
    assert expected in result


def test_question_admonition():
    """Test processing of question admonition to single line."""
    markdown_text = """??? question "Is this a question?"
    Yes, it might be."""

    result = admonitions.replace_admonitions(markdown_text)

    expected = 'question: "Is this a question?". Yes, it might be.'
    assert expected in result


def test_admonition_with_content():
    """Test processing of admonition with content to single line."""
    markdown_text = """!!! example "Look, Ma, No Content!"

    part of admonition



    more admonition content.

Text after admonitions."""

    result = admonitions.replace_admonitions(markdown_text)

    expected = 'example: "Look, Ma, No Content!". part of admonition more admonition content.'
    assert expected in result
    assert "Text after admonitions." in result


def test_admonition_with_nested_code_block():
    """Test processing of admonition with nested code block to single line."""
    markdown_text = """???+ note    

    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et euismod
    nulla. Curabitur feugiat, tortor non consequat finibus, justo purus auctor
    massa, nec semper lorem quam in massa.
    
        This is a nested code block (indented 8 spaces).
        The admonition content will capture it as "    This is a nested..."
    
    Back to 4-space indent."""

    result = admonitions.replace_admonitions(markdown_text)

    # The nested code block content should be included in the single line
    assert "note:" in result
    assert "Lorem ipsum dolor sit amet" in result
    assert "This is a nested code block" in result
    assert "Back to 4-space indent." in result


def test_multiple_admonitions():
    """Test processing of multiple admonitions in one text to single lines."""
    markdown_text = """This is a regular paragraph.

!!! note
    This is a simple note.
    It has multiple lines.

Another paragraph.

??? warning "Custom Warning Title"
    This warning has a custom title.
    And some content.

!!! danger "Proceed with Caution!"
    This is a danger admonition with a title."""

    result = admonitions.replace_admonitions(markdown_text)

    # Check that all admonitions are converted to single lines
    assert "note: This is a simple note. It has multiple lines." in result
    assert 'warning: "Custom Warning Title". This warning has a custom title. And some content.' in result
    assert 'danger: "Proceed with Caution!". This is a danger admonition with a title.' in result

    # Check that regular text is preserved
    assert "This is a regular paragraph." in result
    assert "Another paragraph." in result


def test_admonition_with_blank_lines():
    """Test processing of admonition with blank lines in content to single line."""
    markdown_text = """!!! note

    A note with an indented blank line:
    
    Followed by more text."""

    result = admonitions.replace_admonitions(markdown_text)

    expected = "note: A note with an indented blank line: Followed by more text."
    assert expected in result


def test_prompt_examples():
    """Test the specific examples from the original prompt."""
    prompt_examples_text = """
!!! note

    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et euismod
    nulla. Curabitur feugiat, tortor non consequat finibus, justo purus auctor
    massa, nec semper lorem quam in massa.

??? warning "this is broken"

???+ note    

    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et euismod
    nulla. Curabitur feugiat, tortor non consequat finibus, justo purus auctor
    massa, nec semper lorem quam in massa.
"""

    result = admonitions.replace_admonitions(prompt_examples_text)

    # Check that all three admonitions are converted
    assert "note: Lorem ipsum dolor sit amet" in result
    assert 'warning: "this is broken".' in result
    assert "note: Lorem ipsum dolor sit amet" in result


def test_no_admonitions():
    """Test text with no admonitions remains unchanged."""
    markdown_text = """This is just regular markdown text.

# A heading

Some more text without any admonitions."""

    result = admonitions.replace_admonitions(markdown_text)

    # Text should remain exactly the same
    assert result == markdown_text


def test_admonition_no_content():
    """Test processing of admonition with no content."""
    markdown_text = """!!! note

Text after admonition."""

    result = admonitions.replace_admonitions(markdown_text)

    # Should just have the type with colon
    assert "note:" in result
    assert "Text after admonition." in result


def test_admonition_only_title():
    """Test processing of admonition with only a title and no content."""
    markdown_text = """??? info "Just a title"

Text after admonition."""

    result = admonitions.replace_admonitions(markdown_text)

    expected = 'info: "Just a title".'
    assert expected in result
    assert "Text after admonition." in result


def test_nested_admonitions():
    """Test processing of admonition containing another admonition inside it."""
    markdown_text = """!!! note "Outer Note"
    This is the outer note content.
    
    !!! warning "Inner Warning"
        This is a warning inside the note.
        It has multiple lines too.
    
    Back to the outer note content."""
    result = admonitions.replace_admonitions(markdown_text)

    # The outer admonition should contain the inner admonition as text content
    expected = 'note: "Outer Note". This is the outer note content. !!! warning "Inner Warning" This is a warning inside the note. It has multiple lines too. Back to the outer note content.'
    assert expected in result
