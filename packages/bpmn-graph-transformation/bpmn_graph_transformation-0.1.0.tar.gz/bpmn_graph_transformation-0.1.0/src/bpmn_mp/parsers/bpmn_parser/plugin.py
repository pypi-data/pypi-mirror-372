from pathlib import Path
from typing import Optional, Dict, Any, Union
from ..base import ParserPlugin, SourceLike
from .parser import parse_file

class Plugin(ParserPlugin):
    plugin_id = "bpmn"
    priority = 10   # BPMN kita anggap paling spesifik

    def detect(self, source: SourceLike, filename: Optional[str] = None) -> float:
        """
        Beri skor kecocokan file/isi dengan format BPMN.
        """
        name = (filename or str(source)).lower() if filename or isinstance(source, (str, Path)) else ""

        # Deteksi by ekstensi
        if name.endswith(".bpmn"):
            return 0.95

        # Deteksi by isi string (xmlns bpmn / <bpmn:definitions>)
        try:
            text = (
                Path(source).read_text("utf-8") if isinstance(source, Path) and source.exists()
                else source.decode("utf-8", "ignore") if isinstance(source, bytes)
                else str(source)
            )
        except Exception:
            text = ""

        if "xmlns:bpmn" in text or "<bpmn:definitions" in text:
            return 0.9

        return 0.0

    def parse(self, source: SourceLike, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Panggil parser lama (parse_file) dengan menyiapkan content string.
        """
        if isinstance(source, bytes):
            content = source.decode("utf-8", "ignore")
            return parse_file(content, file_path=Path(filename) if filename else None)

        if isinstance(source, Path):
            return parse_file(source.read_text("utf-8"), file_path=source)

        if isinstance(source, str) and Path(source).exists():
            p = Path(source)
            return parse_file(p.read_text("utf-8"), file_path=p)

        # Asumsi: source sudah string XML mentah
        return parse_file(str(source), file_path=Path(filename) if filename else None)
