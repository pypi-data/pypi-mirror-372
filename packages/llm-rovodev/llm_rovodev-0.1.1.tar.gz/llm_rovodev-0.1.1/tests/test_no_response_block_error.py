from click.testing import CliRunner
from llm.cli import cli
import os

def test_rovodev_errors_when_no_response_block(monkeypatch):
    runner = CliRunner()

    # Mock acli to emit only a banner/model line and no Response box
    script = (
        "#!/usr/bin/env python3\n"
        "print('Using model: gpt-5-2025-08-07')\n"
        "print('')\n"
    )

    with runner.isolated_filesystem():
        mock_path = os.path.abspath("mock_acli.py")
        with open(mock_path, "w", encoding="utf-8") as f:
            f.write(script)
        os.chmod(mock_path, 0o755)

        # Shim that forwards all args to the Python script
        shim = os.path.abspath("mock_acli_shim.sh")
        with open(shim, "w", encoding="utf-8") as f:
            f.write("#!/usr/bin/env bash\n" "python3 \"%s\" \"$@\"\n" % mock_path)
        os.chmod(shim, 0o755)

        # Ensure our plugin finds the shim
        os.environ["ACLI_BIN"] = shim

        # Invoke llm with the rovodev model; since there is no Response block,
        # the plugin should raise a ClickException and the CLI should exit with non-zero code.
        args = [
            "Hello there",
            "-m",
            "rovodev",
        ]
        result = runner.invoke(cli, args)
        assert result.exit_code != 0
        # Click formats ClickException as "Error: <message>\n"
        assert "No Response block found in rovodev CLI output" in result.output

        # Raw mode should still succeed and return raw stdout
        # Raw mode still enforces presence of a Response block, but the hint
        # should tell users how to inspect raw output by passing `true`.
        args_raw = [
            "Hello there",
            "-m",
            "rovodev",
        ]
        result_raw = runner.invoke(cli, args_raw)
        assert result_raw.exit_code != 0
        assert "No Response block found in rovodev CLI output" in result_raw.output

        # Even with `-o raw true`, absence of a Response block should still be treated as an error
        args_raw_true = [
            "Hello there",
            "-m",
            "rovodev",
            "-o",
            "raw",
            "true",
        ]
        result_raw_true = runner.invoke(cli, args_raw_true)
        assert result_raw_true.exit_code != 0
        assert "No Response block found in rovodev CLI output" in result_raw_true.output
