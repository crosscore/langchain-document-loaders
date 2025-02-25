# fitz.pyi
from typing import List, Any

class Document:
    def __init__(self, filename: str) -> None: ...
    def get_page_labels(self) -> List[str]: ...
    def close(self) -> None: ...
    def __len__(self) -> int: ...
    def __getitem__(self, index: int) -> 'Page': ...

class Page:
    def get_text(self, option: str = ...) -> Any: ...

def open(filename: str) -> Document: ...
