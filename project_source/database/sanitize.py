import re


def sanitize_alphanumeric(text: str) -> str:
    pattern = "[^0-9a-zA-Z]+"
    sanitized = re.sub(pattern, "", text)
    return sanitized