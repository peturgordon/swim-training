#!/usr/bin/env bash
# Verifies:
#   1. Every practices/*.md file has a matching link in practices/index.md
#   2. Every relative (internal) link in every .md/.html file resolves to a real file
#
# Does not check external (http/https) links — deliberately, to keep this fast and
# reliable rather than flaky against third-party sites being slow/down/rate-limiting.
#
# Run locally with: bash scripts/check-links.sh   (from the repo root)

set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

fail=0

echo "== Checking practices/index.md completeness =="
for f in practices/*.md; do
  base="$(basename "$f")"
  [ "$base" = "index.md" ] && continue
  if ! grep -q "$base" practices/index.md; then
    echo "MISSING LINK: $base is not linked from practices/index.md"
    fail=1
  fi
done

echo ""
echo "== Checking internal links resolve =="

check_file_links() {
  local file="$1"
  local dir
  dir="$(dirname "$file")"
  local targets

  case "$file" in
    *.md)   targets=$(grep -oE '\]\([^)]+\)' "$file" | sed 's/^](//;s/)$//') ;;
    *.html) targets=$(grep -oE 'href="[^"]+"' "$file" | sed 's/href="//;s/"$//') ;;
    *) return ;;
  esac

  while IFS= read -r target; do
    [ -z "$target" ] && continue
    case "$target" in
      http://*|https://*) continue ;;
    esac
    # strip a trailing #fragment; if nothing's left, it was a pure in-page anchor
    local path="${target%%#*}"
    [ -z "$path" ] && continue
    if [ ! -e "$dir/$path" ]; then
      echo "BROKEN LINK: $file -> $target"
      fail=1
    fi
  done <<< "$targets"
}

while IFS= read -r -d '' f; do
  check_file_links "$f"
done < <(find . -path ./.git -prune -o \( -name "*.md" -o -name "*.html" \) -print0)

echo ""
if [ "$fail" -ne 0 ]; then
  echo "FAILED: one or more checks above need fixing."
  exit 1
else
  echo "OK: all checks passed."
  exit 0
fi
