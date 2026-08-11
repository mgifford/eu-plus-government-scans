#!/usr/bin/env bash
#
# Download every per-owner scan-metadata artifact into one directory, ready for
# `python3 -m src.cli.metadata_artifact merge`.
#
# Each scan workflow owns one artifact and writes only that one, so nothing ever
# overwrites another workflow's results.  A job that needs the full picture --
# for cross-scanner skip logic, or to generate reports -- collects them all here
# first.  See src/lib/metadata_merge.py.
#
# Artifacts are fetched from whichever workflow run produced them most recently.
# A missing artifact is not an error: it simply has not been produced yet.
#
# Usage: scripts/fetch-metadata-artifacts.sh [destination-dir]
# Requires: gh (authenticated), GITHUB_REPOSITORY.

set -euo pipefail

DEST="${1:-data/artifacts}"
: "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY must be set}"

# Artifact names come from the ownership map so the two cannot drift apart.
NAMES="$(python3 -c 'from src.lib.metadata_merge import ARTIFACT_TABLES; print(" ".join(sorted(ARTIFACT_TABLES)))')"

mkdir -p "$DEST"

for name in $NAMES; do
  run_id="$(
    gh api --paginate \
      "/repos/${GITHUB_REPOSITORY}/actions/artifacts?per_page=100&name=${name}" \
      --jq '.artifacts[] | select(.expired == false) | "\(.created_at) \(.workflow_run.id)"' \
      2>/dev/null | sort -rk1 | head -1 | awk '{print $2}' || true
  )"

  if [ -z "$run_id" ]; then
    echo "  ${name}: none published yet"
    continue
  fi

  if gh run download "$run_id" --name "$name" --dir "${DEST}/${name}" >/dev/null 2>&1; then
    echo "  ${name}: from run ${run_id}"
  else
    # A download failure must not abort the scan; the merge simply proceeds
    # without this artifact rather than losing the run.
    echo "  ${name}: download failed, continuing without it"
    rm -rf "${DEST:?}/${name}"
  fi
done
