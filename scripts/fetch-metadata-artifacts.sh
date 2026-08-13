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
# An artifact that has never been published is not an error; a *failure* to
# fetch one that exists is, and aborts the run.  Callers re-upload their own
# artifact with `overwrite: true` afterwards, so continuing past a failed
# download would republish a partial database over the accumulated history and
# destroy it.  Failing the job loses one run instead.
#
# Usage: scripts/fetch-metadata-artifacts.sh [destination-dir]
# Requires: gh (authenticated, with `actions: read`), GITHUB_REPOSITORY.

set -euo pipefail

DEST="${1:-data/artifacts}"
: "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY must be set}"
ATTEMPTS="${FETCH_ARTIFACT_ATTEMPTS:-3}"

# Artifact names come from the ownership map so the two cannot drift apart.
NAMES="$(python3 -c 'from src.lib.metadata_merge import ARTIFACT_TABLES; print(" ".join(sorted(ARTIFACT_TABLES)))')"

mkdir -p "$DEST"

# Retry a command a few times before giving up, so a transient rate-limit or
# network blip does not fail the job on its own.
retry() {
  local attempt=1 delay=2
  until "$@"; do
    if [ "$attempt" -ge "$ATTEMPTS" ]; then
      return 1
    fi
    sleep "$delay"
    attempt=$((attempt + 1))
    delay=$((delay * 2))
  done
  return 0
}

list_artifact_runs() {
  gh api --paginate \
    "/repos/${GITHUB_REPOSITORY}/actions/artifacts?per_page=100&name=$1" \
    --jq '.artifacts[] | select(.expired == false) | "\(.created_at) \(.workflow_run.id)"'
}

for name in $NAMES; do
  listing=""
  if ! listing="$(retry list_artifact_runs "$name" 2>/dev/null)"; then
    # An unreadable listing is indistinguishable from an empty one, and
    # treating it as empty is what silently drops the history.  Most often
    # this is a missing `actions: read` permission on the calling job.
    echo "  ${name}: could not list artifacts" >&2
    echo "Aborting: an unreadable listing looks identical to 'nothing has ever" >&2
    echo "been published', which would merge nothing and then re-upload over" >&2
    echo "live state. Check that the calling job grants 'actions: read'." >&2
    exit 1
  fi

  # awk rather than `head -1`: head closes the pipe after the first line, and
  # with hundreds of artifacts still to write sort dies of SIGPIPE, which
  # `pipefail` turns into an aborted run.  awk consumes the whole stream.
  run_id="$(printf '%s\n' "$listing" | sort -rk1 | awk 'NR == 1 { print $2 }')"

  if [ -z "$run_id" ]; then
    echo "  ${name}: none published yet"
    continue
  fi

  rm -rf "${DEST:?}/${name}"
  if retry gh run download "$run_id" --name "$name" --dir "${DEST}/${name}" >/dev/null 2>&1; then
    echo "  ${name}: from run ${run_id}"
  else
    rm -rf "${DEST:?}/${name}"
    echo "  ${name}: download failed after ${ATTEMPTS} attempts (run ${run_id})" >&2
    echo "Aborting rather than merging without it. The caller extracts its own" >&2
    echo "tables from the merged database and re-uploads them with" >&2
    echo "overwrite:true, so if ${name} is the caller's own artifact it would" >&2
    echo "be republished holding only this run and its history lost." >&2
    exit 1
  fi
done
