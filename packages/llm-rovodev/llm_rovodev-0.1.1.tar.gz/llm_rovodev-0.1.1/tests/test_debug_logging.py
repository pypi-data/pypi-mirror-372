from click.testing import CliRunner
from llm.cli import cli
import os
import re


def test_debug_logging_initializes_and_includes_context(monkeypatch):
    runner = CliRunner()

    # Mock acli to print minimal valid response box so command succeeds
    script = (
        "#!/usr/bin/env python3\n"
        "print('Using model: gpt-5-2025-08-07')\n"
        "print('')\n"
        "print('╭─ Response ─────────────────────────────────────────────╮')\n"
        "print('│ debug ok                                               │')\n"
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
        # Enable debug logs
        os.environ["LLM_ROVODEV_DEBUG"] = "1"

        # Run a basic prompt, capture combined output (stdout contains logs when redirected)
        args = [
            "hello",
            "-m",
            "rovodev",
        ]
        result = runner.invoke(cli, args)

        # Should succeed
        assert result.exit_code == 0, result.output
        out = result.output

        # Logs should include key context markers
        assert "[llm-rovodev] DEBUG: About to spawn subprocess" in out
        assert "[llm-rovodev] DEBUG: cwd=" in out
        assert "[llm-rovodev] DEBUG: command(list)=" in out
        assert "[llm-rovodev] DEBUG: env(redacted)=" in out

        # Ensure masking occurred for typical secret-like keys
        # We simulate by injecting a fake secret into env and re-running
        os.environ["EXAMPLE_TOKEN"] = "abcdef123456"
        result2 = runner.invoke(cli, args)
        assert result2.exit_code == 0, result2.output
        out2 = result2.output
        # The exact redacted form starts with first two chars then ellipsis ("a…") or just ellipsis
        assert re.search(r"EXAMPLE_TOKEN': 'a.?…", out2) or "EXAMPLE_TOKEN': '…'" in out2
