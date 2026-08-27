from dataclasses import dataclass

@dataclass
class Document:
    """
    Represents a document after it has been loaded.
    """
    filename: str
    title: str
    source: str
    category: str
    pages: int
    text: str
    year: int | None