import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bootstrap"))

from node_identity import ensure_identity, validate_identity  # noqa: E402


class NodeIdentityTests(unittest.TestCase):
    def test_creates_unique_identity_atomically(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "node.json"
            first = ensure_identity(path, role="edge-display")
            second = ensure_identity(path, role="edge-display")
            self.assertEqual(first, second)
            self.assertEqual(first["schema"], "omarchypi.node.v1")
            self.assertEqual(first["role"], "edge-display")
            self.assertTrue(first["node_id"].startswith("omarchypi-"))
            self.assertTrue(validate_identity(json.loads(path.read_text())))

    def test_rejects_malformed_or_duplicate_identity(self):
        self.assertFalse(validate_identity({}))
        self.assertFalse(validate_identity({"schema": "omarchypi.node.v1", "node_id": "", "role": "edge-display"}))
        self.assertFalse(validate_identity({"schema": "wrong", "node_id": "omarchypi-abc123", "role": "edge-display"}))
        self.assertTrue(validate_identity({"schema": "omarchypi.node.v1", "node_id": "omarchypi-abc123", "role": "edge-display", "capabilities": [], "network_scope": "lan-only"}))


if __name__ == "__main__":
    unittest.main()
