import zipfile
import xml.etree.ElementTree as ET
from io import BytesIO
from typing import Dict, List, Optional, Tuple


def extract_zip_bytes(zip_bytes: bytes) -> Dict[str, bytes]:
    result = {}
    with zipfile.ZipFile(BytesIO(zip_bytes), 'r') as zf:
        for name in zf.namelist():
            result[name] = zf.read(name)
    return result


def load_extended_attributes(xml_bytes: bytes) -> Dict[str, List[dict]]:
    element_attributes = {}
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return element_attributes

    for element in root.findall("ElementAttributeValues"):
        element_id = element.get("ElementId")
        if not element_id:
            continue

        values_node = element.find("Values")
        if values_node is None:
            continue

        attrs = []
        for attr in values_node.findall("ExtendedAttributeValue"):
            table_values = []
            table_node = attr.find("TableValues")
            if table_node is not None:
                for row in table_node.findall("RowValues"):
                    row_data = []
                    for cell in row.findall("ExtendedAttributeValue"):
                        row_data.append({
                            "id": cell.get("Id"),
                            "type": cell.get("Type", "LongText"),
                            "content": cell.findtext("Content", default="")
                        })
                    table_values.append(row_data)

            attrs.append({
                "id": attr.get("Id", ""),
                "type": attr.get("Type", "LongText"),
                "name": attr.get("Name", ""),
                "content": attr.findtext("Content", default=""),
                "displayValue": attr.get("DisplayValue", ""),
                "tableValues": table_values
            })
        element_attributes[element_id] = attrs

    return element_attributes


def extract_metadata_bpm(root: ET.Element) -> dict:
    ns = "{http://www.wfmc.org/2009/XPDL2.2}"
    header = root.find(f"{ns}PackageHeader")
    redef_header = root.find(f"{ns}RedefinableHeader")

    return {
        "id": None,
        "name": root.findtext(f"{ns}Name", default="Unnamed"),
        "version": redef_header.findtext(f"{ns}Version", default="1.0") if redef_header is not None else "1.0",
        "author": redef_header.findtext(f"{ns}Author", default="") if redef_header is not None else "",
        "created": header.findtext(f"{ns}Created", default="") if header is not None else "",
        "modified": header.findtext(f"{ns}ModificationDate", default="") if header is not None else "",
        "source_format": "bpmn",
        "source_tool": "Bizagi Modeler",
        "parser_version": ""
    }


def get_clean_tag(tag: str) -> str:
    """Remove namespace from tag."""
    return tag.split("}", 1)[-1] if "}" in tag else tag

BPMN_FLOW_TAGS = {
    "startevent", "task", "usertask", "servicetask", "sendtask", "receivetask", "manualtask", "businessruletask", "scripttask",
    "callactivity", "subprocess", "intermediatethrowevent", "intermediatecatchevent",
    "exclusivegateway", "parallelgateway", "inclusivegateway", "eventbasedgateway", "complexgateway",
    "endevent", "sequenceflow", "association", "messageflow", "dataobject", "datastorereference", "textannotation"
}


def is_flow_element(tag: str) -> bool:
    return get_clean_tag(tag).lower() in BPMN_FLOW_TAGS


def is_message_flow(tag: str) -> bool:
    return get_clean_tag(tag).lower() == "messageflow"

def get_element_text_list(elem, xpath):
    """Ambil list text dari child dengan xpath tertentu."""
    return [e.text for e in elem.findall(xpath) if e.text]

def determine_type_and_subtype(tag: ET.Element) -> tuple[str, str]:
    ns = "{http://www.wfmc.org/2009/XPDL2.2}"
    if tag.tag.endswith("Activity"):
        event = tag.find(f"{ns}Event")
        if event is not None:
            start = event.find(f"{ns}StartEvent")
            inter = event.find(f"{ns}IntermediateEvent")
            end = event.find(f"{ns}EndEvent")
            if start is not None:
                trigger = start.attrib.get("Trigger", "None")
                if trigger == "Multiple":
                    return "startevent", "multipleEventDefinition"
                elif trigger == "ParallelMultiple":
                    return "startevent", "parallelMultipleEventDefinition"
                return "startevent", f"{trigger.lower()}EventDefinition" if trigger != "None" else "noneEventDefinition"
            if inter is not None:
                trigger = inter.attrib.get("Trigger", "None")
                return "intermediatecatchevent", f"{trigger.lower()}EventDefinition" if trigger != "None" else "noneEventDefinition"
            if end is not None:
                result = end.attrib.get("Result", "None")
                return "endevent", f"{result.lower()}EventDefinition" if result != "None" else "noneEventDefinition"

        if tag.find(f"{ns}BlockActivity") is not None:
            return "subprocess", "subprocess"
        if tag.find(f"{ns}Implementation/{ns}SubFlow") is not None:
            return "callactivity", "callactivity"

        task = tag.find(f"{ns}Implementation/{ns}Task")
        if task is not None:
            for t in task:
                suffix = get_clean_tag(t.tag).lower()
                if suffix in BPMN_FLOW_TAGS:
                    return "task", suffix
            return "task", "nonetask"

        route = tag.find(f"{ns}Route")
        if route is not None:
            gtype = route.attrib.get("GatewayType", "exclusive").lower()
            return "gateway", f"{gtype}gateway"

        return "task", "nonetask"

    else:
        tag_type = get_clean_tag(tag.tag).lower()
        return tag_type, tag_type




def build_pool_and_lane_mappings(root: ET.Element) -> Tuple[Dict[str, str], Dict[str, str]]:
    ns = "{http://www.wfmc.org/2009/XPDL2.2}"
    lane_map: Dict[str, str] = {}
    pool_map: Dict[str, str] = {}

    # 1. Ambil posisi koordinat lane
    lane_positions = {}
    for lane in root.findall(f".//{ns}Lane"):
        lane_id = lane.attrib.get("Id")
        ginfo = lane.find(f".//{ns}NodeGraphicsInfo")
        coords = ginfo.find(f"{ns}Coordinates") if ginfo is not None else None
        if lane_id and coords is not None:
            x = float(coords.attrib.get("XCoordinate", "0"))
            y = float(coords.attrib.get("YCoordinate", "0"))
            w = float(ginfo.attrib.get("Width", "0"))
            h = float(ginfo.attrib.get("Height", "0"))
            lane_positions[lane_id] = {"x": x, "y": y, "w": w, "h": h}

    # 2. Ambil semua koordinat shape diagram
    shape_coords = {}
    for elem in root.findall(f".//*[@Id]"):
        elem_id = elem.attrib.get("Id")
        ginfo = elem.find(f".//{ns}NodeGraphicsInfo")
        coords = ginfo.find(f"{ns}Coordinates") if ginfo is not None else None
        if elem_id and coords is not None:
            x = float(coords.attrib.get("XCoordinate", "0"))
            y = float(coords.attrib.get("YCoordinate", "0"))
            w = float(ginfo.attrib.get("Width", "0"))
            h = float(ginfo.attrib.get("Height", "0"))
            center = (x + w / 2, y + h / 2)
            shape_coords[elem_id] = {"x": x, "y": y, "width": w, "height": h, "center": center}

    # 3. Mapping langsung dari <FlowNodeRef> pada Lane (jika ada)
    for lane in root.findall(f".//{ns}Lane"):
        lane_id = lane.attrib.get("Id")
        for flow_node_ref in lane.findall(f"{ns}FlowNodeRef"):
            ref_id = flow_node_ref.text
            if ref_id:
                lane_map[ref_id] = lane_id

    # 4. Mapping berdasarkan posisi center shape di area lane
    for elem_id, coords in shape_coords.items():
        if elem_id in lane_map:
            continue
        cx, cy = coords["center"]
        for lane_id, lane_box in lane_positions.items():
            if (lane_box["x"] <= cx <= lane_box["x"] + lane_box["w"]) and \
               (lane_box["y"] <= cy <= lane_box["y"] + lane_box["h"]):
                lane_map[elem_id] = lane_id
                break

    # 5. Fallback: assign lane dari salah satu incoming/outgoing transition (kecuali messageflow)
    transitions = []
    for t in root.findall(f".//{ns}Transition"):
        transitions.append({
            "Id": t.attrib.get("Id"),
            "From": t.attrib.get("From"),
            "To": t.attrib.get("To"),
        })

    # Cari semua id messageflow agar bisa dikecualikan
    messageflow_ids = set()
    for mf in root.findall(f".//{ns}MessageFlow"):
        mf_id = mf.attrib.get("Id")
        if mf_id:
            messageflow_ids.add(mf_id)

    for elem in root.findall(f".//*[@Id]"):
        elem_id = elem.attrib.get("Id")
        if not elem_id or elem_id in lane_map or elem_id in messageflow_ids:
            continue
        tag = get_clean_tag(elem.tag).lower()
        if tag == "transition":
            continue
        if elem.find(f".//{ns}StartEvent") is not None or elem.find(f".//{ns}EndEvent") is not None:
            continue

        incomings = [t['From'] for t in transitions if t['To'] == elem_id and t['From']]
        outgoings = [t['To'] for t in transitions if t['From'] == elem_id and t['To']]
        candidates = [lane_map[x] for x in incomings + outgoings if x in lane_map]
        if candidates:
            lane_map[elem_id] = candidates[0]  # pilih salah satu

    # 6. SequenceFlow (Transition): hanya diberi lane jika source & target ada di lane yang sama
    for trans in root.findall(f".//{ns}Transition"):
        seq_id = trans.attrib.get("Id")
        source = trans.attrib.get("From")
        target = trans.attrib.get("To")
        if not source or not target:
            continue
        source_lane = lane_map.get(source)
        target_lane = lane_map.get(target)
        if source_lane and target_lane and source_lane == target_lane:
            lane_map[seq_id] = source_lane

    # 7. Mapping pool_id berdasarkan Pool.Process → WorkflowProcess
    process_to_pool = {}
    for pool in root.findall(f".//{ns}Pool"):
        pool_id = pool.attrib.get("Id")
        proc_ref = pool.attrib.get("Process")
        if pool_id and proc_ref:
            process_to_pool[proc_ref] = pool_id

    for process in root.findall(f".//{ns}WorkflowProcess"):
        proc_id = process.attrib.get("Id")
        pool_id = process_to_pool.get(proc_id, None)
        for tag in process.iter():
            el_id = tag.attrib.get("Id")
            if el_id:
                pool_map[el_id] = pool_id

    return lane_map, pool_map