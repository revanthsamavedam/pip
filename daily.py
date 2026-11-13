"""Pip's daily routine — the wake-up cycle.

One run = one day:
  1. read INTENTIONS.md (the standing routine, "- [ ]" tasks)
  2. run each task through its own fresh Looper (own 30-turn budget,
     own session; the store and home are shared)
  3. write digests/YYYY-MM-DD.md
  4. append a diary entry to home/DIARY.md

Needs the looper installed first:
  pip install git+https://github.com/revanthsamavedam/looper.git

Live runs need a provider: LOOPER_API_KEY (OpenAI/OpenRouter) or a local
Ollama (LOOPER_MODEL=ollama/...). With no provider, use --dry-run to
exercise the plumbing with a scripted model (no network, no key).

Run:  python daily.py [--dry-run]
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

try:
    from looper import Looper, SessionStore
    from looper.provider import resolve_provider
except ImportError:
    print("Pip needs the looper installed first:")
    print("  pip install git+https://github.com/revanthsamavedam/looper.git")
    sys.exit(2)

AGENT_DIR = Path(__file__).resolve().parent
HOME = AGENT_DIR / "home"
DIGESTS = AGENT_DIR / "digests"


class DryRunClient:
    """Scripted model for --dry-run: one real tool call, then 'done'.

    Mirrors tests/test_looper.py's ScriptedClient. The first chat() does a
    real write_file (proving the loop can act), then answers in text;
    every later call answers "done".
    """

    def __init__(self):
        note = HOME / "scratch" / "dry-run-note.txt"
        self.script = [
            {"content": "", "tool_calls": [
                {"id": "d1", "name": "write_file",
                 "arguments": {"path": str(note),
                               "content": "Pip was here (dry run)\n"}}]},
            {"content": "Wrote the dry-run note and verified it by reading it back.",
             "tool_calls": []},
        ]
        self.calls = []

    def call(self, messages, tools):
        self.calls.append((messages, tools))
        if not self.script:
            return {"content": "done", "tool_calls": []}
        return self.script.pop(0)


def read_intentions() -> list[str]:
    tasks = []
    for line in (AGENT_DIR / "INTENTIONS.md").read_text().splitlines():
        line = line.strip()
        if line.startswith("- [ ]"):
            tasks.append(line[5:].strip())
    return tasks


def write_digest(day: date, provider_label: str, results: list[dict]) -> Path:
    DIGESTS.mkdir(parents=True, exist_ok=True)
    lines = [f"# Pip — digest {day.isoformat()}", "", f"Provider: {provider_label}", ""]
    for r in results:
        lines += [f"## {r['task']}", "", r["summary"] or "(no summary)", "",
                  f"({r['turns']} turn{'s' if r['turns'] != 1 else ''})", ""]
    lines += ["## What I learned", "",
              "Anything durable I saved today is in MEMORY.md and the diary.", ""]
    p = DIGESTS / f"{day.isoformat()}.md"
    p.write_text("\n".join(lines))
    return p


def append_diary(day: date, one_liners: list[str]) -> None:
    p = HOME / "DIARY.md"
    entry = f"\n## {day.isoformat()}\n" + "\n".join(f"- {s}" for s in one_liners) + "\n"
    p.write_text((p.read_text() if p.exists() else "# Pip — diary\n") + entry)


def run_day(dry_run: bool) -> Path:
    today = date.today()
    tasks = read_intentions()
    HOME.mkdir(parents=True, exist_ok=True)
    store = SessionStore(HOME / "sessions.db")

    if dry_run:
        client: DryRunClient | None = DryRunClient()
        provider_label = "dry-run (scripted model)"
    else:
        client = None
        try:
            provider_label = resolve_provider().model
        except Exception as exc:  # noqa: BLE001 — no provider configured
            print(f"Pip cannot wake up: {exc}")
            print("Set LOOPER_API_KEY (or OPENAI_API_KEY), or run a local Ollama")
            print("with LOOPER_MODEL=ollama/<model>. Or test the plumbing with:")
            print("  python agent/daily.py --dry-run")
            sys.exit(2)

    results = []
    for task in tasks:
        try:
            # Fresh Looper per task: its own 30-turn budget and session.
            # The store and home are shared, so memory and session search
            # still see everything.
            agent = Looper(client=client, store=store, home=HOME,
                           auto_approve=True)
            prompt = (
                f"Today is {today.isoformat()}. Task: {task}\n"
                "Work in the looper repo and your home folder. Use tools to "
                "verify; summarise what you did and found in a few lines."
            )
            r = agent.run_conversation(prompt)
            results.append({"task": task,
                            "summary": r.get("final_response", ""),
                            "turns": r.get("turns", 0)})
        except Exception as exc:  # noqa: BLE001 — one bad task must not kill the day
            results.append({"task": task,
                            "summary": f"Task failed: {exc}",
                            "turns": 0})

    digest = write_digest(today, provider_label, results)
    one_liners = []
    for r in results:
        first = (r["summary"] or "").splitlines()
        one_liners.append(first[0] if first else "(no summary)")
    append_diary(today, one_liners)
    return digest


def main() -> None:
    ap = argparse.ArgumentParser(description="Pip's daily routine.")
    ap.add_argument("--dry-run", action="store_true",
                    help="scripted model, no network, no key")
    args = ap.parse_args()
    digest = run_day(args.dry_run)
    print(f"Pip done for today. Digest: {digest}")


if __name__ == "__main__":
    main()
