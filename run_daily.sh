#!/bin/sh
# Pip's daily run — for cron or a manual wake-up.
#   ./run_daily.sh [--dry-run]
# Needs the looper installed first:
#   pip install git+https://github.com/revanthsamavedam/looper.git
# Live runs need LOOPER_API_KEY (or OPENAI_API_KEY) in the environment,
# or a local Ollama with LOOPER_MODEL=ollama/<model>.
# Cron example (7am daily, on the machine that owns the provider key):
#   0 7 * * * /path/to/pip/run_daily.sh >> /tmp/pip-daily.log 2>&1
set -e
cd "$(dirname "$0")"
export LOOPER_HOME="$PWD/home"
exec python3 daily.py "$@"
