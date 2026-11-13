# Pip — the persistent layer on the looper

Pip is a persistent agent built on the custom looper. It wakes once a
day, runs its standing routine, writes a digest, and goes back to sleep.
It is not sentient — it is a loop over a language model plus files. What
it has that a one-shot looper run doesn't: continuity. It remembers what
it wrote down, builds on yesterday, and gets more useful the longer it
runs.

## Layout

- `home/SOUL.md` — Pip's identity. Rename Pip by editing one line here.
- `home/USER.md` — about Revanth, its owner.
- `home/MEMORY.md` — long-term memory. Pip's `memory` tool appends here.
- `home/DIARY.md` — one entry per day, appended by the routine.
- `home/skills/` — skill files Pip can read (first line each is indexed).
- `home/sessions.db` — SQLite sessions + FTS5 search (the looper's store).
- `INTENTIONS.md` — the standing daily routine. Tasks repeat every day;
  they are not a todo list, so they stay unchecked.
- `daily.py` — the wake-up cycle.
- `run_daily.sh` — wrapper for cron or manual runs.
- `digests/` — one file per day. This is Pip's voice.

## Run it

```bash
pip install git+https://github.com/revanthsamavedam/looper.git   # the engine Pip runs on
python daily.py --dry-run   # scripted model, no key, no network
python daily.py             # live — needs a provider (below)
./run_daily.sh              # same, for cron
```

Schedule it (on the machine that owns the provider key), 7am daily:

```
0 7 * * * /path/to/pip/run_daily.sh >> /tmp/pip-daily.log 2>&1
```

## Provider (for live runs)

- OpenAI: `LOOPER_API_KEY=...` (or `OPENAI_API_KEY`), default model `openai/gpt-4o-mini`.
- OpenRouter: `LOOPER_MODEL=openrouter/...` + `LOOPER_API_KEY`.
- Ollama (no key): Ollama running locally + `LOOPER_MODEL=ollama/<model>`.
- Never paste a key in chat. Env var only.

## Where the "alive" feeling comes from — and where it stops

From: identity + memory + a routine + a digest. Pip has a name, remembers
what it wrote, does the same kinds of things every day, and tells you what
it did. That continuity is most of what "alive" feels like from the
outside.

Stops: Pip has no inner experience and no goals of its own — its routine
is the file Revanth wrote. It cannot message you on its own (no gateway);
the digest is its voice, and Dino shows it to you. It stops when the run
ends, and it can only act through its tools (files, shell) in the places
a task names. It never deletes anything.
