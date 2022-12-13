import json
from typing import Any
from rsocket.payload import Payload

from project_source.common.constants import ENCODE_TYPE

def create_payload(data) -> Payload:
    if data:
        return Payload(json.dumps(data).encode(ENCODE_TYPE))
    else:
        return Payload()

def parse_payload(payload: Payload) -> Any:
    return json.loads(payload.data)

def parse_byte_payload(payload: Payload) -> bytes:
    return payload.data

def create_byte_payload(data: bytes) -> Payload:
    if data:  
        return Payload(data)
    else:
        return Payload()