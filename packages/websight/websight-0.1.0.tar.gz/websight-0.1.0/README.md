# Websight

Minimal Python package for calling the Websight VLM and a thin browser Agent.

## Layout

```
src/websight/
  __init__.py
  agent/
    agent.py         # Agent(run/execute_action)
    browser.py       # Playwright wrapper
  model/
    websight.py      # websight_call(prompt, history, image)
    actions.py       # Action + parse_action
    prompts.py       # system prompt for websight_call
    llm.py           # simple OpenRouter LLM helpers
scripts/
  manual_image_demo.py
eval/
  showdown/...
tests/
```

## Install (editable) and run tests

```bash
uv run --frozen -- python -V  # ensure Python is available
PYTHONPATH=src uv run --group test pytest -q tests
```

## Quickstart

Programmatic use:

```python
from websight import websight_call

# image_base64 may include the 'data:image/png;base64,' prefix or raw base64
action = websight_call(
    prompt="Click the Login button",
    history=[],  # list of (reasoning, action_str) pairs from prior steps
    image_base64="data:image/png;base64,<...>",
)
print(action.action, action.args)
```

Agent (with a real browser via Playwright):

```bash
PYTHONPATH=src uv run python websight.py --task "Go to https://example.com and click More" --show-browser
```

Manual image demo (no browser):

```bash
PYTHONPATH=src uv run python scripts/manual_image_demo.py \
  --image data/showdown_clicks/images/0b1c958b929acdbf.png \
  --max-new-tokens 512
```

## Environment

Web requests to LLMs use OpenRouter. Set:

```
export OPENROUTER_API_KEY=...
```

The Websight model will be loaded from Hugging Face via `transformers` pipeline: `tanvirb/websight-7B`.

## Packaging (src layout)

This repository is configured for a src layout with setuptools.

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
packages = {find = {where = ["src"]}}
```

Build locally (artifacts in `dist/`):

```bash
uv build
```

Do not publish yet. When ready, you can publish with `uv publish` after setting the appropriate token.
