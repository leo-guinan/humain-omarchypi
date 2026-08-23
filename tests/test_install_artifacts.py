import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class InstallArtifactTests(unittest.TestCase):
    def test_installer_is_arm_aware_and_user_level(self):
        source = (ROOT / "install.sh").read_text()
        self.assertIn('uname -m', source)
        self.assertIn('aarch64', source)
        self.assertIn('systemctl --user', source)
        self.assertNotIn('sshpass', source)
        self.assertNotIn('PRIVATE KEY', source)

    def test_service_is_loopback_adapter_path(self):
        source = (ROOT / "omarchy" / "context_server.py").read_text()
        self.assertIn('127.0.0.1', source)
        self.assertIn('/healthz', source)
        self.assertIn('/v1/context', source)

    def test_shell_module_is_explicitly_public_only(self):
        source = (ROOT / "omarchy" / "quickshell-humain" / "custom-humain.qml").read_text()
        self.assertIn('127.0.0.1:8787/v1/context', source)
        self.assertIn('public_only', source)
        self.assertNotIn('document.', source)

    def test_extension_manifest_is_mv3(self):
        manifest = json.loads((ROOT / "omarchy" / "extension" / "manifest.json").read_text())
        self.assertEqual(manifest["manifest_version"], 3)
        self.assertEqual(manifest["action"]["default_popup"], "popup.html")


if __name__ == "__main__":
    unittest.main()
