import subprocess
import sys
import shutil

def test_cli_help_runs():
    # Run as module
    result = subprocess.run(
        [sys.executable, "-m", "pdf_box_fields.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()


def test_installed_entry_point_works():
    # Ensure console script "pdf-box-fields" exists in PATH
    exe = shutil.which("pdf-box-fields")
    assert exe is not None, "pdf-box-fields entry point not found in PATH"

    result = subprocess.run(
        [exe, "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()
