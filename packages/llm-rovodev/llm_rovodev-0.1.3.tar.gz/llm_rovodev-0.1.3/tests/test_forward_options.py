from click.testing import CliRunner
from llm.cli import cli
import os
import json


def _make_shim_and_script(content: str, runner: CliRunner):
    mock_path = os.path.abspath("mock_acli.py")
    with open(mock_path, "w", encoding="utf-8") as f:
        f.write(content)
    os.chmod(mock_path, 0o755)

    shim = os.path.abspath("mock_acli_shim.sh")
    with open(shim, "w", encoding="utf-8") as f:
        # Important: forward $@ so args are visible to the Python script
        f.write("#!/usr/bin/env bash\n" "python3 \"%s\" \"$@\"\n" % mock_path)
    os.chmod(shim, 0o755)
    os.environ["ACLI_BIN"] = shim


def test_forwards_yolo_flag_to_acli():
    runner = CliRunner()

    script = (
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "args = sys.argv[1:]\n"
        "has_yolo = '--yolo' in args\n"
        "print('Using model: test-model')\n"
        "print('')\n"
        # Emit a Response block showing whether --yolo was present
        "print('\u256d\u2500 Response \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e')\n"
        "print('\u2502 yolo=' + str(has_yolo).lower() + '                 \u2502')\n"
        "print('\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f')\n"
    )

    with runner.isolated_filesystem():
        _make_shim_and_script(script, runner)
        args = [
            "Prompt",
            "-m",
            "rovodev",
            "-o",
            "yolo",
            "true",
        ]
        result = runner.invoke(cli, args)
        assert result.exit_code == 0, result.output
        out = result.output
        assert "yolo=true" in out


def test_forwards_config_file_to_acli():
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
        cfg_path = os.path.abspath("rovo.json")
        with open(cfg_path, "w", encoding="utf-8") as f:
            f.write("{}\n")
        args = [
            "Prompt",
            "-m",
            "rovodev",
            "-o",
            "config-file",
            cfg_path,
        ]
        result = runner.invoke(cli, args)
        assert result.exit_code == 0, result.output
        out = result.output
        assert f"cfg={cfg_path}" in out
