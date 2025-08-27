from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Union

SourceLike = Union[str, bytes, Path]

class ParserPlugin(ABC):
    plugin_id: str
    priority: int = 0

    @abstractmethod
    def detect(self, source: SourceLike, filename: Optional[str] = None) -> float: ...

    @abstractmethod
    def parse(self, source: SourceLike, filename: Optional[str] = None) -> Dict[str, Any]: ...
