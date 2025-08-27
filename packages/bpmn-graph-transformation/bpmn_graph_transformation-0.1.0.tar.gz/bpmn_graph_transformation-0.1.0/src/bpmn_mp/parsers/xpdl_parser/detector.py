def detect_format(file_content: str, filename: str) -> bool:
    return "<Package" in file_content or filename.lower().endswith(".xpdl")
