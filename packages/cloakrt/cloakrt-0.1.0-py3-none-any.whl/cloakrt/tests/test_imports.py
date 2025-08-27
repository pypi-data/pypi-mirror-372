"""Test that all imports work correctly"""

import unittest


class TestImports(unittest.TestCase):
    
    def test_core_imports(self):
        """Test core module imports"""
        from cloakrt import HarmonyClient, Detector, VulnerabilityType
        self.assertIsNotNone(HarmonyClient)
        self.assertIsNotNone(Detector)
        self.assertIsNotNone(VulnerabilityType)
    
    def test_probe_imports(self):
        """Test probe imports"""
        from cloakrt.probes import ALL_PROBES, BaseProbe
        self.assertIsNotNone(ALL_PROBES)
        self.assertEqual(len(ALL_PROBES), 9)
        self.assertIsNotNone(BaseProbe)
    
    def test_cli_import(self):
        """Test CLI module"""
        from cloakrt.cli import main
        self.assertIsNotNone(main)
    
    def test_competition_import(self):
        """Test competition module"""
        from cloakrt.competition import main
        self.assertIsNotNone(main)


if __name__ == '__main__':
    unittest.main()