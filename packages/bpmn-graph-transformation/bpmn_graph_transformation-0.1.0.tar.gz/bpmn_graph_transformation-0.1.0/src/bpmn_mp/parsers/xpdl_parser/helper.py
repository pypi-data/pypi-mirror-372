from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Union, Dict, Any, Tuple, Optional
from io import StringIO
import os
from datetime import datetime


def parse_xml_file(content: str):
    tree = ET.parse(StringIO(content))
    return tree.getroot()

def get_clean_tag(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag

def get_element_details_xpdl(element: ET.Element, ns: Dict[str, str]) -> Dict[str, Any]:
    details = {"type": "task", "subType": "task"}  

    event_node = element.find("xpdl:Event", ns)
    if event_node is not None:
        if event_node.find("xpdl:StartEvent", ns) is not None:
            details["type"] = "startEvent"
            details["subType"] = event_node.find("xpdl:StartEvent", ns).attrib.get("Trigger")
        elif event_node.find("xpdl:IntermediateEvent", ns) is not None:
            trigger_node = event_node.find("xpdl:IntermediateEvent", ns)
            details["subType"] = trigger_node.attrib.get("Trigger")

            # Cek apakah ini THROW atau CATCH event
            if trigger_node.attrib.get("CatchThrow") == "THROW" or \
               trigger_node.find(".//xpdl:TriggerResultLink[@CatchThrow='THROW']", ns) is not None:
                details["type"] = "intermediateThrowEvent"
            else:
                details["type"] = "intermediateCatchEvent"
        elif event_node.find("xpdl:EndEvent", ns) is not None:
            details["type"] = "endEvent"
            details["subType"] = event_node.find("xpdl:EndEvent", ns).attrib.get("Result")
        return details

    # Cek Gateway (Route)
    route_node = element.find("xpdl:Route", ns)
    if route_node is not None:
        gateway_type = route_node.attrib.get("GatewayType", "Exclusive")
        details["type"] = f"{gateway_type.lower()}Gateway"
        details["subType"] = gateway_type
        return details

    # Cek Implementasi Task
    task_node = element.find("xpdl:Implementation/xpdl:Task", ns)
    if task_node is not None:
        if task_node.find("xpdl:TaskUser", ns) is not None: details["subType"] = "userTask"
        elif task_node.find("xpdl:TaskService", ns) is not None: details["subType"] = "serviceTask"
        elif task_node.find("xpdl:TaskScript", ns) is not None: details["subType"] = "scriptTask"
        elif task_node.find("xpdl:TaskSend", ns) is not None: details["subType"] = "sendTask"
        elif task_node.find("xpdl:TaskReceive", ns) is not None: details["subType"] = "receiveTask"
        elif task_node.find("xpdl:TaskManual", ns) is not None: details["subType"] = "manualTask"
        elif task_node.find("xpdl:TaskBusinessRule", ns) is not None: details["subType"] = "businessRuleTask"
    
    # Cek SubFlow (SubProcess)
    if element.find("xpdl:Implementation/xpdl:SubFlow", ns) is not None or \
       element.find("xpdl:BlockActivity", ns) is not None:
        details["type"] = "subProcess"
        details["subType"] = None

    return details


def build_lane_and_pool_mappings_xpdl(root: ET.Element, ns: dict) -> Tuple[Dict[str, str], Dict[str, str]]:
    lane_map = {}
    pool_map = {}

    # Ambil semua koordinat pool
    pool_positions = {}
    for pool in root.findall(".//xpdl:Pool", ns):
        pool_id = pool.attrib.get("Id")
        graphics = pool.find("xpdl:NodeGraphicsInfos/xpdl:NodeGraphicsInfo", ns)
        if graphics is not None:
            coords = graphics.find("xpdl:Coordinates", ns)
            if coords is not None:
                pool_positions[pool_id] = {
                    "x": float(coords.attrib.get("XCoordinate", "0")),
                    "y": float(coords.attrib.get("YCoordinate", "0")),
                    "width": float(graphics.attrib.get("Width", "0")),
                    "height": float(graphics.attrib.get("Height", "0")),
                }

    # Ambil semua koordinat lane
    lane_positions = {}
    for lane in root.findall(".//xpdl:Lane", ns):
        lane_id = lane.attrib.get("Id")
        parent_pool_id = lane.attrib.get("ParentPool")
        pool_pos = pool_positions.get(parent_pool_id, {"x": 0, "y": 0})
        
        graphics = lane.find("xpdl:NodeGraphicsInfos/xpdl:NodeGraphicsInfo", ns)
        if graphics is not None:
            coords = graphics.find("xpdl:Coordinates", ns)
            if coords is not None:

                # Koordinat lane di XPDL relatif terhadap pool, jadi di jumlahkan
                lane_positions[lane_id] = {
                    "x": pool_pos["x"] + float(coords.attrib.get("XCoordinate", "0")),
                    "y": pool_pos["y"] + float(coords.attrib.get("YCoordinate", "0")),
                    "width": float(graphics.attrib.get("Width", "0")),
                    "height": float(graphics.attrib.get("Height", "0")),
                    "pool_id": parent_pool_id
                }

    # Ambil koordinat semua elemen (activity)
    element_coords = {}
    for activity in root.findall(".//xpdl:Activity", ns):
        activity_id = activity.attrib.get("Id")
        graphics = activity.find("xpdl:NodeGraphicsInfos/xpdl:NodeGraphicsInfo", ns)
        if graphics is not None:
            coords = graphics.find("xpdl:Coordinates", ns)
            if coords is not None:
                x = float(coords.attrib.get("XCoordinate", "0"))
                y = float(coords.attrib.get("YCoordinate", "0"))
                w = float(graphics.attrib.get("Width", "0"))
                h = float(graphics.attrib.get("Height", "0"))
                element_coords[activity_id] = {
                    "center_x": x + w / 2,
                    "center_y": y + h / 2,
                }

    # Lakukan pemetaan berdasarkan posisi
    for elem_id, coords in element_coords.items():
        cx, cy = coords["center_x"], coords["center_y"]
        
        # Prioritaskan map ke Lane
        found_in_lane = False
        for lane_id, lane_box in lane_positions.items():
            if (lane_box["x"] <= cx <= lane_box["x"] + lane_box["width"]) and \
               (lane_box["y"] <= cy <= lane_box["y"] + lane_box["height"]):
                lane_map[elem_id] = lane_id
                pool_map[elem_id] = lane_box["pool_id"]
                found_in_lane = True
                break
        
        # Jika tidak di lane, map ke Pool
        if not found_in_lane:
            for pool_id, pool_box in pool_positions.items():
                if (pool_box["x"] <= cx <= pool_box["x"] + pool_box["width"]) and \
                   (pool_box["y"] <= cy <= pool_box["y"] + pool_box["height"]):
                    pool_map[elem_id] = pool_id
                    break

    # Petakan Transition (SequenceFlow) ke lane dan pool
    for transition in root.findall(".//xpdl:Transition", ns):
        trans_id = transition.attrib.get("Id")
        source = transition.attrib.get("From")
        target = transition.attrib.get("To")

        source_lane = lane_map.get(source)
        target_lane = lane_map.get(target)

        if source_lane and source_lane == target_lane:
            lane_map[trans_id] = source_lane
        
        pool_map[trans_id] = pool_map.get(source) or pool_map.get(target)

    return lane_map, pool_map   


def extract_metadata_xpdl(root: ET.Element, file_path: Optional[Path]) -> dict:
    """
    Ekstrak metadata dari file XPDL, termasuk header package dan properti file.
    """
    metadata = {
        "id": None,
        "name": None,
        "version": "1.0",
        "author": "",
        "created": "",
        "modified": "",
        "source_format": "xpdl",
        "source_tool": "",
        "parser_version": ""
    }

    # 1. Nama file (tanpa ekstensi)
    if file_path:
        metadata["name"] = file_path.stem
        try:
            file_stats = os.stat(file_path)
            metadata["created"] = datetime.fromtimestamp(file_stats.st_ctime).isoformat()
            metadata["modified"] = datetime.fromtimestamp(file_stats.st_mtime).isoformat()
        except Exception:
            pass

    # 2. Ambil Package info
    metadata["id"] = root.attrib.get("Id")
    metadata["name"] = root.attrib.get("Name", metadata["name"])

    # 3. PackageHeader
    pkg_header = root.find("{http://www.wfmc.org/2009/XPDL2.2}PackageHeader")
    if pkg_header is not None:
        created = pkg_header.findtext("{http://www.wfmc.org/2009/XPDL2.2}Created", "")
        modified = pkg_header.findtext("{http://www.wfmc.org/2009/XPDL2.2}ModificationDate", "")
        version = pkg_header.findtext("{http://www.wfmc.org/2009/XPDL2.2}XPDLVersion", "")
        vendor = pkg_header.findtext("{http://www.wfmc.org/2009/XPDL2.2}Vendor", "")
        metadata["created"] = created or metadata["created"]
        metadata["modified"] = modified or metadata["modified"]
        metadata["version"] = version or metadata["version"]
        metadata["source_tool"] = vendor or ""

    # 4. RedefinableHeader
    redef_header = root.find("{http://www.wfmc.org/2009/XPDL2.2}RedefinableHeader")
    if redef_header is not None:
        author = redef_header.findtext("{http://www.wfmc.org/2009/XPDL2.2}Author", "")
        version2 = redef_header.findtext("{http://www.wfmc.org/2009/XPDL2.2}Version", "")
        metadata["author"] = author or metadata["author"]
        if version2:
            metadata["version"] = version2

    return metadata