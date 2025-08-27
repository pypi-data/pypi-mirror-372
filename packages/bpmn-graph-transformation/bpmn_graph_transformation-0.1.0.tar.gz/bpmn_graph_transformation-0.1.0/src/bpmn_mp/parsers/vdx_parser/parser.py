from typing import Optional
from pathlib import Path

from src.bpmn_mp.parsers.vdx_parser.helper import (
    parse_xml_file,
    extract_metadata_vdx,
    extract_shapes_and_connects
)

def parse_file(content: str, file_path: Optional[Path] = None) -> dict:
    """
    Parse file .vdx (Visio) menjadi format JSON standar.
    """
    root = parse_xml_file(content)
    metadata = extract_metadata_vdx(root, file_path)

    shapes, connects = extract_shapes_and_connects(root)

    result = {
        "metadata": metadata,
        "flowElements": shapes + connects,
        "messageFlows": [],
        "pools": [],
        "lanes": []
    }

    return result
