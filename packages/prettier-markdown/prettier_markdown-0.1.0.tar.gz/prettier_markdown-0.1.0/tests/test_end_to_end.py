"""End-to-end tests for markdown formatter."""

from pathlib import Path

from prettier_markdown.formatter import (
    MarkdownFormatter,
    MarkdownFormatterOptions,
)


class TestEndToEnd:
    """End-to-end tests using test data files."""

    def test_format_complete_document(self) -> None:
        """Test formatting a complete markdown document."""
        test_data_dir = Path(__file__).parent / 'test_data'
        before_file = test_data_dir / 'before.md'
        after_file = test_data_dir / 'after.md'

        # Read the before and expected after content
        with open(before_file, encoding='utf-8') as f:
            before_content = f.read()

        with open(after_file, encoding='utf-8') as f:
            expected_content = f.read()

        # Format using default options (print_width=79, prose_wrap=True)
        formatter = MarkdownFormatter()
        actual_content = formatter.format(before_content)

        assert actual_content.strip() == expected_content.strip()

    def test_format_with_different_print_width(self) -> None:
        """Test formatting with different print width."""
        test_data_dir = Path(__file__).parent / 'test_data'
        before_file = test_data_dir / 'before.md'

        with open(before_file, encoding='utf-8') as f:
            content = f.read()

        # Test with smaller print width
        options = MarkdownFormatterOptions(print_width=50, prose_wrap=True)
        formatter = MarkdownFormatter(options)
        result = formatter.format(content)

        # Verify that lines are wrapped at 50 characters
        # (excluding list indentation)
        lines = result.split('\n')
        for line in lines:
            if (
                line.strip()
                and not line.startswith('#')
                and not line.startswith('|')
                and not line.startswith('>')
                and not line.startswith('```')
            ):
                # Allow tolerance for list items and other special
                # formatting
                if not line.startswith(('- ', '1. ', '2. ', '  ')):
                    assert len(line) <= 50, (
                        f"Line too long: '{line}' ({len(line)} chars)"
                    )

    def test_format_without_prose_wrap(self) -> None:
        """Test formatting without prose wrapping."""
        test_data_dir = Path(__file__).parent / 'test_data'
        before_file = test_data_dir / 'before.md'

        with open(before_file, encoding='utf-8') as f:
            content = f.read()

        # Test without prose wrapping
        options = MarkdownFormatterOptions(print_width=79, prose_wrap=False)
        formatter = MarkdownFormatter(options)
        result = formatter.format(content)

        # The long paragraph should remain on a single line
        lines = result.split('\n')
        paragraph_line = None
        for line in lines:
            if 'This is a very long paragraph that should be wrapped' in line:
                paragraph_line = line
                break

        assert paragraph_line is not None
        assert (
            len(paragraph_line) > 79
        )  # Should be longer than print_width since wrapping is disabled

    def test_idempotent_formatting(self) -> None:
        """Test that formatting is idempotent (formatting twice gives same result)."""
        test_data_dir = Path(__file__).parent / 'test_data'
        before_file = test_data_dir / 'before.md'

        with open(before_file, encoding='utf-8') as f:
            content = f.read()

        formatter = MarkdownFormatter()

        # Format once
        first_format = formatter.format(content)

        # Format the result again
        second_format = formatter.format(first_format)

        # Should be identical
        assert first_format == second_format

    def test_preserve_code_blocks(self) -> None:
        """Test that code blocks are preserved exactly."""
        test_data_dir = Path(__file__).parent / 'test_data'
        before_file = test_data_dir / 'before.md'

        with open(before_file, encoding='utf-8') as f:
            content = f.read()

        formatter = MarkdownFormatter()
        result = formatter.format(content)

        # Code block should be preserved exactly
        assert (
            '```python\ndef hello_world():\n    print("Hello, World!")\n```'
            in result
        )

    def test_table_alignment(self) -> None:
        """Test that tables are properly aligned."""
        test_data_dir = Path(__file__).parent / 'test_data'
        before_file = test_data_dir / 'before.md'

        with open(before_file, encoding='utf-8') as f:
            content = f.read()

        formatter = MarkdownFormatter()
        result = formatter.format(content)

        # Extract table lines
        table_lines = []
        in_table = False
        for line in result.split('\n'):
            if line.strip().startswith('|') and line.strip().endswith('|'):
                table_lines.append(line)
                in_table = True
            elif in_table and not line.strip():
                break

        assert (
            len(table_lines) >= 3
        )  # Header, separator, at least one data row

        # Check that all table lines have the same number of columns
        column_counts = [line.count('|') for line in table_lines]
        assert all(count == column_counts[0] for count in column_counts)

        # Should have proper spacing
        assert '| Header 1          | Header 2 | Header 3     |' in result
        assert '| ----------------- | -------- | ------------ |' in result
