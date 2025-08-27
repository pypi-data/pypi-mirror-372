import os
from typing import Dict, Any, Tuple

from src.bpmn_mp.parsers.bpmn_parser.parser import parse_file as parse_file_bpmn
from src.bpmn_mp.parsers.xpdl_parser.parser import parse_file as parse_file_xpdl
from src.bpmn_mp.parsers.xml_parser.parser import parse_definitions as parse_file_xml
from src.bpmn_mp.parsers.native_parser.parser import parse_file as parse_file_native

def dispatch_parse(file_path: str) -> Tuple[Dict[str, Any], str]:
    file_ext = os.path.splitext(file_path)[-1].lower()
    
    if file_ext == ".bpmn":
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        return parse_file_bpmn(file_content), "bpmn"

    elif file_ext == ".xpdl":
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        return parse_file_xpdl(file_content), "xpdl"

    elif file_ext == ".xml":
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        attributes = parse_file_xml(file_content)
        return {"extendedAttributes": attributes}, "xml"

    elif file_ext == ".bpm":
        with open(file_path, "rb") as f:
            file_content = f.read()
        return parse_file_native(file_content), "native"

    else:
        raise ValueError(f"Unsupported file extension: {file_ext}")