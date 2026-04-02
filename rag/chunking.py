import re

from langchain_core.documents import Document


def parse_constitution(text: str, *, source: str = "1999 Constitution") -> list[Document]:
    chunks: list[Document] = []
    current_chapter: str | None = None
    current_part: str | None = None
    current_section: str | None = None
    current_title: str | None = None
    buffer: list[str] = []

    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            continue

        if re.match(r"CHAPTER\s+[IVX]+", line):
            current_chapter = line
            continue

        if re.match(r"PART\s+[IVX]+", line):
            current_part = line
            continue

        section_match = re.match(r"(\d+[A-Z]?)\.\s+(.*)", line)
        if section_match:
            if current_section:
                chunks.append(
                    Document(
                        page_content="\n".join(buffer),
                        metadata={
                            "chapter": current_chapter,
                            "part": current_part,
                            "section": current_section,
                            "title": current_title,
                            "source": source,
                        },
                    )
                )
            current_section = section_match.group(1)
            current_title = section_match.group(2)
            buffer = [f"Section {current_section} - {current_title}"]
            continue

        if current_section:
            buffer.append(line)

    if current_section:
        chunks.append(
            Document(
                page_content="\n".join(buffer),
                metadata={
                    "chapter": current_chapter,
                    "part": current_part,
                    "section": current_section,
                    "title": current_title,
                    "source": source,
                },
            )
        )

    return chunks
