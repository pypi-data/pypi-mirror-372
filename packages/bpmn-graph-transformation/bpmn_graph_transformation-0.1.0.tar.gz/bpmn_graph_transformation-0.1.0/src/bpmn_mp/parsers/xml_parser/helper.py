from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Union
from io import StringIO

def parse_xml_file(content: str):
    try:
        tree = ET.parse(StringIO(content))
        return tree.getroot()
    except ET.ParseError as e:
        raise ValueError(f"Error parsing XML file: {filepath}. Detail: {e}")
