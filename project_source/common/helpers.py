#
# helpers.py
#
# AUTHOR: Cassius Meeches
#
# PURPOSE: Implements some helper functions to convert
# Python data into data that can be sent via RSocket.
#
import json
from typing import Any
from rsocket.payload import Payload

from project_source.common.constants import ENCODE_TYPE

#
# create_payload
#
# PURPOSE: Takes in a dictionary and encodes it as JSON
# so that it can be sent to another host via an RSocket
# message
# 
# PARAMS:
# data - a dictionary object
#
# Returns a Payload object with 'data' as its payload.
#
def create_payload(data) -> Payload:
    if data:
        return Payload(json.dumps(data).encode(ENCODE_TYPE))
    else:
        return Payload()


#
# parse_payload
#
# PURPOSE: Parses the JSON data from a Payload object so Python
# can use it.
# 
# PARAMS:
# payload - The payload from an RSocket message.
#
# Returns the payload of a message. Should be a dictionary.
#
def parse_payload(payload: Payload) -> Any:
    return json.loads(payload.data)

#
# parse_byte_payload
#
# PURPOSE: Parses byte data from a Payload object so Python
# can use it.
# 
# PARAMS:
# payload - The payload from an RSocket message.
#
# Returns raw byte data.
#
def parse_byte_payload(payload: Payload) -> bytes:
    return payload.data


#
# create_byte_payload
#
# PURPOSE: Adds raw byte data to the payload section of
# an RSocket message.
# 
# PARAMS:
# data - raw bytes from a file
#
# Returns a Payload object with 'data' as its payload.
#
def create_byte_payload(data: bytes) -> Payload:
    if data:  
        return Payload(data)
    else:
        return Payload()