from chATLAS_Embed.process_md.chunker import preprocess_markdown


def test_preprocess_markdown_with_all_features():
    """Test processing markdown with code blocks, tables, admonitions, and content tabs."""
    markdown_text = """# Test Document

This is a regular paragraph.

!!! note "Important Information"
    This is an admonition with some important details.
    It spans multiple lines.

???+ warning "Important Information"

!!!+ warning "Important Information"

    Here's a warning with a title.


=== "Option A"
    This is content for option A.
    It has multiple lines too.

=== "Option B"
    This is content for option B.

Here's a code block:

```python
def hello_world():
    print("Hello, World!")
    return True
```

And here's a table:

| Name | Age | City |
|------|-----|------|
| John | 25  | NYC  |
| Jane | 30  | LA   |

More regular text after all the special elements."""

    expected_content = """# Test Document

This is a regular paragraph.

note: "Important Information". This is an admonition with some important details. It spans multiple lines.

warning: "Important Information".

warning: "Important Information". Here's a warning with a title.


Option A: This is content for option A. It has multiple lines too.

Option B: This is content for option B.

Here's a code block:

[CODE-BLOCK-1]

And here's a table:

[TABLE-1]

More regular text after all the special elements."""

    result, placeholders = preprocess_markdown(markdown_text)
    assert result == expected_content

    # Check code block placeholder
    assert "[CODE-BLOCK-1]" in placeholders
    code_metadata = placeholders["[CODE-BLOCK-1]"]
    assert code_metadata["type"] == "code"
    assert code_metadata["language"] == "python"
    assert code_metadata["lines"] == "3"
    assert "def hello_world():" in code_metadata["content"]
    assert "```python" in code_metadata["content"]

    # Check table placeholder
    assert "[TABLE-1]" in placeholders
    table_metadata = placeholders["[TABLE-1]"]
    assert table_metadata["type"] == "table"
    assert table_metadata["columns"] == "Name,Age,City"
    assert "| Name | Age | City |" in table_metadata["content"]
    assert "| John | 25  | NYC  |" in table_metadata["content"]


def test_admonitions_processing():
    """Test processing of admonitions only."""
    markdown_text = """!!! note "Important Information"
    This is an admonition with some important details.
    It spans multiple lines.

!!! warning
    This is a warning."""

    expected_content = """note: "Important Information". This is an admonition with some important details. It spans multiple lines.

warning: This is a warning."""

    result, placeholders = preprocess_markdown(markdown_text)
    assert result == expected_content
    # No structural blocks, so placeholders should be empty
    assert len(placeholders) == 0


def test_content_tabs_processing():
    """Test processing of content tabs only."""
    markdown_text = """=== "Option A"
    This is content for option A.
    It has multiple lines too.

=== "Option B"
    This is content for option B."""

    expected_content = """Option A: This is content for option A. It has multiple lines too.

Option B: This is content for option B.
"""

    result, placeholders = preprocess_markdown(markdown_text)
    assert result == expected_content
    # No structural blocks, so placeholders should be empty
    assert len(placeholders) == 0


def test_structural_blocks_processing():
    """Test that structural blocks are replaced with placeholders."""
    markdown_text = """# Code Example

```python
print("test")
print("test")
```

| Col1 | Col2 |
|------|------|
| A    | B    |
"""

    expected_content = """# Code Example

[CODE-BLOCK-1]

[TABLE-1]
"""

    result, placeholders = preprocess_markdown(markdown_text)
    assert result == expected_content

    # Check code block metadata
    assert "[CODE-BLOCK-1]" in placeholders
    code_metadata = placeholders["[CODE-BLOCK-1]"]
    assert code_metadata["type"] == "code"
    assert code_metadata["language"] == "python"
    assert code_metadata["lines"] == "2"
    assert 'print("test")' in code_metadata["content"]
    assert "```python" in code_metadata["content"]

    # Check table metadata
    assert "[TABLE-1]" in placeholders
    table_metadata = placeholders["[TABLE-1]"]
    assert table_metadata["type"] == "table"
    assert table_metadata["columns"] == "Col1,Col2"
    assert "| Col1 | Col2 |" in table_metadata["content"]
    assert "| A    | B    |" in table_metadata["content"]


def test_empty_input():
    """Test handling of empty input."""
    result, placeholders = preprocess_markdown("")
    assert result == ""
    assert len(placeholders) == 0


def test_only_structural_blocks():
    """Test processing text with only structural blocks."""
    markdown_text = """```python
print("hello")
print("hello")
```

| A | B |
|---|---|
| 1 | 2 |


| A | B |
|---|---|
| 1 | 2 |"""

    expected_content = """[CODE-BLOCK-1]

[TABLE-1]


[TABLE-2]"""

    result, placeholders = preprocess_markdown(markdown_text)
    print(result)
    assert result == expected_content

    # Check code block metadata
    assert "[CODE-BLOCK-1]" in placeholders
    code_metadata = placeholders["[CODE-BLOCK-1]"]
    assert code_metadata["type"] == "code"
    assert code_metadata["language"] == "python"
    assert code_metadata["lines"] == "2"
    assert 'print("hello")' in code_metadata["content"]

    # Check first table metadata
    assert "[TABLE-1]" in placeholders
    table1_metadata = placeholders["[TABLE-1]"]
    assert table1_metadata["type"] == "table"
    assert table1_metadata["columns"] == "A,B"
    assert "| A | B |" in table1_metadata["content"]
    assert "| 1 | 2 |" in table1_metadata["content"]

    # Check second table metadata
    assert "[TABLE-2]" in placeholders
    table2_metadata = placeholders["[TABLE-2]"]
    assert table2_metadata["type"] == "table"
    assert table2_metadata["columns"] == "A,B"
    assert "| A | B |" in table2_metadata["content"]
    assert "| 1 | 2 |" in table2_metadata["content"]


def test_mixed_content():
    """Test processing text with mixed content types."""
    markdown_text = """# Title

Regular paragraph.

!!! info "Note"
    Some information here.

=== "Tab 1"
    Tab content here.

```bash
echo "hello"
echo "hello"
```

Another paragraph.
"""

    expected_content = """# Title

Regular paragraph.

info: "Note". Some information here.

Tab 1: Tab content here.

[CODE-BLOCK-1]

Another paragraph.
"""

    result, placeholders = preprocess_markdown(markdown_text)
    assert result == expected_content

    # Check code block metadata
    assert "[CODE-BLOCK-1]" in placeholders
    code_metadata = placeholders["[CODE-BLOCK-1]"]
    assert code_metadata["type"] == "code"
    assert code_metadata["language"] == "bash"
    assert code_metadata["lines"] == "2"
    assert 'echo "hello"' in code_metadata["content"]
    assert "```bash" in code_metadata["content"]


def test_code_block_without_language():
    """Test processing code block without language specifier."""
    markdown_text = """```
print("no language specified")
x = 42
```"""

    expected_content = """[CODE-BLOCK-1]"""

    result, placeholders = preprocess_markdown(markdown_text)
    assert result == expected_content

    # Check code block metadata
    assert "[CODE-BLOCK-1]" in placeholders
    code_metadata = placeholders["[CODE-BLOCK-1]"]
    assert code_metadata["type"] == "code"
    assert code_metadata["language"] == ""  # Empty string for no language
    assert code_metadata["lines"] == "2"
    assert 'print("no language specified")' in code_metadata["content"]
    assert code_metadata["content"].count("\n") == 3  # Opening fence + 2 content lines + closing fence


def test_table_with_different_columns():
    """Test processing table with different column structure."""
    markdown_text = """| Product | Price | Available |
|---------|-------|-----------|
| Apple   | $1.50 | Yes       |
| Orange  | $2.00 | No        |"""

    expected_content = """[TABLE-1]"""

    result, placeholders = preprocess_markdown(markdown_text)
    assert result == expected_content

    # Check table metadata
    assert "[TABLE-1]" in placeholders
    table_metadata = placeholders["[TABLE-1]"]
    assert table_metadata["type"] == "table"
    assert table_metadata["columns"] == "Product,Price,Available"
    assert "| Product | Price | Available |" in table_metadata["content"]
    assert "| Apple   | $1.50 | Yes       |" in table_metadata["content"]


def test_code_blocks_inside_admonitions_and_tabs():
    """Test that code blocks inside admonitions and content tabs are correctly identified and replaced with placeholders."""
    markdown_text = """# Test Document

!!! note "Code Example"

    Here's some Python code:

    ```python
    def example_function():
        return "Hello from admonition"
    ```

    This is additional text after the code block.

=== "Python Tab"
    Here's a Python example:
    
    ```python
    x = [1, 2, 3]
    print(x)
    ```

=== "Bash Tab"
    And here's a bash command:
    
    ```bash
    ls -la
    echo "done"
    ```

!!! warning "Multiple Code Blocks"
    First code block:
    
    ```javascript
    console.log("first");
    console.log("first");
    ```
    
    Some text in between.
    
    ```sql
    SELECT * FROM users;
    SELECT * FROM users;
    ```

Regular paragraph with a table:

| Name | Value |
|------|-------|
| Test | 123   |
"""

    expected_content = """# Test Document

note: "Code Example". Here's some Python code: [CODE-BLOCK-1] This is additional text after the code block.

Python Tab: Here's a Python example: [CODE-BLOCK-2]

Bash Tab: And here's a bash command: [CODE-BLOCK-3]

warning: "Multiple Code Blocks". First code block: [CODE-BLOCK-4] Some text in between. [CODE-BLOCK-5]

Regular paragraph with a table:

[TABLE-1]
"""

    result, placeholders = preprocess_markdown(markdown_text)
    assert result == expected_content

    # Check that all 5 code blocks and 1 table are identified
    assert len(placeholders) == 6

    # Check first code block (inside note admonition)
    assert "[CODE-BLOCK-1]" in placeholders
    code1_metadata = placeholders["[CODE-BLOCK-1]"]
    assert code1_metadata["type"] == "code"
    assert code1_metadata["language"] == "python"
    assert code1_metadata["lines"] == "2"
    assert "def example_function():" in code1_metadata["content"]
    assert 'return "Hello from admonition"' in code1_metadata["content"]

    # Check second code block (inside Python tab)
    assert "[CODE-BLOCK-2]" in placeholders
    code2_metadata = placeholders["[CODE-BLOCK-2]"]
    assert code2_metadata["type"] == "code"
    assert code2_metadata["language"] == "python"
    assert code2_metadata["lines"] == "2"
    assert "x = [1, 2, 3]" in code2_metadata["content"]
    assert "print(x)" in code2_metadata["content"]

    # Check third code block (inside Bash tab)
    assert "[CODE-BLOCK-3]" in placeholders
    code3_metadata = placeholders["[CODE-BLOCK-3]"]
    assert code3_metadata["type"] == "code"
    assert code3_metadata["language"] == "bash"
    assert code3_metadata["lines"] == "2"
    assert "ls -la" in code3_metadata["content"]
    assert 'echo "done"' in code3_metadata["content"]

    # Check fourth code block (first one inside warning admonition)
    assert "[CODE-BLOCK-4]" in placeholders
    code4_metadata = placeholders["[CODE-BLOCK-4]"]
    assert code4_metadata["type"] == "code"
    assert code4_metadata["language"] == "javascript"
    assert code4_metadata["lines"] == "2"
    assert 'console.log("first");' in code4_metadata["content"]

    # Check fifth code block (second one inside warning admonition)
    assert "[CODE-BLOCK-5]" in placeholders
    code5_metadata = placeholders["[CODE-BLOCK-5]"]
    assert code5_metadata["type"] == "code"
    assert code5_metadata["language"] == "sql"
    assert code5_metadata["lines"] == "2"
    assert "SELECT * FROM users;" in code5_metadata["content"]

    # Check table
    assert "[TABLE-1]" in placeholders
    table_metadata = placeholders["[TABLE-1]"]
    assert table_metadata["type"] == "table"
    assert table_metadata["columns"] == "Name,Value"
    assert "| Name | Value |" in table_metadata["content"]
    assert "| Test | 123   |" in table_metadata["content"]


def test_tables_inside_admonitions_and_tabs():
    """Test that tables inside admonitions and content tabs are correctly identified and replaced with placeholders."""
    markdown_text = """# Test Document

!!! info "Data Example"
    Here's some tabular data:
    
    | Product | Price | Stock |
    |---------|-------|-------|
    | Widget  | $10   | 50    |
    | Gadget  | $25   | 30    |
    
    This table shows our inventory.

=== "Sales Data"
    Current sales figures:
    
    | Month | Sales | Growth |
    |-------|-------|--------|
    | Jan   | 1000  | 5%     |
    | Feb   | 1100  | 10%    |

=== "User Data"
    User statistics:
    
    | Role  | Count | Active |
    |-------|-------|--------|
    | Admin | 5     | 100%   |
    | User  | 120   | 85%    |

!!! warning "Important Tables"
    First table with critical data:
    
    | System | Status | Last Check |
    |--------|--------|------------|
    | DB     | OK     | 10:30 AM   |
    | API    | DOWN   | 09:45 AM   |
    
    Some text between tables.
    
    | Error | Count | Severity |
    |-------|-------|----------|
    | 404   | 25    | Medium   |
    | 500   | 3     | High     |

Regular paragraph with a code block:

```python
print("This is a code block")
print("This is a code block")
```
"""

    expected_content = """# Test Document

info: "Data Example". Here's some tabular data: [TABLE-1] This table shows our inventory.

Sales Data: Current sales figures: [TABLE-2]

User Data: User statistics: [TABLE-3]

warning: "Important Tables". First table with critical data: [TABLE-4] Some text between tables. [TABLE-5]

Regular paragraph with a code block:

[CODE-BLOCK-1]
"""

    result, placeholders = preprocess_markdown(markdown_text)
    assert result == expected_content

    # Check that all 5 tables and 1 code block are identified
    assert len(placeholders) == 6

    # Check first table (inside info admonition)
    assert "[TABLE-1]" in placeholders
    table1_metadata = placeholders["[TABLE-1]"]
    assert table1_metadata["type"] == "table"
    assert table1_metadata["columns"] == "Product,Price,Stock"
    expected_table1_content = """| Product | Price | Stock |
    |---------|-------|-------|
    | Widget  | $10   | 50    |
    | Gadget  | $25   | 30    |"""
    assert table1_metadata["content"].strip() == expected_table1_content

    # Check second table (inside Sales Data tab)
    assert "[TABLE-2]" in placeholders
    table2_metadata = placeholders["[TABLE-2]"]
    assert table2_metadata["type"] == "table"
    assert table2_metadata["columns"] == "Month,Sales,Growth"
    expected_table2_content = """| Month | Sales | Growth |
    |-------|-------|--------|
    | Jan   | 1000  | 5%     |
    | Feb   | 1100  | 10%    |"""
    assert table2_metadata["content"].strip() == expected_table2_content

    # Check third table (inside User Data tab)
    assert "[TABLE-3]" in placeholders
    table3_metadata = placeholders["[TABLE-3]"]
    assert table3_metadata["type"] == "table"
    assert table3_metadata["columns"] == "Role,Count,Active"
    expected_table3_content = """| Role  | Count | Active |
    |-------|-------|--------|
    | Admin | 5     | 100%   |
    | User  | 120   | 85%    |"""
    assert table3_metadata["content"].strip() == expected_table3_content

    # Check fourth table (first one inside warning admonition)
    assert "[TABLE-4]" in placeholders
    table4_metadata = placeholders["[TABLE-4]"]
    assert table4_metadata["type"] == "table"
    assert table4_metadata["columns"] == "System,Status,Last Check"
    expected_table4_content = """| System | Status | Last Check |
    |--------|--------|------------|
    | DB     | OK     | 10:30 AM   |
    | API    | DOWN   | 09:45 AM   |"""
    assert table4_metadata["content"].strip() == expected_table4_content

    # Check fifth table (second one inside warning admonition)
    assert "[TABLE-5]" in placeholders
    table5_metadata = placeholders["[TABLE-5]"]
    assert table5_metadata["type"] == "table"
    assert table5_metadata["columns"] == "Error,Count,Severity"
    expected_table5_content = """| Error | Count | Severity |
    |-------|-------|----------|
    | 404   | 25    | Medium   |
    | 500   | 3     | High     |"""
    assert table5_metadata["content"].strip() == expected_table5_content

    # Check code block
    assert "[CODE-BLOCK-1]" in placeholders
    code_metadata = placeholders["[CODE-BLOCK-1]"]
    assert code_metadata["type"] == "code"
    assert code_metadata["language"] == "python"
    assert code_metadata["lines"] == "2"
    assert 'print("This is a code block")' in code_metadata["content"]
