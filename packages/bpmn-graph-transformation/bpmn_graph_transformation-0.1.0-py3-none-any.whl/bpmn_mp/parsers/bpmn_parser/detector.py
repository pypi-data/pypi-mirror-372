def detect_format(file_content: str, filename: str) -> bool:
    return "<bpmn:definitions" in file_content or filename.lower().endswith(".bpmn")
