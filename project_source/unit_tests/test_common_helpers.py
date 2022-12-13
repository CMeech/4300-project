import json
import unittest
from project_source.common.constants import ENCODE_TYPE

from project_source.common.helpers import create_byte_payload, create_payload, parse_byte_payload, parse_payload

class TestCommonHelpers(unittest.TestCase):

    def test_json_payload(self):
        dictionary = {
            "message": "hello"
        }
        payload = create_payload(dictionary)
        self.assertEqual(payload.data, json.dumps(dictionary).encode(ENCODE_TYPE))
        parsed = parse_payload(payload)
        self.assertEqual(dictionary, parsed)
        pass

    def test_byte_payload(self):
        dictionary = {
            "message": "hello"
        }
        payload = create_byte_payload(json.dumps(dictionary).encode(ENCODE_TYPE))
        parsed = parse_byte_payload(payload)
        self.assertEqual(json.dumps(dictionary).encode(ENCODE_TYPE), parsed)

    def test_empty_payloads(self):
        payload = create_payload(None)
        byte_payload = create_byte_payload(None)
        self.assertIsNone(payload.data)
        self.assertIsNone(byte_payload.data)