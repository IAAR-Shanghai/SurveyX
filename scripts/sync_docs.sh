#!/usr/bin/env bash
set -euo pipefail

# The single source of truth
SOURCE_FILE="AGENTS.md"

# Files to be synchronized with the source file
TARGET_FILES=("GEMINI.md" "CLAUDE.md")

# --- Script ---
cd "$(dirname "$0")/.." # Run from project root

if [ ! -f "$SOURCE_FILE" ]; then
  echo "Error: Source file '$SOURCE_FILE' not found."
  exit 1
fi

for target in "${TARGET_FILES[@]}"; do
  # If target doesn't exist or is different from source, copy it.
  if ! cmp -s "$SOURCE_FILE" "$target" &>/dev/null; then
    echo "Syncing $SOURCE_FILE -> $target"
    cp "$SOURCE_FILE" "$target"
  fi
done
