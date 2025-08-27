from chATLAS_Embed.process_md import structural_blocks


def test_simple_code_block():
    """Test detection and replacement of a simple code block."""
    markdown_text = """This is regular text.

```python
def hello():
    print("Hello, world!")
```

More text after."""

    result, placeholders = structural_blocks.replace_structural_blocks(markdown_text)

    # Check that code block was replaced with placeholder
    assert "[CODE-BLOCK-1]" in result
    assert "```python" not in result
    assert "def hello():" not in result

    # Check placeholder mapping
    assert len(placeholders) == 1
    assert "[CODE-BLOCK-1]" in placeholders

    # Check metadata structure
    metadata = placeholders["[CODE-BLOCK-1]"]
    assert metadata["type"] == "code"
    assert metadata["language"] == "python"
    assert metadata["lines"] == "2"  # "def hello():" and "print(...)"
    assert "```python" in metadata["content"]
    assert "def hello():" in metadata["content"]

    # Check that other text is preserved
    assert "This is regular text." in result
    assert "More text after." in result


def test_multiple_code_blocks():
    """Test detection and replacement of multiple code blocks."""
    markdown_text = """First code block:

```bash
echo "Hello"
echo "Hello"
```

Some text between.

```javascript
console.log("World");
console.log("World");
```

End text."""

    result, placeholders = structural_blocks.replace_structural_blocks(markdown_text)

    # Check that both code blocks were replaced
    assert "[CODE-BLOCK-1]" in result
    assert "[CODE-BLOCK-2]" in result
    assert "```bash" not in result
    assert "```javascript" not in result

    # Check placeholder mappings
    assert len(placeholders) == 2

    # Check first code block metadata
    metadata1 = placeholders["[CODE-BLOCK-1]"]
    assert metadata1["type"] == "code"
    assert metadata1["language"] == "bash"
    assert metadata1["lines"] == "2"
    assert 'echo "Hello"' in metadata1["content"]

    # Check second code block metadata
    metadata2 = placeholders["[CODE-BLOCK-2]"]
    assert metadata2["type"] == "code"
    assert metadata2["language"] == "javascript"
    assert metadata2["lines"] == "2"
    assert 'console.log("World");' in metadata2["content"]


def test_code_block_with_language():
    """Test code block with language specification."""
    markdown_text = """```sql
SELECT * FROM users;
SELECT * FROM users;
```"""

    result, placeholders = structural_blocks.replace_structural_blocks(markdown_text)

    assert "[CODE-BLOCK-1]" in result
    metadata = placeholders["[CODE-BLOCK-1]"]
    assert metadata["type"] == "code"
    assert metadata["language"] == "sql"
    assert metadata["lines"] == "2"
    assert "SELECT * FROM users;" in metadata["content"]


def test_code_block_without_language():
    """Test code block without language specification."""
    markdown_text = """```
This is plain code
without language
```"""

    result, placeholders = structural_blocks.replace_structural_blocks(markdown_text)

    assert "[CODE-BLOCK-1]" in result
    metadata = placeholders["[CODE-BLOCK-1]"]
    assert metadata["type"] == "code"
    assert metadata["language"] == ""
    assert "This is plain code" in metadata["content"]


def test_simple_table():
    """Test detection and replacement of a simple markdown table."""
    markdown_text = """Here's a table:

| Name | Age | City |
|------|-----|------|
| John | 25  | NYC  |
| Jane | 30  | LA   |

Text after table."""

    result, placeholders = structural_blocks.replace_structural_blocks(markdown_text)

    # Check that table was replaced with placeholder
    assert "[TABLE-1]" in result
    assert "| Name | Age | City |" not in result
    assert "|------|-----|------|" not in result

    # Check placeholder mapping
    assert len(placeholders) == 1
    assert "[TABLE-1]" in placeholders

    # Check metadata structure
    metadata = placeholders["[TABLE-1]"]
    assert metadata["type"] == "table"
    assert metadata["columns"] == "Name,Age,City"
    table_content = metadata["content"]
    assert "| Name | Age | City |" in table_content
    assert "|------|-----|------|" in table_content
    assert "| John | 25  | NYC  |" in table_content
    assert "| Jane | 30  | LA   |" in table_content

    # Check that other text is preserved
    assert "Here's a table:" in result
    assert "Text after table." in result


def test_multiple_tables():
    """Test detection and replacement of multiple tables."""
    markdown_text = """First table:

| A | B |
|---|---|
| 1 | 2 |

Some text.

| X | Y | Z |
|---|---|---|
| a | b | c |
| d | e | f |

End text."""

    result, placeholders = structural_blocks.replace_structural_blocks(markdown_text)

    # Check that both tables were replaced
    assert "[TABLE-1]" in result
    assert "[TABLE-2]" in result
    assert "| A | B |" not in result
    assert "| X | Y | Z |" not in result

    # Check placeholder mappings
    assert len(placeholders) == 2

    # Check table metadata
    metadata1 = placeholders["[TABLE-1]"]
    assert metadata1["type"] == "table"
    assert "| A | B |" in metadata1["content"]

    metadata2 = placeholders["[TABLE-2]"]
    assert metadata2["type"] == "table"
    assert "| X | Y | Z |" in metadata2["content"]


def test_table_with_alignment():
    """Test table with column alignment syntax."""
    markdown_text = """| Left | Center | Right |
|:-----|:------:|------:|
| L1   |   C1   |    R1 |
| L2   |   C2   |    R2 |"""

    result, placeholders = structural_blocks.replace_structural_blocks(markdown_text)

    assert "[TABLE-1]" in result
    metadata = placeholders["[TABLE-1]"]
    assert metadata["type"] == "table"
    table_content = metadata["content"]
    assert "|:-----|:------:|------:|" in table_content
    assert "| Left | Center | Right |" in table_content


def test_mixed_code_blocks_and_tables():
    """Test text with both code blocks and tables."""
    markdown_text = """Code example:

```python
print("Hello")
print("Hello")
```

And a table:

| Item | Count |
|------|-------|
| Apples | 5 |
| Oranges | 3 |

Another code block:

```bash
ls -la
ls -la
```"""

    result, placeholders = structural_blocks.replace_structural_blocks(markdown_text)

    # Check that all structural blocks were replaced
    assert "[CODE-BLOCK-1]" in result
    assert "[TABLE-1]" in result
    assert "[CODE-BLOCK-2]" in result

    # Check placeholder mappings
    assert len(placeholders) == 3

    # Check code block metadata
    code1_metadata = placeholders["[CODE-BLOCK-1]"]
    assert code1_metadata["type"] == "code"
    assert code1_metadata["language"] == "python"
    assert 'print("Hello")' in code1_metadata["content"]

    # Check table metadata
    table_metadata = placeholders["[TABLE-1]"]
    assert table_metadata["type"] == "table"
    assert "| Item | Count |" in table_metadata["content"]

    # Check second code block metadata
    code2_metadata = placeholders["[CODE-BLOCK-2]"]
    assert code2_metadata["type"] == "code"
    assert code2_metadata["language"] == "bash"
    assert "ls -la" in code2_metadata["content"]


def test_invalid_table_no_separator():
    """Test that lines with pipes but no separator are not treated as tables."""
    markdown_text = """This line has | pipes | but no separator.
| Another | line | with | pipes |
But no separator follows."""

    result, placeholders = structural_blocks.replace_structural_blocks(markdown_text)

    # Should not create any table placeholders
    assert "[TABLE-" not in result
    assert len(placeholders) == 0
    # Original text should be preserved
    assert "This line has | pipes | but no separator." in result


def test_invalid_table_malformed_separator():
    """Test that malformed separators don't create tables."""
    markdown_text = """| Column 1 | Column 2 |
| not a valid separator |
| Data 1 | Data 2 |"""

    result, placeholders = structural_blocks.replace_structural_blocks(markdown_text)

    # Should not create table placeholders
    assert "[TABLE-" not in result
    assert len(placeholders) == 0


def test_table_separator_detection():
    """Test the table separator detection function directly."""
    # Valid separators
    assert structural_blocks._is_table_separator("|---|---|")
    assert structural_blocks._is_table_separator("| --- | --- |")
    assert structural_blocks._is_table_separator("|:-----|:----:|-----:|")
    assert structural_blocks._is_table_separator("| :--- | :---: | ---: |")

    # Invalid separators
    assert not structural_blocks._is_table_separator("| text | more |")
    assert not structural_blocks._is_table_separator("|abc|def|")
    assert not structural_blocks._is_table_separator("no pipes here")
    assert not structural_blocks._is_table_separator("| --- no ending pipe")
    assert not structural_blocks._is_table_separator("no starting | --- |")


def test_restore_structural_blocks():
    """Test restoration of structural blocks from placeholders."""
    original_text = """Code:

```python
def test():
    pass
```

Table:

| A | B |
|---|---|
| 1 | 2 |"""

    # Replace blocks with placeholders
    modified_text, placeholders = structural_blocks.replace_structural_blocks(original_text)

    # Restore from placeholders
    restored_text = structural_blocks.restore_structural_blocks(modified_text, placeholders)

    # Should match original (allowing for minor whitespace differences)
    assert "```python" in restored_text
    assert "def test():" in restored_text
    assert "| A | B |" in restored_text
    assert "|---|---|" in restored_text


def test_get_code_language():
    """Test the get_code_language helper function."""
    markdown_text = """```python
print("Hello")
print("Hello")
```

```
plain code
plain code
```

| Table | Here |
|-------|------|
| Data  | Here |"""

    result, placeholders = structural_blocks.replace_structural_blocks(markdown_text)

    # Test getting language for Python code block
    assert structural_blocks.get_code_language(placeholders, "[CODE-BLOCK-1]") == "python"

    # Test getting language for code block without language
    assert structural_blocks.get_code_language(placeholders, "[CODE-BLOCK-2]") is None

    # Test getting language for table (should be None)
    assert structural_blocks.get_code_language(placeholders, "[TABLE-1]") is None

    # Test getting language for non-existent placeholder
    assert structural_blocks.get_code_language(placeholders, "[NONEXISTENT]") is None


def test_get_placeholder_type():
    """Test the get_placeholder_type helper function."""
    markdown_text = """```python
print("Hello")
print("Hello")
```

| Table | Here |
|-------|------|
| Data  | Here |"""

    result, placeholders = structural_blocks.replace_structural_blocks(markdown_text)

    # Test getting type for code block
    assert structural_blocks.get_placeholder_type(placeholders, "[CODE-BLOCK-1]") == "code"

    # Test getting type for table
    assert structural_blocks.get_placeholder_type(placeholders, "[TABLE-1]") == "table"

    # Test getting type for non-existent placeholder
    assert structural_blocks.get_placeholder_type(placeholders, "[NONEXISTENT]") is None


def test_get_code_lines():
    """Test the get_code_lines helper function."""
    markdown_text = """Single line:
```python
print("Hello")
print("Hello")
```

Multiple lines:
```javascript
function test() {
    console.log("Line 1");
    console.log("Line 2");
    return true;
}
```

Empty code block:
```
```

| Table | Here |
|-------|------|
| Data  | Here |"""

    result, placeholders = structural_blocks.replace_structural_blocks(markdown_text)

    # Test getting line count for single line code block
    assert structural_blocks.get_code_lines(placeholders, "[CODE-BLOCK-1]") == 2

    # Test getting line count for multi-line code block
    assert structural_blocks.get_code_lines(placeholders, "[CODE-BLOCK-2]") == 5

    # Test getting line count for empty code block
    assert "[CODE-BLOCK-3]" not in placeholders

    # Test getting line count for table (should be None)
    assert structural_blocks.get_code_lines(placeholders, "[TABLE-1]") is None

    # Test getting line count for non-existent placeholder
    assert structural_blocks.get_code_lines(placeholders, "[NONEXISTENT]") is None


def test_no_structural_blocks():
    """Test text with no code blocks or tables remains unchanged."""
    markdown_text = """This is just regular markdown text.

# A heading

Some paragraphs with **bold** and *italic* text.

- List items
- More items

> A blockquote

No structural blocks here."""

    result, placeholders = structural_blocks.replace_structural_blocks(markdown_text)

    # Text should remain exactly the same
    assert result == markdown_text
    assert len(placeholders) == 0


def test_code_block_edge_cases():
    """Test edge cases for code block detection."""
    # Code block at start of text
    markdown_text1 = """```python
print("start")
print("end")
```"""
    result1, placeholders1 = structural_blocks.replace_structural_blocks(markdown_text1)
    assert "[CODE-BLOCK-1]" in result1
    assert len(placeholders1) == 1
    assert placeholders1["[CODE-BLOCK-1]"]["language"] == "python"

    # Code block at end of text
    markdown_text2 = """Some text
```bash
echo "end"
another
```"""
    result2, placeholders2 = structural_blocks.replace_structural_blocks(markdown_text2)
    assert "[CODE-BLOCK-1]" in result2
    assert len(placeholders2) == 1
    assert placeholders2["[CODE-BLOCK-1]"]["language"] == "bash"

    # Empty code block (shouldn't become a placeholder)
    markdown_text3 = """```
```"""
    result3, placeholders3 = structural_blocks.replace_structural_blocks(markdown_text3)
    assert "[CODE-BLOCK-1]" not in result3
    assert len(placeholders3) == 0

    # One line code block (shouldn't become a placeholder)
    markdown_text4 = """```
print("Hello")
```"""
    result4, placeholders4 = structural_blocks.replace_structural_blocks(markdown_text4)
    assert "[CODE-BLOCK-1]" not in result4
    assert len(placeholders4) == 0


def test_table_edge_cases():
    """Test edge cases for table detection."""
    # Table at start of text
    markdown_text1 = """| A | B |
|---|---|
| 1 | 2 |"""
    result1, placeholders1 = structural_blocks.replace_structural_blocks(markdown_text1)
    assert "[TABLE-1]" in result1
    assert len(placeholders1) == 1
    assert placeholders1["[TABLE-1]"]["type"] == "table"

    # Table at end of text
    markdown_text2 = """Some text

| X | Y |
|---|---|
| a | b |

More text
"""
    result2, placeholders2 = structural_blocks.replace_structural_blocks(markdown_text2)

    expected_result = """Some text

[TABLE-1]

More text
"""
    assert expected_result == result2
    assert len(placeholders2) == 1
    assert placeholders2["[TABLE-1]"]["type"] == "table"


def test_nested_backticks_in_text():
    """Test that inline code with backticks doesn't interfere with code blocks."""
    markdown_text = """Here's some `inline code` with backticks.

```python
def example():
    # This has `backticks` inside
    return "code block"
```

More `inline` code here."""

    result, placeholders = structural_blocks.replace_structural_blocks(markdown_text)

    # Code block should be replaced
    assert "[CODE-BLOCK-1]" in result
    # Inline code should remain
    assert "`inline code`" in result
    assert "`inline`" in result

    # Check placeholder content
    metadata = placeholders["[CODE-BLOCK-1]"]
    assert metadata["type"] == "code"
    assert metadata["language"] == "python"
    assert metadata["lines"] == "3"  # 3 lines in the code block
    assert int(metadata["lines"]) == 3  # Ensure line count is correct
    assert "def example():" in metadata["content"]
    assert "`backticks`" in metadata["content"]


def test_complex_integration():
    """Test complex markdown with multiple structural elements."""
    markdown_text = """# Project Documentation

Here's the main function:

```python
def main():
    print("Starting application")
    return 0
```

## Configuration

The configuration options are:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| debug | bool | false | Enable debug mode |
| port | int | 8080 | Server port |

## Usage Examples

Basic usage:

```bash
python app.py --debug
python app.py --debug
```

Advanced configuration:

```yaml
server:
  port: 3000
  debug: true
```

## Results

| Test | Status | Time |
|------|--------|------|
| Unit | Pass | 2.3s |
| Integration | Pass | 5.1s |

That's all!"""

    result, placeholders = structural_blocks.replace_structural_blocks(markdown_text)

    # Check all structural blocks were replaced
    assert "[CODE-BLOCK-1]" in result  # Python code
    assert "[TABLE-1]" in result  # Configuration table
    assert "[CODE-BLOCK-2]" in result  # Bash command
    assert "[CODE-BLOCK-3]" in result  # YAML config
    assert "[TABLE-2]" in result  # Results table

    # Check placeholder count
    assert len(placeholders) == 5

    # Check some content preservation
    assert "# Project Documentation" in result
    assert "## Configuration" in result
    assert "That's all!" in result

    # Verify placeholder contents and metadata
    code1_metadata = placeholders["[CODE-BLOCK-1]"]
    assert code1_metadata["type"] == "code"
    assert code1_metadata["language"] == "python"
    assert "def main():" in code1_metadata["content"]

    table1_metadata = placeholders["[TABLE-1]"]
    assert table1_metadata["type"] == "table"
    assert "| Option | Type |" in table1_metadata["content"]

    code2_metadata = placeholders["[CODE-BLOCK-2]"]
    assert code2_metadata["type"] == "code"
    assert code2_metadata["language"] == "bash"
    assert "python app.py" in code2_metadata["content"]

    code3_metadata = placeholders["[CODE-BLOCK-3]"]
    assert code3_metadata["type"] == "code"
    assert code3_metadata["language"] == "yaml"
    assert "server:" in code3_metadata["content"]

    table2_metadata = placeholders["[TABLE-2]"]
    assert table2_metadata["type"] == "table"
    assert "| Test | Status |" in table2_metadata["content"]


def test_language_extraction_edge_cases():
    """Test various edge cases for language extraction."""
    # Language with extra spaces
    markdown_text1 = """```  python  
print("test")
print("test")
```"""
    result1, placeholders1 = structural_blocks.replace_structural_blocks(markdown_text1)
    assert placeholders1["[CODE-BLOCK-1]"]["language"] == "python"

    # Language with parameters (common in markdown)
    markdown_text2 = """```javascript {.line-numbers}
console.log("test");
console.log("test");
```"""
    result2, placeholders2 = structural_blocks.replace_structural_blocks(markdown_text2)
    assert placeholders2["[CODE-BLOCK-1]"]["language"] == "javascript {.line-numbers}"

    # No language, just whitespace
    markdown_text3 = """```   
plain text
plain text
```"""
    result3, placeholders3 = structural_blocks.replace_structural_blocks(markdown_text3)
    assert placeholders3["[CODE-BLOCK-1]"]["language"] == ""


def test_get_table_columns():
    """Test the get_table_columns helper function."""
    markdown_text = """Simple table:

| Name | Age | City |
|------|-----|------|
| John | 25  | NYC  |

Table with spaces:

| First Name | Last Name | Email Address |
|------------|-----------|---------------|
| Jane       | Doe       | jane@example.com |

| A | B |
|---|---|
| 1 | 2 |

```python
print("code")
```"""

    result, placeholders = structural_blocks.replace_structural_blocks(markdown_text)

    # Test getting columns for first table
    columns1 = structural_blocks.get_table_columns(placeholders, "[TABLE-1]")
    assert columns1 == ["Name", "Age", "City"]

    # Test getting columns for second table (with spaces in names)
    columns2 = structural_blocks.get_table_columns(placeholders, "[TABLE-2]")
    assert columns2 == ["First Name", "Last Name", "Email Address"]

    # Test getting columns for third table
    columns3 = structural_blocks.get_table_columns(placeholders, "[TABLE-3]")
    assert columns3 == ["A", "B"]

    # Test getting columns for code block (should be None)
    assert structural_blocks.get_table_columns(placeholders, "[CODE-BLOCK-1]") is None

    # Test getting columns for non-existent placeholder
    assert structural_blocks.get_table_columns(placeholders, "[NONEXISTENT]") is None
