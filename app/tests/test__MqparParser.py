import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "omics" / "proteomics" / "maxquant" / "MqparParser.py"
SPEC = spec_from_file_location("MqparParserModule", MODULE_PATH)
MODULE = module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
MqparParser = MODULE.MqparParser


class MqparParserTestCase(unittest.TestCase):
    def test_as_template_tolerates_placeholderless_stub(self):
        parser = MqparParser()
        parser._content = "<mqpar></mqpar>"

        parser.as_template()

        self.assertEqual(parser._content, "<mqpar></mqpar>")

    def test_as_template_rejects_multiple_raw_entries(self):
        parser = MqparParser()
        parser._content = """
<MaxQuantParams>
  <filePaths>
    <string>sample-1.raw</string>
    <string>sample-2.RAW</string>
  </filePaths>
</MaxQuantParams>
"""

        with self.assertRaisesRegex(AssertionError, "Please use mqpar.xml for single RAW file."):
            parser.as_template()
