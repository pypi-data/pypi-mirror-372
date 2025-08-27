# src/bpmn_mp/parsers/xml_parser/plugin.py
from pathlib import Path
from typing import Optional, Dict, Any, Union
from ..base import ParserPlugin, SourceLike
from .parser import parse_definitions

class Plugin(ParserPlugin):
    plugin_id = "xml"
    priority = 5   # paling umum, fallback terakhir

    def detect(self, source: SourceLike, filename: Optional[str] = None) -> float:
        """
        Deteksi file XML generik (bukan BPMN/XPDL/Native).
        """
        name = (filename or str(source)).lower() if filename or isinstance(source, (str, Path)) else ""

        if name.endswith(".xml"):
            return 0.7

        try:
            text = (
                Path(source).read_text("utf-8") if isinstance(source, Path) and source.exists()
                else source.decode("utf-8", "ignore") if isinstance(source, bytes)
                else str(source)
            )
        except Exception:
            text = ""

        # Jika ada ExtendedAttribute → kemungkinan besar file target
        return 0.8 if "<ExtendedAttribute" in text else 0.0

    def parse(self, source: SourceLike, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Panggil parser lama (parse_definitions) dan bungkus hasilnya.
        """
        if isinstance(source, Path):
            content = source.read_text("utf-8")
        elif isinstance(source, str) and Path(source).exists():
            content = Path(source).read_text("utf-8")
        elif isinstance(source, bytes):
            content = source.decode("utf-8", "ignore")
        else:
            content = str(source)

        definitions = parse_definitions(content)

        return {
            "metadata": {
                "source_format": "xml",
                "file": str(filename) if filename else None
            },
            "definitions": definitions
        }
