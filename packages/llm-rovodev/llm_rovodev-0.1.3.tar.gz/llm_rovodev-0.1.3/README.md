# llm-rovodev

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](./LICENSE)

Plugin for [LLM](https://llm.datasette.io/) adding a model called `rovodev` that shells out to `acli rovodev run` and returns the parsed response.

## Installation

Install this plugin in the same environment as LLM:

```bash
llm install llm-rovodev
```

To learn more about installing and using the Rovo Dev CLI itself, see:
[Introducing Rovo Dev CLI – AI-Powered Development in your terminal](https://community.atlassian.com/forums/Rovo-for-Software-Teams-Beta/Introducing-Rovo-Dev-CLI-AI-Powered-Development-in-your-terminal/ba-p/3043623).

## Usage

This plugin adds a model called `rovodev`. You can execute it like this:

```bash
# Basic usage
llm -m rovodev "What is 2+2?"

# Allow up to 15 minutes for complex runs (minimum enforced is 120s)
llm -m rovodev -o timeout_seconds 900 "Run a long multi-step task"
```

By default it parses the box-drawn "Response" section from the external `acli rovodev run` output and prints just that content.

Notes:
- The plugin executes an external CLI: `acli rovodev run`.
- Rovodev non-interactive "run" prompts can only contain 256 characters. To work around this, if your prompt exceeds 256 characters, the plugin writes it to a file under `./.llm-rovodev/` and instructs the agent to read it. These files are deleted after the next run of llm using this plugin.
- Many advanced features are not yet supported: no API keys, no schemas, no tools, no attachments, no token usage tracking, etc.
- Enable `LLM_ROVODEV_DEBUG=1` to see the exact command, redacted env, timing, and (on errors or missing Response blocks) full stdout/stderr. This can help diagnose CLI behavior quickly.
- Options:
  - `-o yolo true` forwards `--yolo` to `acli rovodev run`.
  - `-o config-file <path>` forwards `--config-file <path>` to `acli rovodev run`. Relative paths are normalized to absolute before being passed through. The config file can set which model Rovo Dev runs with, whether sessions are persisted between runs, and more.
  - `-o timeout <seconds, minimum  120>` to set a timeout which will kill the subprocess that spawned rovodev.
  - `-o raw true` will output unfiltered stdout text from `acli rovodev` subprocess.
## Development

To set up this plugin locally:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
pip install pytest
pytest
```
