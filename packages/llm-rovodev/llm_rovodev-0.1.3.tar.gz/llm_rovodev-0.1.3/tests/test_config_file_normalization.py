from click.testing import CliRunner
from llm.cli import cli
import os

def _make_shim_and_script(content: str, runner: CliRunner):
    mock_path = os.path.abspath("mock_acli.py")
    with open(mock_path, "w", encoding="utf-8") as f:
        f.write(content)
    os.chmod(mock_path, 0o755)

    shim = os.path.abspath("mock_acli_shim.sh")
    with open(shim, "w", encoding="utf-8") as f:
        f.write("#!/usr/bin/env bash\n" "python3 \"%s\" \"$@\"\n" % mock_path)
    os.chmod(shim, 0o755)
    os.environ["ACLI_BIN"] = shim


def test_config_file_relative_path_is_normalized_to_abs():
    runner = CliRunner()

    script = (
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "args = sys.argv[1:]\n"
        "cfg = None\n"
        "if '--config-file' in args:\n"
        "    i = args.index('--config-file')\n"
        "    cfg = args[i+1] if i+1 < len(args) else None\n"
        "print('Using model: test-model')\n"
        "print('')\n"
        "print('\u256d\u2500 Response \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e')\n"
        "print('\u2502 cfg=' + str(cfg) + '                 \u2502')\n"
        "print('\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f')\n"
    )

    with runner.isolated_filesystem():
        _make_shim_and_script(script, runner)
        rel_cfg = "rovo.json"
        with open(rel_cfg, "w", encoding="utf-8") as f:
            f.write("{}\n")
        abs_cfg = os.path.abspath(rel_cfg)
        args = [
            "Prompt",
            "-m",
            "rovodev",
            "-o",
            "config-file",
            rel_cfg,
        ]
        result = runner.invoke(cli, args)
        assert result.exit_code == 0, result.output
        out = result.output
        assert f"cfg={abs_cfg}" in out
