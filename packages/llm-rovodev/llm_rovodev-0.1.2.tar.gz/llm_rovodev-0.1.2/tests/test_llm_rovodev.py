from click.testing import CliRunner
from llm.cli import cli
import os
import pytest


def test_rovodev_basic_invocation(monkeypatch):
    runner = CliRunner()

    # Monkeypatch ACLI_BIN to point to a mock script that prints a known acli-like output
    script = (
        "#!/usr/bin/env python3\n"
        "print('Using model: gpt-5-2025-08-07')\n"
        "print('')\n"
        "print('╭─ Response ───────────────────────────────────────────────────────────╮')\n"
        "print('│ 42                                                                  │')\n"
        "print('│                                                                      │')\n"
        "print('│ Done.                                                               │')\n"
        "print('╰──────────────────────────────────────────────────────────────────────╯')\n"
    )
    with runner.isolated_filesystem():
        mock_path = os.path.abspath("mock_acli.py")
        with open(mock_path, "w", encoding="utf-8") as f:
            f.write(script)
        os.chmod(mock_path, 0o755)

        # Wrapper shell script to accept arbitrary args and run the Python script
        shim = os.path.abspath("mock_acli_shim.sh")
        with open(shim, "w", encoding="utf-8") as f:
            f.write("#!/usr/bin/env bash\n" "python3 \"%s\"\n" % mock_path)
        os.chmod(shim, 0o755)

        # Ensure our plugin finds the shim
        os.environ["ACLI_BIN"] = shim

        args = [
            "What is the answer?",
            "-m",
            "rovodev",
        ]
        result = runner.invoke(cli, args)
        assert result.exit_code == 0, result.output
        # Should print just the parsed response block contents
        output = result.output.strip()
        assert "42" in output
        assert "Done." in output
        assert "Using model:" not in output


def test_rovodev_raw_output(monkeypatch):
    runner = CliRunner()

    # Monkeypatch ACLI_BIN to point to a mock script output with banner + response box
    script = (
        "#!/usr/bin/env python3\n"
        "print('Using model: gpt-5-2025-08-07')\n"
        "print('')\n"
        "print('╭─ Response ───────────────────────────────────────────────────────────╮')\n"
        "print('│ hello                                                              │')\n"
        "print('╰──────────────────────────────────────────────────────────────────────╯')\n"
    )
    with runner.isolated_filesystem():
        mock_path = os.path.abspath("mock_acli.py")
        with open(mock_path, "w", encoding="utf-8") as f:
            f.write(script)
        os.chmod(mock_path, 0o755)

        shim = os.path.abspath("mock_acli_shim.sh")
        with open(shim, "w", encoding="utf-8") as f:
            f.write("#!/usr/bin/env bash\n" "python3 \"%s\"\n" % mock_path)
        os.chmod(shim, 0o755)

        os.environ["ACLI_BIN"] = shim

        args = [
            "What is 2+2?",
            "-m",
            "rovodev",
            "-o",
            "raw",
            "true",
        ]
        result = runner.invoke(cli, args)
        assert result.exit_code == 0, result.output
        # Raw output should include the "Using model:" line
        output = result.output
        assert "Using model:" in output
        assert "hello" in output
