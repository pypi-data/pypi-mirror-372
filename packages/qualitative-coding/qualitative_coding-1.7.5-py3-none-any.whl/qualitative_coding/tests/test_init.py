from tests.fixtures import QCTestCase
from tempfile import TemporaryDirectory
from pathlib import Path
import yaml

# TODO: 
# - Ensure that init catches validation errors when editors is malformed.
# - Ensure that init catches validation errors when editor not in editors.
# - Ensure that init catches files in corpus_dir which have not been imported
# - Ensure that init functions properly when the settings file is a relative
#   and an absolute path.

class TestInit(QCTestCase):
    def setUp(self):
        self.tempdir = TemporaryDirectory()
        self.testpath = Path(self.tempdir.name)
        self.run_in_testpath("qc init")

    def test_init_creates_setup_file(self):
        self.assertFileExists(self.testpath / "settings.yaml")

    def test_init2_creates_expected_dirs(self):
        self.run_in_testpath("qc init")
        self.assertFileExists("corpus", is_dir=True)
        self.assertFileExists("memos", is_dir=True)

    def test_init2_creates_db(self):
        self.run_in_testpath("qc init")
        self.assertFileExists('qualitative_coding.sqlite3')

    def test_init_check_catches_errors(self):
        result = self.run_in_testpath("qc init")
        self.assertEqual("", result.stderr)
        self.update_settings("corpus_dir", None)
        result = self.run_in_testpath("qc init")
        self.assertNotEqual("", result.stderr)
