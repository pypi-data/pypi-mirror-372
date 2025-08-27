def detect_format(file_content: str, filename: str) -> bool:
    return "<Definitions" in file_content or filename.lower().endswith(".xml")
