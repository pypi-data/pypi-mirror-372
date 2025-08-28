"""Command-line interface for prettier-markdown."""

import sys
from pathlib import Path
import difflib

import click
from importlib.metadata import version

from prettier_markdown.formatter import (
    MarkdownFormatter,
    MarkdownFormatterOptions,
)


@click.command(
    context_settings={'help_option_names': ['-h', '--help']},
)
@click.argument(
    'files',
    nargs=-1,
    required=True,
    metavar='FILES...',
    type=click.Path(path_type=Path),
)
@click.option(
    '--check',
    is_flag=True,
    help='Check if files are formatted without making changes',
)
@click.option(
    '--print-width',
    type=int,
    default=79,
    show_default=True,
    help='Maximum line width',
)
@click.option(
    '--prose-wrap',
    type=bool,
    default=True,
    show_default=True,
    help='Wrap prose to print-width',
)
@click.version_option(
    version=version('prettier-markdown'), prog_name='prettier-markdown'
)
def main(  # noqa: C901
        files: tuple[Path, ...],
        check: bool,
        print_width: int,
        prose_wrap: bool,
) -> None:
    """Format Markdown files."""
    options = MarkdownFormatterOptions(
        print_width=print_width,
        prose_wrap=prose_wrap,
    )

    formatter = MarkdownFormatter(options)

    markdown_files = collect_markdown_files(files)

    if not markdown_files:
        click.echo('No markdown files found.', err=True)
        sys.exit(1)

    exit_code = 0

    for file_path in markdown_files:
        try:
            with open(file_path, encoding='utf-8') as f:
                original_content = f.read()

            formatted_content = formatter.format(original_content)

            if check:
                if original_content != formatted_content:
                    click.echo(f'{file_path}: File is re-formatted')
                    show_diff(original_content, formatted_content, file_path)
                    exit_code = 1
                else:
                    click.echo(f'{file_path}: File is not changed')

            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(formatted_content)

                click.echo(f'Formatted {file_path}')

        except Exception as e:
            click.echo(f'Error processing {file_path}: {e}', err=True)
            exit_code = 1

    sys.exit(exit_code)


def show_diff(original: str, formatted: str, file_path: Path) -> None:
    """Display a colored diff between original and formatted content."""
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        formatted.splitlines(keepends=True),
        fromfile=f'{file_path} (original)',
        tofile=f'{file_path} (formatted)',
        lineterm='',
    )

    for line in diff:
        if line.startswith('+++') or line.startswith('---'):
            click.echo(
                click.style(line, fg='white', bold=True),
                nl=False,
            )
        elif line.startswith('@@'):
            click.echo(click.style(line, fg='cyan'), nl=False)
        elif line.startswith('+'):
            click.echo(click.style(line, fg='green'), nl=False)
        elif line.startswith('-'):
            click.echo(click.style(line, fg='red'), nl=False)
        else:
            click.echo(line, nl=False)


def collect_markdown_files(file_paths: tuple[Path, ...]) -> list[Path]:
    """Collect all markdown files from the given paths."""
    markdown_files = []

    for path in file_paths:
        if not path.exists():
            click.echo(f'Error: {path} does not exist', err=True)
            sys.exit(1)

        if path.is_file():
            if path.suffix.lower() in ('.md', '.markdown'):
                markdown_files.append(path)

        elif path.is_dir():
            for ext in ('*.md', '*.markdown'):
                markdown_files.extend(path.glob(f'**/{ext}'))

        else:
            click.echo(
                f'Warning: {path} is not a valid file or directory',
                err=True,
            )

    return sorted(set(markdown_files))


if __name__ == '__main__':
    main()
