from typing import List, Dict, Any
from src.bpmn_mp.parsers.xml_parser.helper import parse_xml_file

def parse_definitions(content: str) -> List[Dict[str, Any]]:
    root = parse_xml_file(content)
    
    final_result_list = []

    for attr_elem in root.findall(".//ExtendedAttribute"):
        options = [opt.text for opt in attr_elem.findall("Options/string") if opt.text is not None]
        
        table_columns = [
            {
                "id": col.attrib.get("Id"),
                "type": col.attrib.get("Type"),
                "name": col.findtext("Name"),
                "description": col.findtext("Description"),
                "options": [opt.text for opt in col.findall("Options/string") if opt.text is not None]
            } for col in attr_elem.findall("TableColumns/ColumnAttribute")
        ]

        element_types = [
            el_type.attrib.get("Type") 
            for el_type in attr_elem.findall("ElementTypes/AttributeElementType")
        ]

        attribute_payload = {
            "id": attr_elem.attrib.get("Id"),
            "type": attr_elem.attrib.get("Type"),
            "name": attr_elem.findtext("Name"),
            "documentation": attr_elem.findtext("Description"), 
            "content": "",
            "displayValue": "", 
            "tableValues": table_columns, 
        }
        
        wrapper_object = {
            "extensionElements": {
                "extendedAttributeValues": attribute_payload
            }
        }

        final_result_list.append(wrapper_object)

    return final_result_list
