"""Integration tests for CLI functionality."""

import subprocess
import tempfile
from pathlib import Path


class IntegrationTests:
    """Integration tests for command-line interface."""

    def test_cli_format_file(self) -> None:
        """Test CLI formatting a file in place."""
        # Create a temporary markdown file
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.md', delete=False
        ) as f:
            f.write(
                '# Title\n\nThis is a very long paragraph that should'
                ' be wrapped when the prose-wrap option is enabled.'
            )
            temp_file = Path(f.name)

        try:
            # Run the CLI command to format the file
            result = subprocess.run(
                ['prettier-markdown', str(temp_file)],
                capture_output=True,
                text=True,
                check=True,
            )

            assert result.returncode == 0
            assert f'Formatted {temp_file}' in result.stdout

            # Read the formatted content
            with open(temp_file, encoding='utf-8') as f:
                content = f.read()

            # Should be properly formatted
            assert '# Title' in content
            assert (
                'This is a very long paragraph that should be wrapped'
                ' when the prose-wrap'
            ) in content
            assert 'option\nis enabled.' in content

        finally:
            # Clean up
            temp_file.unlink()

    def test_cli_check_mode_formatted(self) -> None:
        """Test CLI check mode on already formatted file."""
        # Create a properly formatted temporary file
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.md', delete=False
        ) as f:
            f.write('# Title\n\nThis is a properly formatted paragraph.\n')
            temp_file = Path(f.name)

        try:
            # Run check mode
            result = subprocess.run(
                ['prettier-markdown', '--check', str(temp_file)],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert f'{temp_file}: File is not changed' in result.stdout

        finally:
            temp_file.unlink()

    def test_cli_check_mode_unformatted(self) -> None:
        """Test CLI check mode on unformatted file."""
        # Create an unformatted temporary file
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.md', delete=False
        ) as f:
            f.write(
                '# Title\n\nThis is a very long paragraph that should'
                ' be wrapped when the prose-wrap option is enabled because'
                ' it exceeds the print-width limit.'
            )
            temp_file = Path(f.name)

        try:
            # Run check mode
            result = subprocess.run(
                ['prettier-markdown', '--check', str(temp_file)],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 1
            assert f'{temp_file}: File is re-formatted' in result.stdout

        finally:
            temp_file.unlink()

    def test_cli_print_width_option(self) -> None:
        """Test CLI with custom print width."""
        # Create a temporary file with long text
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.md', delete=False
        ) as f:
            f.write(
                'This is a very long paragraph that should be wrapped'
                ' at a specific width.'
            )
            temp_file = Path(f.name)

        try:
            # Format with custom print width
            result = subprocess.run(
                ['prettier-markdown', '--print-width', '30', str(temp_file)],
                capture_output=True,
                text=True,
                check=True,
            )

            assert result.returncode == 0

            # Read the formatted content
            with open(temp_file, encoding='utf-8') as f:
                content = f.read()

            # Lines should be wrapped at 30 characters
            lines = content.strip().split('\n')
            assert len(lines) > 1  # Should be multiple lines due to wrapping
            assert all(len(line) <= 30 for line in lines if line.strip())

        finally:
            temp_file.unlink()

    def test_cli_prose_wrap_true(self) -> None:
        """Test CLI with prose-wrap=true."""
        # Create a temporary file with long text
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.md', delete=False
        ) as f:
            f.write(
                'This is a very long paragraph that should be wrapped'
                ' when prose wrapping is enabled.'
            )
            temp_file = Path(f.name)

        try:
            # Format with prose-wrap=true
            result = subprocess.run(
                [
                    'prettier-markdown',
                    '--prose-wrap=true',
                    '--print-width',
                    '40',
                    str(temp_file),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            assert result.returncode == 0

            # Read the formatted content
            with open(temp_file, encoding='utf-8') as f:
                content = f.read()

            # Should be wrapped
            lines = content.strip().split('\n')
            assert len(lines) > 1  # Multiple lines due to wrapping

        finally:
            temp_file.unlink()

    def test_cli_prose_wrap_false(self) -> None:
        """Test CLI with prose-wrap=false."""
        # Create a temporary file with long text
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.md', delete=False
        ) as f:
            f.write(
                'This is a very long paragraph that should not be'
                ' wrapped when prose wrapping is disabled.'
            )
            temp_file = Path(f.name)

        try:
            # Format with prose-wrap=false
            result = subprocess.run(
                [
                    'prettier-markdown',
                    '--prose-wrap=false',
                    '--print-width',
                    '40',
                    str(temp_file),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            assert result.returncode == 0

            # Read the formatted content
            with open(temp_file, encoding='utf-8') as f:
                content = f.read()

            # Should remain on single line (not wrapped)
            lines = [
                line for line in content.strip().split('\n') if line.strip()
            ]
            assert len(lines) == 1
            assert len(lines[0]) > 40  # Longer than print-width

        finally:
            temp_file.unlink()

    def test_cli_no_prose_wrap_option(self) -> None:
        """Test CLI with --no-prose-wrap option."""
        # Create a temporary file with long text
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.md', delete=False
        ) as f:
            f.write(
                'This is a very long paragraph that should not be'
                ' wrapped with the no-prose-wrap option.'
            )
            temp_file = Path(f.name)

        try:
            # Format with --prose-wrap false
            result = subprocess.run(
                [
                    'prettier-markdown',
                    '--prose-wrap',
                    'false',
                    '--print-width',
                    '40',
                    str(temp_file),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            assert result.returncode == 0

            # Read the formatted content
            with open(temp_file, encoding='utf-8') as f:
                content = f.read()

            # Should remain on single line (not wrapped)
            lines = [
                line for line in content.strip().split('\n') if line.strip()
            ]
            assert len(lines) == 1
            assert len(lines[0]) > 40  # Longer than print-width

        finally:
            temp_file.unlink()

    def test_cli_directory_processing(self) -> None:
        """Test CLI processing a directory of markdown files."""
        # Create a temporary directory with markdown files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create multiple markdown files
            file1 = temp_path / 'test1.md'
            file2 = temp_path / 'test2.md'
            file3 = temp_path / 'not_markdown.txt'

            file1.write_text('# File 1\n\nThis is a long paragraph in file 1.')
            file2.write_text('# File 2\n\nThis is a long paragraph in file 2.')
            file3.write_text('This is not a markdown file.')

            # Run formatter on directory
            result = subprocess.run(
                ['prettier-markdown', str(temp_path)],
                capture_output=True,
                text=True,
                check=True,
            )

            assert result.returncode == 0
            assert f'Formatted {file1}' in result.stdout
            assert f'Formatted {file2}' in result.stdout
            # Should not process non-markdown files
            assert str(file3) not in result.stdout

    def test_cli_version(self) -> None:
        """Test CLI version option."""
        result = subprocess.run(
            ['prettier-markdown', '--version'],
            capture_output=True,
            text=True,
            check=True,
        )

        assert result.returncode == 0
        assert '0.1.0' in result.stdout

    def test_cli_help(self) -> None:
        """Test CLI help option."""
        result = subprocess.run(
            ['prettier-markdown', '--help'],
            capture_output=True,
            text=True,
            check=True,
        )

        assert result.returncode == 0
        assert 'Format Markdown files' in result.stdout
        assert '--prose-wrap' in result.stdout
        assert '--print-width' in result.stdout
        assert '--check' in result.stdout

    def test_cli_no_files(self) -> None:
        """Test CLI with no files specified."""
        result = subprocess.run(
            ['prettier-markdown'], capture_output=True, text=True
        )

        assert result.returncode == 2
        assert 'Missing argument' in result.stderr

    def test_cli_nonexistent_file(self) -> None:
        """Test CLI with non-existent file."""
        result = subprocess.run(
            ['prettier-markdown', 'nonexistent.md'],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert 'does not exist' in result.stderr
