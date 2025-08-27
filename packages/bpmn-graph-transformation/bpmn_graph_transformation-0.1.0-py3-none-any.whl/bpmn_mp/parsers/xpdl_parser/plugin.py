# src/bpmn_mp/parsers/xpdl_parser/plugin.py
from pathlib import Path
from typing import Optional, Dict, Any, Union
from ..base import ParserPlugin, SourceLike
from .parser import parse_file

class Plugin(ParserPlugin):
    plugin_id = "xpdl"
    priority = 8  # di bawah BPMN, di atas Native/XML generic

    def detect(self, source: SourceLike, filename: Optional[str] = None) -> float:
        """
        Deteksi file XPDL.
        Heuristik:
        - Ekstensi .xpdl -> tinggi
        - Isi mengandung namespace XPDL 2.2 -> tinggi
        """
        name = (filename or str(source)).lower() if filename or isinstance(source, (str, Path)) else ""

        # 1) Berdasarkan ekstensi
        if name.endswith(".xpdl"):
            return 0.95

        # 2) Berdasarkan isi
        try:
            text = (
                Path(source).read_text("utf-8") if isinstance(source, Path) and source.exists()
                else source.decode("utf-8", "ignore") if isinstance(source, bytes)
                else str(source)
            )
        except Exception:
            text = ""

        # XPDL 2.2 namespace: http://www.wfmc.org/2009/XPDL2.2
        if "http://www.wfmc.org/2009/XPDL2.2" in text or "<Package" in text:
            return 0.9

        return 0.0

    def parse(self, source: SourceLike, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Bungkus parser lama. XPDL parser membutuhkan string XML.
        """
        if isinstance(source, Path):
            return parse_file(source.read_text("utf-8"), file_path=source)

        if isinstance(source, str) and Path(source).exists():
            p = Path(source)
            return parse_file(p.read_text("utf-8"), file_path=p)

        if isinstance(source, bytes):
            return parse_file(source.decode("utf-8", "ignore"),
                              file_path=Path(filename) if filename else None)

        # Asumsi: source sudah string XML mentah
        return parse_file(str(source), file_path=Path(filename) if filename else None)
