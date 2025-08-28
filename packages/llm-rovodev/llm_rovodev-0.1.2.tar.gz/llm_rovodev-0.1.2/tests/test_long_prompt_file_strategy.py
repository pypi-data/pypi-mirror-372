from click.testing import CliRunner
from llm.cli import cli
import os


def test_long_prompt_creates_dot_file_and_instructs_open(monkeypatch):
    runner = CliRunner()

    long_prompt = "x" * 300  # > 256

    # Mock acli to verify the message argument contains the instruction to open the dot file
    # and to emit a valid Response block so the run succeeds.
    script = (
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "args = sys.argv[1:]\n"
        "# Expect: ['rovodev', 'run', 'Open ./.llm_rovodev_prompt_... and follow ...']\n"
        "instr = args[2] if len(args) >= 3 else ''\n"
        "print('Using model: gpt-5-2025-08-07')\n"
        "print('')\n"
        "print('╭─ Response ─────────────────────────────────────────────╮')\n"
        "print('│ ' + instr[:60].ljust(54) + ' │')\n"
        "print('╰────────────────────────────────────────────────────────╯')\n"
    )

    with runner.isolated_filesystem():
        mock_path = os.path.abspath("mock_acli.py")
        with open(mock_path, "w", encoding="utf-8") as f:
            f.write(script)
        os.chmod(mock_path, 0o755)

        shim = os.path.abspath("mock_acli_shim.sh")
        with open(shim, "w", encoding="utf-8") as f:
            f.write("#!/usr/bin/env bash\n" "python3 \"%s\" \"$@\"\n" % mock_path)
        os.chmod(shim, 0o755)

        os.environ["ACLI_BIN"] = shim

        # Invoke llm with a long prompt
        args = [
            long_prompt,
            "-m",
            "rovodev",
        ]
        result = runner.invoke(cli, args)
        assert result.exit_code == 0, result.output

        # The plugin should have written a dot-temp file in CWD
        dot_files = [f for f in os.listdir(".") if f.startswith(".llm_rovodev_prompt_")]
        assert dot_files, "Expected a dot temp file to be created for long prompt"

        # And the instruction passed to acli should mention opening that file
        out = result.output
        assert "Open ./" in out and ".llm_rovodev_prompt_" in out
