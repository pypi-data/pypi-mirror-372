import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

from src.bpmn_mp.parsers.bpmn_parser.helper import (
    get_clean_tag,
    parse_xml_file,
    parse_element,
    build_lane_and_pool_mappings,
    parse_extended_attribute_definitions,
    get_positions_by_element_id,
    extract_metadata_bpmn
)

# Daftar tag BPMN yang diambil
FLOW_ELEMENT_TAGS = [
    "startevent",
    "task", "usertask", "servicetask", "sendtask", "receivetask", "manualtask", "businessruletask", "scripttask",
    "callactivity", "subprocess",
    "intermediatethrowevent", "intermediatecatchevent",
    "exclusivegateway", "parallelgateway", "inclusivegateway", "eventbasedgateway", "complexgateway",
    "endevent",
    "sequenceflow",
    "association",
    "messageflow",
    "dataobject",
    "datastorereference",
    "textannotation"
]

def parse_file(content: str, file_path: Optional[Path] = None) -> dict:
    """
    Parse isi file .bpmn (dalam bentuk string XML) menjadi format JSON terstruktur.
    """
    root = parse_xml_file(content)

    # Ambil metadata dari struktur XML dan properties file
    metadata = extract_metadata_bpmn(root, file_path)

    result = {
        "metadata": metadata,
        "flowElements": [],
        "messageFlows": [],
        "pools": [],
        "lanes": []
    }

    # Mapping lane_id dan pool_id berdasarkan koordinat dan flowNodeRef
    lane_map, pool_map = build_lane_and_pool_mappings(root)

    # Ambil definisi atribut ekstensi Bizagi
    definitions = parse_extended_attribute_definitions(root)

    # Ambil koordinat posisi dari elemen diagram
    positions_map = get_positions_by_element_id(root)

    # Ambil elemen <process>
    process_nodes = [n for n in root.iter() if get_clean_tag(n.tag).lower() == "process"]
    if not process_nodes:
        raise ValueError("❌ Tidak ditemukan elemen <process> dalam file BPMN.")

    # ===============================
    # Proses: Flow Elements (ALL)
    # ===============================
    for process_node in process_nodes:
        for elem in process_node.iter():
            tag = get_clean_tag(elem.tag).lower()
            if tag in FLOW_ELEMENT_TAGS:
                parsed = parse_element(elem, definitions, positions_map)
                parsed["properties"]["lane_id"] = lane_map.get(parsed["id"])
                parsed["properties"]["pool_id"] = pool_map.get(parsed["id"])

                # Untuk sequenceFlow, isi incoming dan outgoing berdasarkan atribut
                if tag == "sequenceflow":
                    parsed["incoming"] = [elem.attrib.get("sourceRef")] if elem.attrib.get("sourceRef") else []
                    parsed["outgoing"] = [elem.attrib.get("targetRef")] if elem.attrib.get("targetRef") else []
                # Untuk association, sama seperti sequenceFlow/messageFlow
                elif tag == "association":
                    parsed["incoming"] = [elem.attrib.get("sourceRef")] if elem.attrib.get("sourceRef") else []
                    parsed["outgoing"] = [elem.attrib.get("targetRef")] if elem.attrib.get("targetRef") else []

                result["flowElements"].append(parsed)


    # ===============================
    # Proses: MessageFlow (jika ada di collaboration)
    # ===============================
    for elem in root.findall(".//{*}messageFlow"):
        parsed = parse_element(elem, definitions, positions_map)
        parsed["properties"]["lane_id"] = lane_map.get(parsed["id"])
        parsed["properties"]["pool_id"] = pool_map.get(parsed["id"])
        parsed["incoming"] = [elem.attrib.get("sourceRef")] if elem.attrib.get("sourceRef") else []
        parsed["outgoing"] = [elem.attrib.get("targetRef")] if elem.attrib.get("targetRef") else []
        result["messageFlows"].append(parsed)

    # ===============================
    # Proses: Participant → Pool
    # ===============================
    for elem in root.findall(".//{*}participant"):
        result["pools"].append({
            "id": elem.attrib.get("id"),
            "name": elem.attrib.get("name", ""),
            "processRef": elem.attrib.get("processRef")
        })

    # ===============================
    # Proses: Lane
    # ===============================
    for elem in root.findall(".//{*}lane"):
        result["lanes"].append({
            "id": elem.attrib.get("id"),
            "name": elem.attrib.get("name", ""),
            "flowNodeRefs": [n.text for n in elem.findall(".//{*}flowNodeRef") if n.text]
        })

    return result