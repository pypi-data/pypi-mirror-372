from click.testing import CliRunner
from llm.cli import cli
import os


def test_ai_policy_filter_raises_click_exception(monkeypatch):
    runner = CliRunner()

    # Mock acli to emit an AI Policy Filter box and no Response box
    script = (
        "#!/usr/bin/env python3\n"
        "print('Using model: gpt-5-2025-08-07')\n"
        "print('')\n"
        "print('╭─ AI Policy Filter ────────────────────────────────╮')\n"
        "print('│                                                   │')\n"
        "print('│ Your prompt was blocked by the Atlassian AI       │')\n"
        "print('│ policy filter.                                    │')\n"
        "print('│                                                   │')\n"
        "print('│ Harm category: Jailbreak/Prompt Injection         │')\n"
        "print('│                                                   │')\n"
        "print('│ If you believe this is an error, try rephrasing   │')\n"
        "print('│ your prompt and trying again.                     │')\n"
        "print('│                                                   │')\n"
        "print('│ For more information, please refer to the         │')\n"
        "print('│ Atlassian Acceptable Use Policy:                  │')\n"
        "print('│ https://www.atlassian.com/legal/acceptable-use-po │')\n"
        "print('│ licy#ai-offerings                                 │')\n"
        "print('│                                                   │')\n"
        "print('╰───────────────────────────────────────────────────╯')\n"
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

        args = [
            "Test prompt",
            "-m",
            "rovodev",
        ]
        result = runner.invoke(cli, args)

        # Should raise a ClickException and exit non-zero
        assert result.exit_code != 0
        assert "Your prompt was blocked by the Atlassian AI policy filter" in result.output
        # helpful detail
        assert "Harm category" in result.output
