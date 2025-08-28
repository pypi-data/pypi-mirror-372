from pathlib import Path
from tests.fixtures import QCTestCase
from qualitative_coding.refi_qda.writer import REFIQDAWriter
from tempfile import TemporaryDirectory
from xmlschema import validate
import importlib.resources

CODEBOOK = """
- one
- two
- three
- tens:
  - twenty
  - thirty
  - forty
"""

class TestREFIQDAWriter(QCTestCase):
    def setUp(self):
        super().setUp()
        self.writer = REFIQDAWriter(self.testpath / "settings.yaml")

    def test_writes_nested_codes(self):
        with open(self.testpath / "codebook.yaml", 'w') as codebook:
            codebook.write(CODEBOOK)
        codebook_xml = self.writer.codebook_to_xml()
        codes = codebook_xml.find('Codes')
        tens = codes.find("Code[@name='tens']")
        self.assertEqual(len(tens.findall('Code')), 3)

    def test_xml_validates(self):
        schema_path = importlib.resources.files("qualitative_coding") / "refi_qda" / "schema.xsd"
        self.run_in_testpath("qc corpus import macbeth.txt")
        self.set_mock_editor(verbose=True)
        self.run_in_testpath("qc code chris")
        with TemporaryDirectory() as tempdir:
            project_path = Path(tempdir)
            xml_path = project_path / "project.qde"
            self.writer.write_xml(xml_path)
            validate(xml_path, schema_path)
            


