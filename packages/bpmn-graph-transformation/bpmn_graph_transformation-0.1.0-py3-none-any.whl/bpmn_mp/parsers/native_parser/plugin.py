from pathlib import Path
from typing import Optional, Dict, Any
from ..base import ParserPlugin, SourceLike
from .parser import parse_file

class Plugin(ParserPlugin):
    plugin_id = "native"
    priority = 7  # di bawah BPMN/XPDL, di atas XML generic

    def detect(self, source: SourceLike, filename: Optional[str] = None) -> float:
        name = (filename or (str(source) if isinstance(source, (str, Path)) else "")).lower()
        # .bpm adalah container zip, detection paling andal pakai ekstensi
        return 0.95 if name.endswith(".bpm") else 0.0

    def parse(self, source: SourceLike, filename: Optional[str] = None) -> Dict[str, Any]:
        # Parser native butuh BYTES
        if isinstance(source, Path):
            return parse_file(source.read_bytes(), file_path=source)
        if isinstance(source, str) and Path(source).exists():
            p = Path(source)
            return parse_file(p.read_bytes(), file_path=p)
        if isinstance(source, bytes):
            return parse_file(source, file_path=Path(filename) if filename else None)
        # fallback: anggap string → bytes
        return parse_file(str(source).encode("utf-8"), file_path=Path(filename) if filename else None)
