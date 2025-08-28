# Test Document

This is a very long paragraph that should be wrapped when the prose-wrap option is enabled because it exceeds the print-width limit that we have configured for our markdown formatter.

## Lists

- This is a bullet point with some text
- Another bullet point that is quite long and should be wrapped properly when it exceeds the configured print-width setting
- A third point

1. Numbered list item
2. Another numbered item that is very long and should demonstrate proper wrapping behavior when formatting markdown content

## Code Block

```python
def hello_world():
    print("Hello, World!")
```

## Table

| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Long content here | Short | More content |

## Quote

> This is a blockquote that contains some text that might be long enough to test the wrapping behavior of our markdown formatter implementation.

---

**Bold text** and *italic text* and `inline code`.

[Link text](https://example.com)

![Alt text](image.jpg)
