from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from notionary.markdown.markdown_node import MarkdownNode
from notionary.blocks.mixins.captions import CaptionMarkdownNodeMixin


class BookmarkMarkdownBlockParams(BaseModel):
    url: str
    title: Optional[str] = None
    caption: Optional[str] = None


class BookmarkMarkdownNode(MarkdownNode, CaptionMarkdownNodeMixin):
    """
    Programmatic interface for creating Notion-style bookmark Markdown blocks.
    """

    def __init__(
        self, url: str, title: Optional[str] = None, caption: Optional[str] = None
    ):
        self.url = url
        self.title = title
        self.caption = caption

    @classmethod
    def from_params(cls, params: BookmarkMarkdownBlockParams) -> BookmarkMarkdownNode:
        return cls(url=params.url, title=params.title, caption=params.caption)

    def to_markdown(self) -> str:
        """Return the Markdown representation.

        Examples:
        - [bookmark](https://example.com)
        - [bookmark](https://example.com)(caption:Some caption)
        """
        # Use simple bookmark syntax like BookmarkElement
        base_markdown = f"[bookmark]({self.url})"

        # Append caption using mixin helper
        return self.append_caption_to_markdown(base_markdown, self.caption)
