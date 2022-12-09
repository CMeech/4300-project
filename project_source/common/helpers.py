import json
from typing import Any
from rsocket.payload import Payload

from project_source.common.constants import ENCODE_TYPE

def create_payload(data) -> Payload:
    return Payload(json.dumps(data).encode(ENCODE_TYPE))

def parse_payload(payload: Payload) -> Any:
    return json.loads(payload.data)

def parse_byte_payload(payload: Payload) -> bytes:
    return payload.data

def create_byte_payload(data: bytes) -> Payload:
    return Payload(data)