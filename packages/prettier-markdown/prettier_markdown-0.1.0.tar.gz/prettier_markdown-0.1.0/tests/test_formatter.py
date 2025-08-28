"""Unit tests for MarkdownFormatter."""

from prettier_markdown.formatter import (
    MarkdownFormatter,
    MarkdownFormatterOptions,
)


class TestMarkdownFormatterOptions:
    """Test MarkdownFormatterOptions class."""

    def test_default_options(self) -> None:
        """Test default option values."""
        options = MarkdownFormatterOptions()
        assert options.print_width == 79
        assert options.prose_wrap is True

    def test_custom_options(self) -> None:
        """Test custom option values."""
        options = MarkdownFormatterOptions(print_width=100, prose_wrap=False)
        assert options.print_width == 100
        assert options.prose_wrap is False


class TestMarkdownFormatter:
    """Test MarkdownFormatter class."""

    def test_init_default_options(self) -> None:
        """Test initialization with default options."""
        formatter = MarkdownFormatter()
        assert formatter.options.print_width == 79
        assert formatter.options.prose_wrap is True
        assert formatter._output == []

    def test_init_custom_options(self) -> None:
        """Test initialization with custom options."""
        options = MarkdownFormatterOptions(print_width=100, prose_wrap=False)
        formatter = MarkdownFormatter(options)
        assert formatter.options.print_width == 100
        assert formatter.options.prose_wrap is False

    def test_format_simple_text(self) -> None:
        """Test formatting simple text."""
        formatter = MarkdownFormatter()
        result = formatter.format('Hello world')
        assert result == 'Hello world\n'

    def test_format_heading(self) -> None:
        """Test formatting headings."""
        formatter = MarkdownFormatter()

        result = formatter.format('# Heading 1')
        assert result == '# Heading 1\n'

        result = formatter.format('## Heading 2')
        assert result == '## Heading 2\n'

        result = formatter.format('### Heading 3')
        assert result == '### Heading 3\n'

    def test_format_paragraph_with_wrapping(self) -> None:
        """Test paragraph formatting with wrapping enabled."""
        options = MarkdownFormatterOptions(print_width=20, prose_wrap=True)
        formatter = MarkdownFormatter(options)

        long_text = 'This is a very long paragraph that should be wrapped'
        result = formatter.format(long_text)

        lines = result.strip().split('\n')
        assert all(len(line) <= 20 for line in lines if line.strip())
        assert 'This is a very long' in result
        assert 'paragraph that' in result
        assert 'should be wrapped' in result

    def test_format_paragraph_without_wrapping(self) -> None:
        """Test paragraph formatting with wrapping disabled."""
        options = MarkdownFormatterOptions(print_width=20, prose_wrap=False)
        formatter = MarkdownFormatter(options)

        long_text = 'This is a very long paragraph that should not be wrapped'
        result = formatter.format(long_text)

        assert (
            result
            == 'This is a very long paragraph that should not be wrapped\n'
        )

    def test_format_bullet_list(self) -> None:
        """Test formatting bullet lists."""
        formatter = MarkdownFormatter()

        markdown = """- Item 1
- Item 2
- Item 3"""

        result = formatter.format(markdown)
        expected = '- Item 1\n- Item 2\n- Item 3\n'
        assert result == expected

    def test_format_numbered_list(self) -> None:
        """Test formatting numbered lists."""
        formatter = MarkdownFormatter()

        markdown = """1. First item
2. Second item
3. Third item"""

        result = formatter.format(markdown)
        expected = '1. First item\n2. Second item\n3. Third item\n'
        assert result == expected

    def test_format_list_with_long_items(self) -> None:
        """Test formatting lists with long items that need wrapping."""
        options = MarkdownFormatterOptions(print_width=30, prose_wrap=True)
        formatter = MarkdownFormatter(options)

        markdown = (
            '- This is a very long list item that should be wrapped properly'
        )
        result = formatter.format(markdown)

        lines = result.strip().split('\n')
        assert lines[0].startswith('- This is a very long')
        assert lines[1].startswith('  ')  # Proper indentation

    def test_format_code_block_with_language(self) -> None:
        """Test formatting code blocks with language specification."""
        formatter = MarkdownFormatter()

        markdown = """```python
def hello():
    print("Hello, World!")
```"""

        result = formatter.format(markdown)
        expected = '```python\ndef hello():\n    print("Hello, World!")\n```\n'
        assert result == expected

    def test_format_code_block_without_language(self) -> None:
        """Test formatting code blocks without language specification."""
        formatter = MarkdownFormatter()

        markdown = """```
def hello():
    print("Hello, World!")
```"""

        result = formatter.format(markdown)
        expected = '```\ndef hello():\n    print("Hello, World!")\n```\n'
        assert result == expected

    def test_format_table(self) -> None:
        """Test formatting tables."""
        formatter = MarkdownFormatter()

        markdown = """| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |"""

        result = formatter.format(markdown)

        assert '| Header 1 | Header 2 |' in result
        assert '| -------- | -------- |' in result
        assert '| Cell 1   | Cell 2   |' in result
        assert '| Cell 3   | Cell 4   |' in result

    def test_format_blockquote(self) -> None:
        """Test formatting blockquotes."""
        formatter = MarkdownFormatter()

        markdown = '> This is a blockquote'
        result = formatter.format(markdown)

        assert '> This is a blockquote' in result

    def test_format_blockquote_with_wrapping(self) -> None:
        """Test formatting blockquotes with wrapping."""
        options = MarkdownFormatterOptions(print_width=30, prose_wrap=True)
        formatter = MarkdownFormatter(options)

        markdown = (
            '> This is a very long blockquote that should be wrapped properly'
        )
        result = formatter.format(markdown)

        lines = result.strip().split('\n')
        assert all(line.startswith('>') for line in lines if line.strip())

    def test_format_thematic_break(self) -> None:
        """Test formatting thematic breaks."""
        formatter = MarkdownFormatter()

        result = formatter.format('---')
        assert result == '---\n'

    def test_format_inline_formatting(self) -> None:
        """Test formatting inline elements."""
        formatter = MarkdownFormatter()

        markdown = '**bold** and *italic* and `code`'
        result = formatter.format(markdown)

        assert '**bold**' in result
        assert '*italic*' in result
        assert '`code`' in result

    def test_format_links(self) -> None:
        """Test formatting links."""
        formatter = MarkdownFormatter()

        markdown = '[Link text](https://example.com)'
        result = formatter.format(markdown)

        assert '[Link text](https://example.com)' in result

    def test_format_images(self) -> None:
        """Test formatting images."""
        formatter = MarkdownFormatter()

        markdown = '![Alt text](image.jpg)'
        result = formatter.format(markdown)

        assert '![Alt text](image.jpg)' in result

    def test_extract_text_content_simple(self) -> None:
        """Test _extract_text_content with simple text node."""
        formatter = MarkdownFormatter()

        node = {'type': 'text', 'raw': 'Hello world'}
        result = formatter._extract_text_content(node)

        assert result == 'Hello world'

    def test_extract_text_content_emphasis(self) -> None:
        """Test _extract_text_content with emphasis node."""
        formatter = MarkdownFormatter()

        node = {
            'type': 'emphasis',
            'children': [{'type': 'text', 'raw': 'italic text'}],
        }
        result = formatter._extract_text_content(node)

        assert result == '*italic text*'

    def test_extract_text_content_strong(self) -> None:
        """Test _extract_text_content with strong node."""
        formatter = MarkdownFormatter()

        node = {
            'type': 'strong',
            'children': [{'type': 'text', 'raw': 'bold text'}],
        }
        result = formatter._extract_text_content(node)

        assert result == '**bold text**'

    def test_extract_text_content_codespan(self) -> None:
        """Test _extract_text_content with codespan node."""
        formatter = MarkdownFormatter()

        node = {'type': 'codespan', 'raw': 'inline code'}
        result = formatter._extract_text_content(node)

        assert result == '`inline code`'

    def test_extract_text_content_link(self) -> None:
        """Test _extract_text_content with link node."""
        formatter = MarkdownFormatter()

        node = {
            'type': 'link',
            'children': [{'type': 'text', 'raw': 'Link text'}],
            'attrs': {'url': 'https://example.com'},
        }
        result = formatter._extract_text_content(node)

        assert result == '[Link text](https://example.com)'

    def test_extract_text_content_image(self) -> None:
        """Test _extract_text_content with image node."""
        formatter = MarkdownFormatter()

        node = {
            'type': 'image',
            'children': [{'type': 'text', 'raw': 'Alt text'}],
            'attrs': {'url': 'image.jpg'},
        }
        result = formatter._extract_text_content(node)

        assert result == '![Alt text](image.jpg)'

    def test_extract_children_text(self) -> None:
        """Test _extract_children_text method."""
        formatter = MarkdownFormatter()

        node = {
            'children': [
                {'type': 'text', 'raw': 'Hello '},
                {'type': 'text', 'raw': 'world'},
            ]
        }
        result = formatter._extract_children_text(node)

        assert result == 'Hello world'

    def test_extract_children_text_no_children(self) -> None:
        """Test _extract_children_text with no children."""
        formatter = MarkdownFormatter()

        node = {}
        result = formatter._extract_children_text(node)

        assert result == ''

    def test_format_mixed_content(self) -> None:
        """Test formatting content with mixed elements."""
        formatter = MarkdownFormatter()

        markdown = """# Title

This is a paragraph with **bold** and *italic* text.

- List item 1
- List item 2

```python
code_block()
```

> A blockquote

---"""

        result = formatter.format(markdown)

        assert '# Title' in result
        assert '**bold**' in result
        assert '*italic*' in result
        assert '- List item 1' in result
        assert '```python' in result
        assert 'code_block()' in result
        assert '> A blockquote' in result
        assert '---' in result
