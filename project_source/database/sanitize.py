import re


def sanitize_alphanumeric(text: str) -> str:
    pattern = "[^0-9a-zA-Z]+"
    if text != None:
        sanitized = re.sub(pattern, "", text)
    else:
        sanitized = None
    return sanitized