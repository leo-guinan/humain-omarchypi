import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOT = ROOT / "bootstrap"


class BootstrapSafetyTests(unittest.TestCase):
    def test_prepare_node_is_arm_aware_and_never_writes_media(self):
        source = (BOOT / "prepare-node.sh").read_text()
        self.assertIn('aarch64', source)
        self.assertIn('manjaro-arm', source)
        self.assertNotIn('dd of=/dev', source)
        self.assertNotIn('diskutil', source)

    def test_sanitizer_requires_explicit_confirmation(self):
        source = (BOOT / "sanitize-golden-image.sh").read_text()
        self.assertIn('OMARCHYPI_SANITIZE_CONFIRM', source)
        self.assertIn('!= YES', source)
        self.assertIn('/etc/ssh/ssh_host_*', source)
        self.assertIn('/var/lib/omarchypi', source)

    def test_first_boot_service_is_one_shot_and_before_graphical(self):
        source = (BOOT / "omarchypi-first-boot.service").read_text()
        self.assertIn('Type=oneshot', source)
        self.assertIn('Before=graphical.target', source)
        self.assertIn('ConditionPathExists=!', source)


if __name__ == "__main__":
    unittest.main()
