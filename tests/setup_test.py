import unittest
from unittest.mock import patch


class TestSetup(unittest.TestCase):
    def test_main(self):
        with self.assertRaises(SystemExit) as cm:
            import setup
        self.assertIn("error: option --udiscovery not recognized",
                      str(cm.exception))
