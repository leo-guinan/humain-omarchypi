import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "swarm"))

from health_receipt import build_receipt, canonical_bytes, validate_receipt  # noqa: E402


class HealthReceiptTests(unittest.TestCase):
    def test_receipt_is_bounded_and_deterministic(self):
        node = {
            "schema": "omarchypi.node.v1",
            "node_id": "omarchypi-abc123456789",
            "role": "edge-display",
            "capabilities": ["health"],
            "network_scope": "lan-only",
        }
        receipt = build_receipt(node, context_service="active", desktop="observed", version="0.2.0")
        self.assertTrue(validate_receipt(receipt))
        self.assertEqual(canonical_bytes(receipt), canonical_bytes(json.loads(json.dumps(receipt))))
        encoded = json.dumps(receipt)
        self.assertNotIn("password", encoded.lower())
        self.assertNotIn("clipboard", encoded.lower())
        self.assertNotIn("history", encoded.lower())
        self.assertNotIn("private", encoded.lower())

    def test_invalid_scope_and_extra_payload_fail(self):
        node = {
            "schema": "omarchypi.node.v1",
            "node_id": "omarchypi-abc123456789",
            "role": "edge-display",
            "capabilities": ["health"],
            "network_scope": "public",
        }
        with self.assertRaises(ValueError):
            build_receipt(node, context_service="active", desktop="observed", version="0.2.0")

        node["network_scope"] = "lan-only"
        receipt = build_receipt(node, context_service="active", desktop="observed", version="0.2.0")
        receipt["health"]["arbitrary_payload"] = "no"
        self.assertFalse(validate_receipt(receipt))


if __name__ == "__main__":
    unittest.main()
