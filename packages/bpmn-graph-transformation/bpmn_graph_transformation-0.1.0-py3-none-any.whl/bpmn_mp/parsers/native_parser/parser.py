import xml.etree.ElementTree as ET
from typing import Optional
from pathlib import Path
from src.bpmn_mp.parsers.native_parser.helper import (
    extract_zip_bytes,
    load_extended_attributes,
    extract_metadata_bpm,
    determine_type_and_subtype,
    build_pool_and_lane_mappings
)


def parse_file(file_content: bytes, file_path: Optional[Path] = None) -> dict:
    extracted = extract_zip_bytes(file_content)
    diag_file = next((f for f in extracted if f.endswith(".diag")), None)
    if not diag_file:
        raise ValueError("❌ File .diag tidak ditemukan dalam arsip .bpm")

    diag_bytes = extracted[diag_file]
    diag_extracted = extract_zip_bytes(diag_bytes)

    diagram_file = next((f for f in diag_extracted if f.endswith("Diagram.xml")), None)
    if not diagram_file:
        raise ValueError("❌ File Diagram.xml tidak ditemukan dalam .diag")

    root = ET.fromstring(diag_extracted[diagram_file])
    ns = "{http://www.wfmc.org/2009/XPDL2.2}"

    output = {
        "metadata": extract_metadata_bpm(root),
        "flowElements": [],
        "messageFlows": [],
        "pools": [],
        "lanes": []
    }

    ext_attr_map = {}
    if "ExtendedAttributeValues.xml" in diag_extracted:
        ext_attr_map = load_extended_attributes(diag_extracted["ExtendedAttributeValues.xml"])

    def extract_position_box(tag):
        info = tag.find(f".//{ns}NodeGraphicsInfo")
        if info is not None:
            coords = info.find(f".//{ns}Coordinates")
            if coords is not None:
                return {
                    "x": coords.attrib.get("XCoordinate", "0"),
                    "y": coords.attrib.get("YCoordinate", "0"),
                    "width": info.attrib.get("Width", "0"),
                    "height": info.attrib.get("Height", "0")
                }
        return {}

    def extract_waypoints(tag):
        waypoints = []
        for coords in tag.findall(f".//{ns}ConnectorGraphicsInfo/{ns}Coordinates"):
            waypoints.append({
                "x": coords.attrib.get("XCoordinate"),
                "y": coords.attrib.get("YCoordinate")
            })
        return {"waypoints": waypoints} if waypoints else {}

    for pool in root.findall(f".//{ns}Pool"):
        output["pools"].append({
            "id": pool.attrib.get("Id", ""),
            "name": pool.attrib.get("Name", ""),
            "processRef": pool.attrib.get("Process", "")
        })

    for lane in root.findall(f".//{ns}Lane"):
        output["lanes"].append({
            "id": lane.attrib.get("Id", ""),
            "name": lane.attrib.get("Name", "")
        })

    flow_elements = []
    message_flows = []

    for process in root.findall(f".//{ns}WorkflowProcess"):
        for activity in process.findall(f"{ns}Activities/{ns}Activity"):
            el_id = activity.attrib.get("Id", "")
            el_name = activity.attrib.get("Name", "")
            type_, subtype = determine_type_and_subtype(activity)
            flow_elements.append({
                "id": el_id,
                "name": el_name,
                "type": type_,
                "subType": subtype,
                "incoming": [],
                "outgoing": [],
                "documentation": "",
                "extensionElements": {
                    "extendedAttributeValues": ext_attr_map.get(el_id, [])
                },
                "position": extract_position_box(activity),
                "properties": {
                    "pool_id": None,
                    "lane_id": None,
                    "label": None
                }
            })

        for dobj in process.findall(f"{ns}DataObjects/{ns}DataObject"):
            el_id = dobj.attrib.get("Id", "")
            el_name = dobj.attrib.get("Name", "")
            flow_elements.append({
                "id": el_id,
                "name": el_name,
                "type": "dataobject",
                "subType": "dataobject",
                "incoming": [],
                "outgoing": [],
                "documentation": "",
                "extensionElements": {
                    "extendedAttributeValues": ext_attr_map.get(el_id, [])
                },
                "position": extract_position_box(dobj),
                "properties": {
                    "pool_id": None,
                    "lane_id": None,
                    "label": None
                }
            })

        for dstore in process.findall(f"{ns}DataStoreReferences/{ns}DataStoreReference"):
            el_id = dstore.attrib.get("Id", "")
            el_name = dstore.attrib.get("Name", "")
            flow_elements.append({
                "id": el_id,
                "name": el_name,
                "type": "datastorereference",
                "subType": "datastorereference",
                "incoming": [],
                "outgoing": [],
                "documentation": "",
                "extensionElements": {
                    "extendedAttributeValues": ext_attr_map.get(el_id, [])
                },
                "position": extract_position_box(dstore),
                "properties": {
                    "pool_id": None,
                    "lane_id": None,
                    "label": None
                }
            })

        for ta in process.findall(f"{ns}Artifacts/{ns}TextAnnotation"):
            el_id = ta.attrib.get("Id", "")
            el_name = ta.attrib.get("Text", "")
            flow_elements.append({
                "id": el_id,
                "name": el_name,
                "type": "textannotation",
                "subType": "textannotation",
                "incoming": [],
                "outgoing": [],
                "documentation": "",
                "extensionElements": {
                    "extendedAttributeValues": ext_attr_map.get(el_id, [])
                },
                "position": extract_position_box(ta),
                "properties": {
                    "pool_id": None,
                    "lane_id": None,
                    "label": None
                }
            })

    for elem in root.findall(f".//{ns}Transition"):
        source = elem.attrib.get("From")
        target = elem.attrib.get("To")
        flow_id = elem.attrib.get("Id")
        flow_name = elem.attrib.get("Name", "")
        sequenceflow = {
            "id": flow_id,
            "name": flow_name,
            "type": "sequenceflow",
            "subType": "sequenceflow",
            "incoming": [source],
            "outgoing": [target],
            "documentation": "",
            "extensionElements": {
                "extendedAttributeValues": ext_attr_map.get(flow_id, [])
            },
            "position": extract_waypoints(elem),
            "properties": {
                "pool_id": None,
                "lane_id": None,
                "label": None
            }
        }
        flow_elements.append(sequenceflow)
        for fe in flow_elements:
            if fe["id"] == source:
                fe["outgoing"].append(flow_id)
            if fe["id"] == target:
                fe["incoming"].append(flow_id)

    for flow in root.findall(f".//{ns}MessageFlow"):
        f_id = flow.attrib.get("Id", "")
        f_name = flow.attrib.get("Name", "")
        source = flow.attrib.get("Source")
        target = flow.attrib.get("Target")

        message_flows.append({
            "id": f_id,
            "name": f_name,
            "type": "messageflow",
            "subType": "messageflow",
            "incoming": [source],
            "outgoing": [target],
            "documentation": "",
            "extensionElements": {
                "extendedAttributeValues": ext_attr_map.get(f_id, [])
            },
            "position": extract_waypoints(flow),
            "properties": {
                "pool_id": None,
                "lane_id": None,
                "label": None
            }
        })

    for flow in root.findall(f".//{ns}MessageFlow") + root.findall(f".//{ns}Association"):
        f_id = flow.attrib.get("Id", "")
        source = flow.attrib.get("Source")
        target = flow.attrib.get("Target")
        for el in flow_elements + message_flows:
            if el["id"] == source:
                el["outgoing"].append(f_id)
            if el["id"] == target:
                el["incoming"].append(f_id)

    # Map pool_id dan lane_id
    lane_map, pool_map = build_pool_and_lane_mappings(root)
    for el in flow_elements:
        el_id = el["id"]
        if el_id in lane_map:
            el["properties"]["lane_id"] = lane_map[el_id]
        if el_id in pool_map:
            el["properties"]["pool_id"] = pool_map[el_id]

    output["flowElements"] = flow_elements
    output["messageFlows"] = message_flows
    return output
