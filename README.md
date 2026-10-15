# Jev and Laya demo

A live "ticket triage race": [Laya](https://huggingface.co/convaiinnovations/laya), an open-weight
System One decision model compatible with TypeSafe's Jev API, against two local LLMs in Ollama.
Each of 20 support tickets gets three typed questions: which department (choice), how urgent
(score 0-3) and does the customer want money back (yes/no).

The slides are in [presentation/jev-laya.html](presentation/jev-laya.html). Open the file in a browser and press `S` for speaker notes.

## Setup

Requires an Apple Silicon Mac, [uv](https://docs.astral.sh/uv/) and [Ollama](https://ollama.com).

```bash
uv sync
ollama pull mistral:latest
ollama pull gemma:2b
uv run jev-laya-demo --tickets 1 --repeats 0 --quality-only   # first run downloads Laya (~1.5 GB)
```

After the first download the demo runs fully offline (`HF_HUB_OFFLINE` is set automatically once
the checkpoint is cached).

## Run the demo

```bash
uv run jev-laya-demo
```

The demo loads Laya and warms up every model before the race, so nobody pays a cold start. Press Enter
to start. When the race finishes, it prints the quality report: valid outputs, accuracy, Laya's
probabilities on the tricky tickets, a consistency check (the same tickets asked three times) and a
cost projection for 1M tickets per day.

The whole run takes about 3 minutes on an M-series Mac. Run it in a wide terminal (140+ columns).

| flag | default | effect |
| --- | --- | --- |
| `--tickets N` | 20 | tickets in the race |
| `--models a,b` | `mistral:latest,gemma:2b` | Ollama models to race |
| `--single-call` | off | LLMs get all three questions in one call instead of one call per question |
| `--no-reason` | off | LLMs answer with JSON only instead of one sentence of reasoning first |
| `--repeats N` | 3 | reruns of the 7 tricky tickets for the consistency check (0 skips it) |
| `--temperature T` | 0.7 | LLM sampling temperature |
| `--quality-only` | off | skip the live race view |

## What is (and is not) fair

By default the LLMs make one call per question and write a short reason before the JSON. This is
the common "chain of thought, then structured output" pattern, but it costs output tokens. Laya is
preloaded, warmed up and batched. To give the LLMs their fastest setup, run
`uv run jev-laya-demo --single-call --no-reason`. The LLMs are not cold-loaded: every model is
warm before the race starts.

Accuracy is measured against hand-written labels in `src/jev_laya_demo/tickets.py`. An invalid output
counts as wrong, and urgency counts as correct within one level of the label. A typical run
(M-series, all 20 tickets):

| | time | per ticket | output tokens | valid | overall accuracy | flips over 3 reruns |
| --- | --- | --- | --- | --- | --- | --- |
| Laya | 1.0 s | 50 ms | 0 | 100% | 90% | 0 / 21 |
| mistral 7B | 57 s | 2.8 s | 2,199 | 100% | 93% | 4 / 21 |
| gemma 2B | 45 s | 2.3 s | 2,790 | 90% | 68% | 12 / 21 |

Base Laya is within a few points of mistral overall (mistral's score varies from run to run), and
its weakest question is department routing. That matches the
model card: base checkpoints are a foundation to fine-tune, not a zero-shot oracle.
