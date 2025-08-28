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
llm -m rovodev "What is 2+2?"
```

By default it parses the box-drawn "Response" section from the external `acli rovodev run` output and prints just that content.

Return raw stdout (including banners and box drawing) using `-o raw`:

```bash
llm -m rovodev -o raw true "What is 2+2?"
```

Notes:
- The plugin executes an external CLI: `acli rovodev run`. Override the binary path via `ACLI_BIN` if needed (e.g. `ACLI_BIN=/path/to/acli`).
- Advanced features are intentionally not supported: no API keys, no schemas, no tools, no attachments, no token usage tracking, etc.

### Handling blank/no response from Rovo Dev CLI

This plugin relies on the external `acli rovodev run` to emit a box-drawn "Response" section on stdout. If no such Response block is found, the plugin will exit with an error:

Error: No Response block found in rovodev CLI output. Enable LLM_ROVODEV_DEBUG=1 to capture full logs or run the rovodev CLI directly to debug.

Notes and tips:
- This can occur if the external CLI decides not to produce a response for certain inputs (for example multi-line or file-derived prompts).
- Enable debug logging to capture full stdout/stderr from the subprocess and the exact command invoked: `LLM_ROVODEV_DEBUG=1`.
- You can also run the underlying CLI directly to compare behavior: `acli rovodev run "your prompt"`.
- The `-o raw` option only changes how output is displayed when a Response block exists; it does not bypass the error on missing Response blocks. With LLM, booleans for `-o` are passed using two arguments, for example: `-o raw true`.

### Debug logging

Enable verbose debug logs by setting `LLM_ROVODEV_DEBUG=1` for a run. These logs include the effective command, redacted environment, verbatim prompt, timing info, and full stdout/stderr from the external CLI. By default logs go to stderr if your terminal is interactive.

To capture both logs and the normal model output into a file using shell redirection, enable debug and redirect stdout:

```bash
LLM_ROVODEV_DEBUG=1 llm -m rovodev "your prompt" > out.txt
```

- When stdout is redirected (non-tty), the plugin automatically emits debug logs to stdout so `> out.txt` contains both logs and the model's output.
- If you prefer logs to remain separate, keep using a TTY and redirect stderr only:

```bash
LLM_ROVODEV_DEBUG=1 llm -m rovodev "your prompt" 2> debug.log > out.txt
```

## Development

To set up this plugin locally:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
pip install pytest
pytest
```
