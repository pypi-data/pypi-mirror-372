"""Markdown formatting logic."""

import textwrap
from typing import Any

import mistune


class MarkdownFormatterOptions:
    """Configuration options for markdown formatting."""

    def __init__(
            self,
            print_width: int = 79,
            prose_wrap: bool = True,
    ) -> None:
        self.print_width = print_width
        self.prose_wrap = prose_wrap


class MarkdownFormatter:
    """Formats markdown text using mistune parser."""

    def __init__(
            self, options: MarkdownFormatterOptions | None = None
    ) -> None:
        self.options = options or MarkdownFormatterOptions()
        self.markdown = mistune.create_markdown(
            renderer='ast', plugins=['strikethrough', 'footnotes', 'table']
        )
        self._output: list[str] = []

    def format(self, content: str) -> str:
        """Format the markdown content and return formatted string."""
        self._output = []
        ast = self.markdown(content)

        for node in ast:
            if isinstance(node, dict):
                self._format_node(node)

        result = ''.join(self._output)
        return result.rstrip() + '\n'

    def _format_node(self, node: dict[str, Any], level: int = 0) -> None:  # noqa: C901
        """Format a single AST node."""
        node_type = node['type']

        if node_type == 'paragraph':
            self._format_paragraph(node)
        elif node_type == 'heading':
            self._format_heading(node)
        elif node_type == 'list':
            self._format_list(node, level)
        elif node_type == 'list_item':
            self._format_list_item(node, level)
        elif node_type == 'block_quote':
            self._format_block_quote(node)
        elif node_type == 'block_code':
            self._format_block_code(node)
        elif node_type == 'thematic_break':
            self._output.append('---\n\n')
        elif node_type == 'table':
            self._format_table(node)
        elif node_type == 'blank_line':
            pass
        elif node_type == 'block_text':
            self._format_paragraph(node)
        else:
            if 'children' in node:
                for child in node['children']:
                    self._format_node(child, level)

    def _format_paragraph(self, node: dict[str, Any]) -> None:
        """Format a paragraph node."""
        text = self._extract_text_content(node)

        # Normalize whitespace to handle already-wrapped text
        normalized_text = ' '.join(text.split())

        if (
            self.options.prose_wrap
            and len(normalized_text) > self.options.print_width
        ):
            wrapped_text = textwrap.fill(
                normalized_text,
                width=self.options.print_width,
                break_long_words=False,
                break_on_hyphens=True,
            )
            self._output.append(wrapped_text + '\n\n')
        else:
            self._output.append(normalized_text + '\n\n')

    def _format_heading(self, node: dict[str, Any]) -> None:
        """Format a heading node."""
        level = node.get('attrs', {}).get('level', 1)
        text = self._extract_text_content(node)
        prefix = '#' * level
        self._output.append(f'{prefix} {text}\n\n')

    def _format_list(self, node: dict[str, Any], level: int = 0) -> None:
        """Format a list node."""
        attrs = node.get('attrs', {})
        ordered = attrs.get('ordered', False)
        tight = node.get('tight', True)

        for i, item in enumerate(node.get('children', [])):
            if ordered:
                marker = f'{i + 1}.'
            else:
                marker = '-'

            self._format_list_item_with_marker(item, marker, level, tight)

        if level == 0:
            self._output.append('\n')

    def _format_list_item_with_marker(
            self, item: dict[str, Any], marker: str, level: int, tight: bool
    ) -> None:
        """Format a list item with its marker."""
        indent = '  ' * level

        if 'children' in item and item['children']:
            first_child = item['children'][0]

            if first_child['type'] == 'block_text':
                text = self._extract_text_content(first_child)
                normalized_text = ' '.join(text.split())

                if self.options.prose_wrap and len(normalized_text) > (
                    self.options.print_width - len(indent) - len(marker) - 1
                ):
                    wrapped_text = textwrap.fill(
                        normalized_text,
                        width=self.options.print_width
                        - len(indent)
                        - len(marker)
                        - 1,
                        initial_indent='',
                        subsequent_indent=' ' * (len(marker) + 1),
                        break_long_words=False,
                        break_on_hyphens=True,
                    )
                    self._output.append(f'{indent}{marker} {wrapped_text}\n')
                else:
                    self._output.append(
                        f'{indent}{marker} {normalized_text}\n'
                    )

                for child in item['children'][1:]:
                    if child['type'] == 'list':
                        self._format_list(child, level + 1)
                    else:
                        self._format_node(child, level + 1)

            else:
                self._output.append(f'{indent}{marker}\n')
                for child in item['children']:
                    if child['type'] == 'list':
                        self._format_list(child, level + 1)
                    else:
                        self._format_node(child, level + 1)

        if not tight:
            self._output.append('\n')

    def _format_list_item(self, node: dict[str, Any], level: int = 0) -> None:
        """Format a list item node (fallback method)."""
        indent = '  ' * level
        self._output.append(f'{indent}- ')

        if 'children' in node:
            for child in node['children']:
                self._format_node(child, level)

    def _format_block_quote(self, node: dict[str, Any]) -> None:
        """Format a block quote node."""
        if 'children' in node:
            temp_output: list[str] = []
            original_output = self._output
            self._output = temp_output

            for child in node['children']:
                self._format_node(child)

            self._output = original_output

            quoted_text = ''.join(temp_output).rstrip()
            # Normalize whitespace in the quoted text for consistent wrapping
            normalized_quoted = ' '.join(quoted_text.split())

            # Apply wrapping to the blockquote content if needed
            if (
                self.options.prose_wrap
                and len(normalized_quoted) > self.options.print_width - 2
            ):
                wrapped_quoted = textwrap.fill(
                    normalized_quoted,
                    width=self.options.print_width
                    - 2,  # Account for "> " prefix
                    break_long_words=False,
                    break_on_hyphens=True,
                )
                lines = wrapped_quoted.split('\n')
            else:
                lines = [normalized_quoted] if normalized_quoted else []

            for line in lines:
                if line.strip():
                    self._output.append(f'> {line}\n')
                else:
                    self._output.append('>\n')

            self._output.append('\n')

    def _format_block_code(self, node: dict[str, Any]) -> None:
        """Format a code block node."""
        attrs = node.get('attrs', {})
        info = attrs.get('info', '').strip()
        code = node.get('raw', '')

        if info:
            self._output.append(f'```{info}\n')
        else:
            self._output.append('```\n')

        self._output.append(code)
        if not code.endswith('\n'):
            self._output.append('\n')

        self._output.append('```\n\n')

    def _format_table(self, node: dict[str, Any]) -> None:  # noqa: C901
        """Format a table node."""
        if 'children' in node:
            rows = []
            header_row = None

            for child in node['children']:
                if child['type'] == 'table_head':
                    if 'children' in child:
                        header_cells = []
                        for cell in child['children']:
                            if cell['type'] == 'table_cell':
                                cell_text = self._extract_text_content(cell)
                                header_cells.append(cell_text)

                        if header_cells:
                            header_row = header_cells

                elif child['type'] == 'table_body':
                    if 'children' in child:
                        for row_node in child['children']:
                            if row_node['type'] == 'table_row':
                                row = self._extract_table_row(row_node)
                                if row:
                                    rows.append(row)

            if header_row or rows:
                all_rows = []
                if header_row:
                    all_rows.append(header_row)

                all_rows.extend(rows)
                self._format_table_rows(
                    all_rows, has_header=header_row is not None
                )

    def _extract_table_row(self, row_node: dict[str, Any]) -> list[str]:
        """Extract text from table row cells."""
        cells = []
        if 'children' in row_node:
            for cell in row_node['children']:
                if cell['type'] == 'table_cell':
                    cell_text = self._extract_text_content(cell)
                    cells.append(cell_text)

        return cells

    def _format_table_rows(
            self, rows: list[list[str]], has_header: bool = False
    ) -> None:
        """Format table rows with proper alignment."""
        if not rows:
            return

        max_cols = max(len(row) for row in rows)
        col_widths = [0] * max_cols

        for row in rows:
            for i, cell in enumerate(row):
                if i < max_cols:
                    col_widths[i] = max(col_widths[i], len(cell))

        for i, row in enumerate(rows):
            formatted_cells = []
            for j in range(max_cols):
                cell = row[j] if j < len(row) else ''
                formatted_cells.append(cell.ljust(col_widths[j]))

            self._output.append('| ' + ' | '.join(formatted_cells) + ' |\n')

            if has_header and i == 0:
                separators = ['-' * width for width in col_widths]
                self._output.append('| ' + ' | '.join(separators) + ' |\n')

        self._output.append('\n')

    def _extract_text_content(self, node: dict[str, Any]) -> str:  # noqa: C901
        """Extract plain text content from a node."""
        if isinstance(node, str):
            return node

        if node['type'] == 'text':
            return str(node.get('raw', ''))

        if node['type'] == 'softbreak':
            return ' '

        if node['type'] == 'linebreak':
            return '\n'

        if node['type'] == 'emphasis':
            text = self._extract_children_text(node)
            return f'*{text}*'

        if node['type'] == 'strong':
            text = self._extract_children_text(node)
            return f'**{text}**'

        if node['type'] == 'codespan':
            return f'`{node.get("raw", "")}`'

        if node['type'] == 'link':
            text = self._extract_children_text(node)
            attrs = node.get('attrs', {})
            url = attrs.get('url', '')
            title = attrs.get('title', '')
            if title:
                return f'[{text}]({url} "{title}")'

            return f'[{text}]({url})'

        if node['type'] == 'image':
            alt = self._extract_children_text(node)
            attrs = node.get('attrs', {})
            url = attrs.get('url', '')
            title = attrs.get('title', '')
            if title:
                return f'![{alt}]({url} "{title}")'

            return f'![{alt}]({url})'

        if node['type'] == 'strikethrough':
            text = self._extract_children_text(node)
            return f'~~{text}~~'

        if 'children' in node:
            return self._extract_children_text(node)

        return str(node.get('raw', ''))

    def _extract_children_text(self, node: dict[str, Any]) -> str:
        """Extract text content from node children."""
        if 'children' not in node:
            return ''

        result = []
        for child in node['children']:
            result.append(self._extract_text_content(child))

        return ''.join(result)
