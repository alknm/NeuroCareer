"""Content of the master's dissertation, organised as a list of blocks.

Each module exposes a `BLOCKS` list. Block types understood by
`09_build_dissertation.py`:

    ('h1', text)              - Heading 1 (chapter / unnumbered top section)
    ('h2', text)              - Heading 2 (1.1, 1.2, ...)
    ('h3', text)              - Heading 3 (1.1.1, ...)
    ('p', text)               - body paragraph, justified, first-line 0.75 cm
    ('p_center', text)        - centered paragraph, no indent
    ('p_right', text)         - right-aligned, no indent
    ('p_noindent', text)      - justified, no first-line indent
    ('p_bold_center', text)   - bold centered
    ('fig', rel_path, cap)    - figure (path relative to system/) + caption
    ('table', headers, rows, caption)  - Word table
    ('pagebreak',)            - force page break
    ('blank',)                - empty paragraph (vertical spacer)
"""
from __future__ import annotations

from . import (
    frontmatter,
    intro,
    chapter1,
    chapter2,
    chapter3,
    chapter4,
    chapter5,
    chapter6,
    conclusion,
    bibliography,
    appendices,
    back_matter,
)


def annotation_blocks():
    """Резюме / Түйіндеме / Summary — placed before the table of contents."""
    return frontmatter.ANNOTATION_BLOCKS


def all_sections():
    """Yield one block list per top-level section, in document order."""
    yield frontmatter.BLOCKS
    yield intro.BLOCKS
    yield chapter1.BLOCKS
    yield chapter2.BLOCKS
    yield chapter3.BLOCKS
    yield chapter4.BLOCKS
    yield chapter5.BLOCKS
    yield chapter6.BLOCKS
    yield conclusion.BLOCKS
    yield bibliography.BLOCKS
    yield appendices.BLOCKS
    yield back_matter.BLOCKS
