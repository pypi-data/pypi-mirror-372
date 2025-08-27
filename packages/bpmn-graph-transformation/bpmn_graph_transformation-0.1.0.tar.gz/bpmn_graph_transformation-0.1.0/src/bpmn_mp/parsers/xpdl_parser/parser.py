import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional
from src.bpmn_mp.parsers.xpdl_parser.helper import (
    parse_xml_file,
    get_element_details_xpdl,
    build_lane_and_pool_mappings_xpdl,
    extract_metadata_xpdl,
)

def parse_file(content: str, file_path: Optional[Path] = None) -> dict:
    result = {
        "metadata": {},
        "flowElements": [],
        "messageFlows": [],
        "pools": [],
        "lanes": []
    }

    root = parse_xml_file(content)
    ns = {'xpdl': 'http://www.wfmc.org/2009/XPDL2.2'}

    # --- Metadata ---
    result["metadata"] = extract_metadata_xpdl(root, file_path)

    # Pemetaan Pool dan Lane berdasarkan data grafis
    lane_map, pool_map = build_lane_and_pool_mappings_xpdl(root, ns)

    # Ekstrak definisi Pools dan Lanes, lalu isi flowNodeRefs
    for pool_elem in root.findall(".//xpdl:Pool", ns):
        result["pools"].append({
            "id": pool_elem.attrib.get("Id"),
            "name": pool_elem.attrib.get("Name"),
            "processRef": pool_elem.attrib.get("Process")
        })

    for lane_elem in root.findall(".//xpdl:Lane", ns):
        lane_id = lane_elem.attrib.get("Id")
        result["lanes"].append({
            "id": lane_id,
            "name": lane_elem.attrib.get("Name"),
            "flowNodeRefs": [k for k, v in lane_map.items() if v == lane_id]
        })

    # Parse semua elemen (Activities dan Transitions)
    all_elements = {}
    for process in root.findall(".//xpdl:WorkflowProcess", ns):
        # Parse Activities (Tasks, Events, Gateways)
        for element in process.findall("xpdl:Activities/xpdl:Activity", ns):
            elem_id = element.attrib.get("Id")
            details = get_element_details_xpdl(element, ns)
            
            extended_attrs_list = [
                {
                    "id": None,
                    "type": None,
                    "name": attr.attrib.get("Name").replace("_x0020_", " "), 
                    "documentation": None,
                    "content": attr.attrib.get("Value"),
                    "displayValue": "",
                    "tableValues": [],
                }
                for attr in element.findall("xpdl:ExtendedAttributes/xpdl:ExtendedAttribute", ns)
            ]
            
            doc_node = element.find("xpdl:Documentation", ns)
            documentation = doc_node.text if doc_node is not None else ""

            position = {}
            graphics_info = element.find("xpdl:NodeGraphicsInfos/xpdl:NodeGraphicsInfo", ns)
            if graphics_info is not None:
                coords = graphics_info.find("xpdl:Coordinates", ns)
                if coords is not None:
                    position = {
                        "x": coords.attrib.get("XCoordinate"),
                        "y": coords.attrib.get("YCoordinate"),
                        "width": graphics_info.attrib.get("Width"),
                        "height": graphics_info.attrib.get("Height")
                    }

            all_elements[elem_id] = {
                "id": elem_id,
                "name": element.attrib.get("Name", ""),
                "type": details["type"],
                "subType": details["subType"],
                "incoming": [],
                "outgoing": [],
                "documentation": documentation,
                "extensionElements": {"extendedAttributeValues": extended_attrs_list},
                "position": position,
                "properties": {
                    "pool_id": pool_map.get(elem_id),
                    "lane_id": lane_map.get(elem_id),
                    "label": element.attrib.get("Name", "")
                }
            }

        # Parse Transitions (Sequence Flows)
        for transition in process.findall("xpdl:Transitions/xpdl:Transition", ns):
            trans_id = transition.attrib.get("Id")
            source_id = transition.attrib.get("From")
            target_id = transition.attrib.get("To")

            # Buat entri untuk transisi
            all_elements[trans_id] = {
                "id": trans_id,
                "name": transition.attrib.get("Name", ""),
                "type": "sequenceFlow",
                "subType": "sequenceFlow",
                "incoming": [source_id] if source_id else [],
                "outgoing": [target_id] if target_id else [],
                "documentation": transition.findtext("xpdl:Description", "", ns),
                "extensionElements": {},
                "position": {},
                "properties": {
                    "pool_id": pool_map.get(trans_id),
                    "lane_id": lane_map.get(trans_id),
                    "sourceRef": source_id,
                    "targetRef": target_id,
                    "label": transition.attrib.get("Name", "")
                }
            }
            
            # Hubungkan ke elemen sumber dan target
            if source_id and source_id in all_elements:
                all_elements[source_id]["outgoing"].append(trans_id)
            if target_id and target_id in all_elements:
                all_elements[target_id]["incoming"].append(trans_id)

    result["flowElements"] = list(all_elements.values())

    # Parse Message Flows
    for msg_flow in root.findall(".//xpdl:MessageFlow", ns):
        result["messageFlows"].append({
            "id": msg_flow.attrib.get("Id"),
            "name": msg_flow.attrib.get("Name", ""),
            "type": "messageFlow",
            "incoming": [msg_flow.attrib.get("Source")],
            "outgoing": [msg_flow.attrib.get("Target")]
        })
        
    return result