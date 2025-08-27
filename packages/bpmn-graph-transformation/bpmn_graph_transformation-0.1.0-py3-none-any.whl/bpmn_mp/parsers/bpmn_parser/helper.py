import os
import re
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Union, List, Dict, Optional, Tuple
from io import StringIO


def parse_extended_attribute_definitions(collab_elem: ET.Element) -> Dict[str, dict]:
    """
    Parse seluruh BizagiExtendedAttributeDefinition dan ColumnAttribute dalam collaboration.
    Output: dictionary dengan ID sebagai key.
    """
    definitions = {}
    ns = {"bizagi": "http://www.bizagi.com/bpmn20"}

    # 1. Ambil definisi utama (BizagiExtendedAttributeDefinition)
    for def_elem in collab_elem.findall(".//bizagi:BizagiExtendedAttributeDefinition", ns):
        attr_id = def_elem.attrib.get("Id")
        attr_type = def_elem.attrib.get("Type")
        name_elem = def_elem.find("bizagi:Name", ns)
        desc_elem = def_elem.find("bizagi:Description", ns)
        options_elem = def_elem.find("bizagi:Options", ns)
        elem_types = def_elem.find("bizagi:ElementTypes", ns)

        options = []
        if options_elem is not None:
            options = [opt.text for opt in options_elem.findall("bizagi:string", ns) if opt.text]

        types = []
        if elem_types is not None:
            types = [et.attrib.get("Type") for et in elem_types.findall("bizagi:AttributeElementType", ns)]

        definitions[attr_id] = {
            "id": attr_id,
            "type": attr_type,
            "name": name_elem.text if name_elem is not None else "",
            "description": desc_elem.text if desc_elem is not None else "",
            "options": options,
            "elementTypes": types
        }

        # 2. Tambahkan juga definisi kolom dari TableColumns
        for col in def_elem.findall(".//bizagi:ColumnAttribute", ns):
            col_id = col.attrib.get("Id")
            col_type = col.attrib.get("Type")
            col_name = col.findtext("bizagi:Name", default="", namespaces=ns)
            col_desc = col.findtext("bizagi:Description", default="", namespaces=ns)
            col_opts_elem = col.find("bizagi:Options", ns)
            col_options = []
            if col_opts_elem is not None:
                col_options = [opt.text for opt in col_opts_elem.findall("bizagi:string", ns) if opt.text]

            definitions[col_id] = {
                "id": col_id,
                "type": col_type,
                "name": col_name,
                "description": col_desc,
                "options": col_options,
                "elementTypes": []
            }

    return definitions

def parse_extended_attribute_values(ext_elem: ET.Element, definitions: Dict[str, dict]) -> List[dict]:
    """
    Parse seluruh BizagiExtendedAttributeValue di dalam satu elemen BPMN.
    Menggunakan 'definitions' untuk mengambil nama dari atribut berdasarkan ID.
    Output: list of dict.
    """
    results = []
    ns = {"bizagi": "http://www.bizagi.com/bpmn20"}
    values_root = ext_elem.find(".//bizagi:BizagiExtendedAttributeValues", ns)
    if values_root is None:
        return []

    for val in values_root.findall("bizagi:BizagiExtendedAttributeValue", ns):
        attr_id = val.attrib.get("Id")
        attr_type = val.attrib.get("Type")
        content = val.findtext("bizagi:Content", default="", namespaces=ns)
        display = val.findtext("bizagi:DisplayValue", default="", namespaces=ns)

        # Ambil nama dari definisi jika tersedia
        attr_name = definitions.get(attr_id, {}).get("name", "")

        # TableValues
        table = []
        for row in val.findall(".//bizagi:RowValues", ns):
            row_data = []
            for cell in row.findall("bizagi:ExtendedAttributeValue", ns):
                row_data.append({
                    "id": cell.attrib.get("Id"),
                    "type": cell.attrib.get("Type"),
                    "content": cell.findtext("bizagi:Content", default="", namespaces=ns)
                })
            table.append(row_data)

        results.append({
            "id": attr_id,
            "type": attr_type,
            "name": attr_name,
            "content": content,
            "displayValue": display,
            "tableValues": table
        })

    return results



def build_lane_and_pool_mappings(root: ET.Element) -> Tuple[Dict[str, str], Dict[str, str]]:
    lane_map = {}
    pool_map = {}

    # 1. Ambil semua koordinat elemen diagram
    shape_coords = {}
    for shape in root.findall(".//{*}BPMNShape"):
        bpmn_element = shape.attrib.get("bpmnElement")
        bounds = shape.find("{*}Bounds")
        if bpmn_element and bounds is not None:
            x = float(bounds.attrib.get("x", "0"))
            y = float(bounds.attrib.get("y", "0"))
            w = float(bounds.attrib.get("width", "0"))
            h = float(bounds.attrib.get("height", "0"))
            shape_coords[bpmn_element] = {
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "center": (x + w / 2, y + h / 2)
            }

    # 2. Ambil posisi koordinat lane
    lane_positions = {}
    for lane in root.findall(".//{*}lane"):
        lane_id = lane.attrib.get("id")
        for shape in root.findall(".//{*}BPMNShape"):
            if shape.attrib.get("bpmnElement") == lane_id:
                bounds = shape.find("{*}Bounds")
                if bounds is not None:
                    x = float(bounds.attrib.get("x", "0"))
                    y = float(bounds.attrib.get("y", "0"))
                    w = float(bounds.attrib.get("width", "0"))
                    h = float(bounds.attrib.get("height", "0"))
                    lane_positions[lane_id] = {
                        "x": x, "y": y, "w": w, "h": h
                    }

    # 3. Mapping langsung dari <flowNodeRef>
    for lane in root.findall(".//{*}lane"):
        lane_id = lane.attrib.get("id")
        for node_ref in lane.findall(".//{*}flowNodeRef"):
            elem_id = node_ref.text
            if elem_id:
                lane_map[elem_id] = lane_id

    # 4. Fallback berdasarkan posisi koordinat shape
    for elem_id, coords in shape_coords.items():
        if elem_id in lane_map:
            continue
        cx, cy = coords["center"]
        for lane_id, lane_box in lane_positions.items():
            if (lane_box["x"] <= cx <= lane_box["x"] + lane_box["w"]) and (lane_box["y"] <= cy <= lane_box["y"] + lane_box["h"]):
                lane_map[elem_id] = lane_id
                break

    # 5. Fallback lanjutan berdasarkan incoming/outgoing (selain sequenceFlow)
    for elem_id in shape_coords:
        if elem_id in lane_map:
            continue
        elem_node = root.find(f".//*[@id='{elem_id}']")
        if elem_node is None:
            continue
        tag = elem_node.tag.lower()
        if "sequenceflow" in tag:
            continue

        incoming = get_element_text_list(elem_node, "{*}incoming")
        outgoing = get_element_text_list(elem_node, "{*}outgoing")

        lane_candidates = set()

        for flow_id in incoming:
            flow_lane = lane_map.get(flow_id)
            if flow_lane:
                lane_candidates.add(flow_lane)

        for flow_id in outgoing:
            flow_lane = lane_map.get(flow_id)
            if flow_lane:
                lane_candidates.add(flow_lane)

        if len(lane_candidates) == 1:
            lane_map[elem_id] = list(lane_candidates)[0]

    # 6. SequenceFlow hanya diberikan lane jika source & target berada di 1 lane
    for seq in root.findall(".//{*}sequenceFlow"):
        seq_id = seq.attrib.get("id")
        source = seq.attrib.get("sourceRef")
        target = seq.attrib.get("targetRef")
        if not source or not target:
            continue
        source_lane = lane_map.get(source)
        target_lane = lane_map.get(target)
        if source_lane and target_lane and source_lane == target_lane:
            lane_map[seq_id] = source_lane
        else:
            lane_map[seq_id] = None

    # 7. Mapping pool_id berdasarkan process → participant
    process_to_pool = {
        p.attrib.get("processRef"): p.attrib.get("id")
        for p in root.findall(".//{*}participant")
        if p.attrib.get("processRef") and p.attrib.get("id")
    }

    for process in root.findall(".//{*}process"):
        process_id = process.attrib.get("id")
        pool_id = process_id  # default: gunakan process_id
        for elem in process.iter():
            elem_id = elem.attrib.get("id")
            if elem_id:
                pool_map[elem_id] = pool_id

    return lane_map, pool_map



def get_element_text_list(elem: ET.Element, tag_name: str) -> List[str]:
    return [child.text for child in elem.findall(f".//{tag_name}") if child.text]


def get_clean_tag(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def parse_xml_file(content: str):
    tree = ET.parse(StringIO(content))
    return tree.getroot()


def get_positions_by_element_id(root: ET.Element) -> Dict[str, dict]:
    """
    Mengembalikan mapping element_id → posisi (x, y, width, height atau waypoints).
    """
    positions = {}

    # 1. BPMNShape (untuk task/event/gateway/dataobject, dll)
    for shape in root.findall(".//{*}BPMNShape"):
        elem_id = shape.attrib.get("bpmnElement")
        bounds = shape.find("{*}Bounds")
        if elem_id and bounds is not None:
            positions[elem_id] = {
                "x": bounds.attrib.get("x"),
                "y": bounds.attrib.get("y"),
                "width": bounds.attrib.get("width"),
                "height": bounds.attrib.get("height")
            }

    # 2. BPMNEdge (untuk sequenceFlow/messageFlow/association)
    for edge in root.findall(".//{*}BPMNEdge"):
        elem_id = edge.attrib.get("bpmnElement")
        waypoints = edge.findall("{*}waypoint")
        if elem_id and waypoints:
            positions[elem_id] = {
                "waypoints": [
                    {"x": wp.attrib.get("x"), "y": wp.attrib.get("y")}
                    for wp in waypoints
                ]
            }

    return positions




def get_event_subtype(elem: ET.Element) -> str:
    """
    Untuk startEvent, endEvent, intermediateCatchEvent, intermediateThrowEvent:
    - Jika ada >1 EventDefinition: MultipleStart/MultipleEnd/MultipleIntermediate
    - Jika ada parallelMultiple="true": parallelMultiple
    - Jika hanya satu EventDefinition: sesuai namanya
    - Kalau tidak ada EventDefinition: NoneStart/NoneEnd/NoneIntermediate
    """
    base_tag = get_clean_tag(elem.tag)
    tag_map = {
        "startEvent": "Start",
        "endEvent": "End",
        "intermediateCatchEvent": "Intermediate",
        "intermediateThrowEvent": "Intermediate"
    }
    none_type = f"None{tag_map.get(base_tag, base_tag)}"

    # Cek parallelMultiple
    if elem.attrib.get("parallelMultiple") == "true":
        return "parallelMultiple"

    # Ambil semua child EventDefinition
    event_defs = [get_clean_tag(child.tag) for child in elem if get_clean_tag(child.tag).endswith("EventDefinition")]

    if len(event_defs) == 0:
        return none_type
    elif len(event_defs) == 1:
        return event_defs[0]
    else:
        if base_tag == "startEvent":
            return "MultipleStart"
        elif base_tag == "endEvent":
            return "MultipleEnd"
        else:  # intermediateCatchEvent atau intermediateThrowEvent
            return "MultipleIntermediate"
        


def parse_element(elem: ET.Element, definitions: Dict[str, dict], positions_map: Dict[str, dict]) -> dict:
    """
    Parse satu elemen BPMN menjadi dictionary standar.
    """
    tag = get_clean_tag(elem.tag).lower()
    elem_id = elem.attrib.get("id")
    elem_name = elem.attrib.get("name", "")
    position = positions_map.get(elem_id, {})

    # Ambil incoming dan outgoing
    incoming = get_element_text_list(elem, "{*}incoming")
    outgoing = get_element_text_list(elem, "{*}outgoing")

    # Ambil documentation
    doc_node = elem.find(".//{*}documentation")
    documentation = doc_node.text if doc_node is not None else ""

    # Ambil extensionElements
    extension_node = elem.find(".//{*}extensionElements")
    extended_values = parse_extended_attribute_values(extension_node, definitions) if extension_node is not None else []

    # Penentuan subtype
    subtype = tag
    if tag in ["startevent", "endevent", "intermediatecatchevent", "intermediatethrowevent"]:
        subtype = get_event_subtype(elem)
    elif tag == "eventbasedgateway":
        # eventGatewayType: "Exclusive" / "Parallel"
        ev_type = elem.attrib.get("eventGatewayType", "").lower()
        if ev_type == "exclusive":
            subtype = "eventBasedGatewayExclusive"
        elif ev_type == "parallel":
            subtype = "eventBasedGatewayParallel"
        else:
            subtype = "eventBasedGateway"

    return {
        "id": elem_id,
        "name": elem_name,
        "type": tag,
        "subType": subtype,
        "incoming": incoming,
        "outgoing": outgoing,
        "documentation": documentation,
        "extensionElements": {
            "extendedAttributeValues": extended_values
        },
        "position": position,
        "properties": {
            "pool_id": None,
            "lane_id": None,
            "label": None
        }
    }


def detect_source_tool(root: ET.Element) -> str:
    """
    Deteksi tool sumber dari file BPMN berdasarkan atribut, tag, dan namespace di elemen root.
    """
    attribs = []
    
    # Gabungkan semua key dan value dari atribut root
    for k, v in root.attrib.items():
        attribs.append(str(k).lower())
        attribs.append(str(v).lower())

    # Sertakan juga tag root
    attribs.append(str(root.tag).lower())

    # Gabungkan semua string jadi satu
    source_string = " ".join(attribs)

    # Deteksi berdasarkan kata kunci
    if "bizagi" in source_string:
        return "Bizagi Modeler"
    if "camunda" in source_string:
        return "Camunda Modeler"
    if "bpmn.io" in source_string:
        return "bpmn.io Modeler"
    if "bonita" in source_string:
        return "Bonita Studio Modeler"

    return ""





def extract_metadata_bpmn(root: ET.Element, file_path: Optional[Path]) -> dict:
    """
    Ekstrak metadata dari file BPMN, termasuk dari struktur XML dan properti file.
    """
    metadata = {
        "id": None,
        "name": None,
        "version": None,
        "author": "",
        "created": "",
        "modified": "",
        "source_format": "bpmn",
        "source_tool": "",
        "parser_version": ""
    }

    # Nama file (tanpa ekstensi) dan tanggal
    if file_path:
        metadata["name"] = file_path.stem

        # Ambil deklarasi XML version dari baris pertama
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for _ in range(3):
                    line = f.readline()
                    match = re.search(r'<\?xml\s+version="([^"]+)"', line)
                    if match:
                        metadata["version"] = match.group(1)
                        break
            if metadata["version"] is None:
                metadata["version"] = "unknown"
        except Exception:
            metadata["version"] = "unknown"

        # File creation & modification time
        try:
            file_stats = os.stat(file_path)
            metadata["created"] = datetime.fromtimestamp(file_stats.st_ctime).isoformat()
            metadata["modified"] = datetime.fromtimestamp(file_stats.st_mtime).isoformat()
        except Exception:
            pass

    # --- DETEKSI SOURCE TOOL ---
    metadata["source_tool"] = detect_source_tool(root)

    # Author (dari ModifiedBy attribute di salah satu node Bizagi)
    for elem in root.iter():
        if "ModifiedBy" in elem.attrib:
            metadata["author"] = elem.attrib["ModifiedBy"]
            break

    return metadata