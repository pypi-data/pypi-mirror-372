import os
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict
from io import StringIO
import xml.etree.ElementTree as ET


def parse_xml_file(content: str) -> ET.Element:
    """
    Parse string XML menjadi root element.
    """
    tree = ET.parse(StringIO(content))
    return tree.getroot()


def get_clean_tag(tag: str) -> str:
    """
    Hapus namespace dari tag XML.
    """
    return tag.split("}")[-1] if "}" in tag else tag


def extract_metadata_vdx(root: ET.Element, file_path: Optional[Path]) -> dict:
    """
    Ekstrak metadata dari file VDX Visio.
    """
    metadata = {
        "id": None,
        "name": None,
        "version": None,
        "author": "",
        "created": "",
        "modified": "",
        "source_format": "vdx",
        "source_tool": "Microsoft Visio",
        "parser_version": ""
    }

    if file_path:
        metadata["name"] = file_path.stem
        try:
            file_stats = os.stat(file_path)
            metadata["created"] = datetime.fromtimestamp(file_stats.st_ctime).isoformat()
            metadata["modified"] = datetime.fromtimestamp(file_stats.st_mtime).isoformat()
        except Exception:
            pass

    # Cari metadata dari <DocumentProperties> tanpa namespace
    doc_props = root.find(".//DocumentProperties")
    if doc_props is not None:
        creator = doc_props.findtext("Creator")
        if creator:
            metadata["author"] = creator

    return metadata


def extract_shapes_and_connects(root: ET.Element) -> (List[dict], List[dict]):
    """
    Ambil semua elemen <Shape> dan <Connect> dari dokumen dengan namespace.
    """
    ns = {"visio": root.tag.split("}")[0].strip("{")}

    shapes_raw = root.findall(".//visio:Shape", ns)
    connects_raw = root.findall(".//visio:Connect", ns)

    shape_elements = []
    shape_dict = {}

    for shape in shapes_raw:
        shape_id = shape.attrib.get("ID")
        name = shape.attrib.get("Name", "")
        text = shape.findtext("visio:Text", default="", namespaces=ns)
        xform = shape.find("visio:XForm", ns)

        position = {}
        if xform is not None:
            for tag in ["PinX", "PinY", "Width", "Height"]:
                val = xform.findtext(f"visio:{tag}", namespaces=ns)
                if val:
                    position[tag.lower()] = val

        node = {
            "id": shape_id,
            "name": name or text,
            "type": "shape",
            "subType": None,
            "incoming": [],
            "outgoing": [],
            "documentation": "",
            "extensionElements": {
                "extendedAttributeValues": []
            },
            "position": position,
            "properties": {
                "pool_id": None,
                "lane_id": None,
                "label": None
            }
        }
        shape_elements.append(node)
        shape_dict[shape_id] = node

    edge_elements = []
    for conn in connects_raw:
        from_id = conn.attrib.get("FromSheet")
        to_id = conn.attrib.get("ToSheet")
        edge_id = f"{from_id}_to_{to_id}"

        edge = {
            "id": edge_id,
            "name": "",
            "type": "connector",
            "subType": "connect",
            "incoming": [from_id],
            "outgoing": [to_id],
            "documentation": "",
            "extensionElements": {
                "extendedAttributeValues": []
            },
            "position": {},
            "properties": {
                "pool_id": None,
                "lane_id": None,
                "label": None
            }
        }
        edge_elements.append(edge)

        # Tambahkan ke shape source/target
        if from_id in shape_dict:
            shape_dict[from_id]["outgoing"].append(edge_id)
        if to_id in shape_dict:
            shape_dict[to_id]["incoming"].append(edge_id)

    return shape_elements, edge_elements
