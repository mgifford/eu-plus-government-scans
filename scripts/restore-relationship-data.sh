#!/usr/bin/env bash
#
# Restore the relationship dataset from the newest `relationship-data` artifact
# when it is newer than what is committed on main.
#
# The relationship scan runs several times a day but commits its output at most
# once a day, because every commit of the 30 MB shards adds to git history and
# history never shrinks.  Runs that do not commit hand their output to the next
# run through the `relationship-data` artifact instead, so each run must start
# from that artifact, not from the (older) committed files.
#
# Rules, in the same spirit as scripts/fetch-metadata-artifacts.sh:
#   - No artifact published: use the committed files.
#   - Committed files newer than the artifact (for example a deliberate reset
#     committed by hand): use the committed files.
#   - Any listing or download failure: abort.  Continuing would scan from stale
#     committed data and then upload it over the newer artifact, losing up to
#     a day of results.
#
# Usage: scripts/restore-relationship-data.sh [data-dir]
# Requires: gh (authenticated, with `actions: read`), GITHUB_REPOSITORY.

set -euo pipefail

DATA_DIR="${1:-docs/data}"
NAME="relationship-data"
# Repository path of the committed index, independent of where DATA_DIR points.
INDEX_PATH="docs/data/relationships/index.json"
: "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY must be set}"

listing="$(gh api --paginate \
  "/repos/${GITHUB_REPOSITORY}/actions/artifacts?per_page=100&name=${NAME}" \
  --jq '.artifacts[] | select(.expired == false)
        | select(.workflow_run.head_branch == "main")
        | "\(.created_at) \(.workflow_run.id)"')" || {
  echo "Aborting: could not list ${NAME} artifacts (check 'actions: read')." >&2
  exit 1
}

# awk rather than `head -1` so sort never dies of SIGPIPE under pipefail.
newest="$(printf '%s\n' "$listing" | sort -rk1 | awk 'NR == 1')"
if [ -z "$newest" ]; then
  echo "${NAME}: none published; using committed data."
  exit 0
fi
read -r created run_id <<<"$newest"

committed="$(gh api \
  "/repos/${GITHUB_REPOSITORY}/commits?sha=main&path=${INDEX_PATH}&per_page=1" \
  --jq '.[0].commit.committer.date // ""')" || {
  echo "Aborting: could not read the last data commit date." >&2
  exit 1
}

# Both timestamps are ISO 8601 UTC with a Z suffix, so they compare as strings.
if [ -n "$committed" ] && [[ ! "$created" > "$committed" ]]; then
  echo "${NAME}: committed data (${committed}) is newer than artifact (${created}); using committed data."
  exit 0
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
if ! gh run download "$run_id" --name "$NAME" --dir "$tmp" >/dev/null; then
  echo "Aborting: download of ${NAME} from run ${run_id} failed." >&2
  exit 1
fi
if [ ! -f "$tmp/relationships/index.json" ]; then
  echo "Aborting: ${NAME} from run ${run_id} has no relationships/index.json." >&2
  exit 1
fi

# Shards can be re-split between runs, so the shard directory is replaced
# outright.  Summaries and snapshots only ever gain files; copy over them.
rm -rf "${DATA_DIR:?}/relationships"
cp -R "$tmp/relationships" "${DATA_DIR}/relationships"
for dir in summaries snapshots; do
  if [ -d "$tmp/$dir" ]; then
    mkdir -p "${DATA_DIR}/$dir"
    cp -R "$tmp/$dir/." "${DATA_DIR}/$dir/"
  fi
done
for file in coverage_report.json dependency-matrix.json dependency-matrix.csv; do
  if [ -f "$tmp/$file" ]; then
    cp "$tmp/$file" "${DATA_DIR}/$file"
  fi
done
echo "${NAME}: restored from run ${run_id} (${created}); last commit ${committed:-none}."
