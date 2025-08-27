import json
import tempfile

from jf_ingest import diagnostics

_test_diagnostic_1 = {"test": "1"}
_test_diagnostic_2 = {"test": 2}
_test_diagnostic_3 = {"test": "three"}


def test_open_diagnostics_file():
    with tempfile.TemporaryDirectory() as outdir:
        # Test opening and closing diagnostics file
        diagnostics.open_file(outdir=outdir)
        assert diagnostics._DIAGNOSTICS_FILE.name == f"{outdir}/diagnostics.json"
        diagnostics.close_file()
        assert diagnostics._DIAGNOSTICS_FILE == None

        # Test writing to a closed diagnostics file
        diagnostics._write_diagnostic(_test_diagnostic_1)
        assert diagnostics._DIAGNOSTICS_FILE == None

        # Test opening file twice (nothing should happen)
        diagnostics.open_file(outdir=outdir)
        diagnostics.open_file(outdir=outdir)
        assert diagnostics._DIAGNOSTICS_FILE != None
        assert diagnostics._DIAGNOSTICS_FILE.name == f"{outdir}/diagnostics.json"
        diagnostics._write_diagnostic(_test_diagnostic_1)
        diagnostics.close_file()
        assert diagnostics._DIAGNOSTICS_FILE == None


def test_write_diagnostic():
    with tempfile.TemporaryDirectory() as outdir:
        # Test opening and writing to diagnostics
        diagnostics.open_file(outdir=outdir)
        diagnostics._write_diagnostic(_test_diagnostic_1)
        diagnostics._write_diagnostic(_test_diagnostic_2)

        # TEST THAT WE CAN CLOSE AND REOPEN THE SAME FILE, AND APPEND DATA
        diagnostics.close_file()
        diagnostics.open_file(outdir=outdir)
        diagnostics._write_diagnostic(_test_diagnostic_3)
        diagnostics.close_file()

        with open(f"{outdir}/diagnostics.json", "r") as f:
            diagnostics_file_lines = f.readlines()
            assert json.loads(diagnostics_file_lines[0]) == _test_diagnostic_1
            assert json.loads(diagnostics_file_lines[1]) == _test_diagnostic_2
            assert json.loads(diagnostics_file_lines[2]) == _test_diagnostic_3
