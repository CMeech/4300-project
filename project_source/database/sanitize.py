#
# sanitize.py
#
# AUTHOR: Cassius Meeches
#
# PURPOSE: Implements helper functions for sanitizing strings.
#
import re


#
# sanitize_alphanumeric
#
# PURPOSE: Removes any characters from a string that aren't
# alphabetic or numbers.
#
# PARAMS:
# text - the provided text
#
# Returns the sanitized string.
#
def sanitize_alphanumeric(text: str) -> str:
    pattern = "[^0-9a-zA-Z]+"
    if text != None:
        sanitized = re.sub(pattern, "", text)
    else:
        sanitized = None
    return sanitized