"""Split Markdown sections and repeat their heading context on every fragment."""
import re

from .chunking import RecursiveChunker


class HeadingChunker:
    def __init__(self, chunk_size: int = 500) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text.strip():
            return []
        chunks = []
        headings: list[tuple[int, str]] = []
        body: list[str] = []
        fence = None

        def flush():
            content = "".join(body).strip()
            if not content:
                return
            prefix = "\n".join(title for _, title in headings)
            prefix = prefix + "\n\n" if prefix else ""
            budget = self.chunk_size - len(prefix)
            if budget <= 0:
                raise ValueError("Heading context exceeds chunk_size; increase chunk_size")
            for fragment in RecursiveChunker(chunk_size=budget).chunk(content):
                if fragment.strip():
                    chunks.append(prefix + fragment.strip())
            body.clear()

        for line in text.splitlines(keepends=True):
            fence_match = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
            if fence_match:
                marker = fence_match.group(1)
                if fence is None:
                    fence = marker
                elif marker[0] == fence[0] and len(marker) >= len(fence):
                    fence = None
                body.append(line)
                continue
            heading = re.match(r"^ {0,3}(#{1,6})\s+(.+?)\s*$", line) if fence is None else None
            if heading:
                flush()
                level = len(heading.group(1))
                headings = [(depth, title) for depth, title in headings if depth < level]
                headings.append((level, line.strip()))
            else:
                body.append(line)
        flush()
        if not chunks and headings:
            title = "\n".join(value for _, value in headings)
            if len(title) > self.chunk_size:
                raise ValueError("Heading context exceeds chunk_size; increase chunk_size")
            return [title]
        return chunks
