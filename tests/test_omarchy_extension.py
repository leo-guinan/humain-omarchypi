import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "omarchy" / "extension"


class OmarchyExtensionBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((EXT / "manifest.json").read_text())
        cls.source = "\n".join((EXT / name).read_text() for name in ("background.js", "content.js", "popup.js"))

    def test_manifest_is_explicit_popup_activated_mv3(self):
        self.assertEqual(self.manifest["manifest_version"], 3)
        self.assertEqual(self.manifest["action"]["default_popup"], "popup.html")
        self.assertIn("activeTab", self.manifest["permissions"])
        self.assertIn("http://127.0.0.1:8787/*", self.manifest["host_permissions"])

    def test_extension_does_not_send_raw_page_material(self):
        self.assertNotIn("page_text", self.source)
        self.assertNotIn("page_html", self.source)
        self.assertNotIn("document.body.innerText", self.source)
        self.assertIn("message.pointer", self.source)

    def test_extension_preserves_fail_closed_states(self):
        self.assertIn("local adapter unavailable", self.source)
        self.assertIn("resolution_state", self.source)
        self.assertIn("p.resolution_state", self.source)
        self.assertIn("only clean HTTPS public pointers are accepted", self.source)


if __name__ == "__main__":
    unittest.main()
