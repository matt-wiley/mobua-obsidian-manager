#!/usr/bin/env bash
# Starts `headroom proxy --port 8787` in a detached tmux window.
# - If run from inside an existing tmux session, adds a new window to it.
# - Otherwise, creates a new detached session.

set -euo pipefail

SESSION="${TMUX_SESSION:-headroom}"
WINDOW="${TMUX_WINDOW:-proxy}"
CMD="headroom proxy --port 8787"

if [ -n "${TMUX:-}" ]; then
    # Already inside tmux: add a detached window to the current session
    tmux new-window -d -n "$WINDOW" "$CMD"
    echo "Started '$CMD' in new window '$WINDOW' of the current tmux session."
else
    # Not inside tmux: create a new detached session
    tmux new-session -d -s "$SESSION" -n "$WINDOW" "$CMD"
    echo "Started '$CMD' in tmux session '$SESSION', window '$WINDOW'."
    echo "Attach with: tmux attach -t $SESSION"
fi