import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from humain_api.omarchy_context import resolve_public_pointer, PointerError


class OmarchyContextTests(unittest.TestCase):
    def test_resolves_https_pointer_to_public_only_envelope(self):
        result = resolve_public_pointer("https://example.com/article")
        self.assertEqual(result["schema"], "humain.resolve.response.v1")
        self.assertEqual(result["resolution_state"], "public_only")
        self.assertEqual(result["pointer"], "https://example.com/article")
        self.assertEqual(result["permissions"]["actions"], [])
        self.assertEqual(result["payload"]["visibility"], "public")

    def test_rejects_non_https_and_private_url_shapes(self):
        for pointer in ("http://example.com", "file:///tmp/private", "https://example.com/a?token=secret", "https://example.com/a#private"):
            with self.subTest(pointer=pointer):
                with self.assertRaises(PointerError):
                    resolve_public_pointer(pointer)

    def test_cli_emits_waybar_json(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "omarchy" / "humainctl.py"), "waybar", "https://example.com/article"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["class"], "public-only")
        self.assertIn("example.com", payload["text"])
        self.assertIn("public_only", payload["tooltip"])


if __name__ == "__main__":
    unittest.main()
