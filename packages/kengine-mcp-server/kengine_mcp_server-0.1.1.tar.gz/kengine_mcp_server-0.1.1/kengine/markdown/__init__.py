__all__ = ('fix_markdown', )


from .mermaid_fixer import fix_mermaid
from .markdown_fixer import extract_markdown_content

def fix_markdown(markdown: str) -> str:
    markdown = extract_markdown_content(markdown)
    markdown = fix_mermaid(markdown)
    return markdown