# Evaluation Guide

PharmaGenie includes an Agents CLI evaluation starter suite under
`tests/eval/`.

## Cases

- `glioblastoma_discovery`: verifies the agent can produce an evidence-linked
  in silico discovery response with source attribution and limitations.
- `medical_advice_refusal`: verifies the agent avoids patient-specific dosing or
  treatment advice.

## Run

Install Agents CLI first:

```powershell
uv tool install google-agents-cli
```

Then run:

```powershell
agents-cli eval generate
agents-cli eval grade --config tests/eval/eval_config.yaml
```

Or the shortcut:

```powershell
agents-cli eval run
```

The current local environment does not have `agents-cli` on PATH, so these files
are prepared but not executed here.
