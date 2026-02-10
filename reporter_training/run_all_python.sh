#!/usr/bin/env bash
#
# Run all Python scripts in this folder (version-sorted), capturing logs.
#
# Usage:
#   ./run_all_python.sh
#   ./run_all_python.sh --continue-on-error
#   PYTHON=python3.11 ./run_all_python.sh
#
# Output:
#   ./run_logs/<timestamp>/{summary.txt, <script>.out.log, <script>.err.log}
#

set -uo pipefail

CONTINUE_ON_ERROR=0
PYTHON_BIN="${PYTHON:-python3}"

usage() {
  cat <<'EOF'
Usage: ./run_all_python.sh [--continue-on-error] [--python <python>]

Options:
  --continue-on-error   Keep running even if a script fails.
  --python <python>     Python interpreter to use (default: $PYTHON or python3).
  -h, --help            Show this help text.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --continue-on-error)
      CONTINUE_ON_ERROR=1
      shift
      ;;
    --python)
      if [[ $# -lt 2 ]]; then
        echo "Missing value for --python" >&2
        usage >&2
        exit 2
      fi
      PYTHON_BIN="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python interpreter not found: $PYTHON_BIN" >&2
  exit 127
fi

shopt -s nullglob
all_py=( ./*.py )

if [[ ${#all_py[@]} -eq 0 ]]; then
  echo "No .py files found in: $SCRIPT_DIR" >&2
  exit 1
fi

# Sort files in "natural" (version) order: note_2.py < note_10.py < note_100.py
mapfile -t sorted_py < <(printf '%s\n' "${all_py[@]}" | sed 's|^\./||' | LC_ALL=C sort -V)

run_ts="$(date +%Y%m%d_%H%M%S)"
log_root="$SCRIPT_DIR/run_logs/$run_ts"
mkdir -p "$log_root"

summary_file="$log_root/summary.txt"

{
  echo "Run started: $(date -Is)"
  echo "Directory: $SCRIPT_DIR"
  echo "Python: $PYTHON_BIN ($("$PYTHON_BIN" --version 2>&1))"
  echo "Continue on error: $CONTINUE_ON_ERROR"
  echo "Scripts: ${#sorted_py[@]}"
  echo
} >"$summary_file"

pass_count=0
fail_count=0

for py in "${sorted_py[@]}"; do
  base="$(basename "$py")"
  out_log="$log_root/${base}.out.log"
  err_log="$log_root/${base}.err.log"

  echo "=== RUN $base ===" | tee -a "$summary_file"

  start_epoch="$(date +%s)"
  # Run in this directory so relative paths behave consistently.
  "$PYTHON_BIN" "$py" >"$out_log" 2>"$err_log"
  exit_code=$?
  end_epoch="$(date +%s)"
  duration=$(( end_epoch - start_epoch ))

  if [[ $exit_code -eq 0 ]]; then
    pass_count=$((pass_count + 1))
    echo "PASS ($duration s)" | tee -a "$summary_file"
  else
    fail_count=$((fail_count + 1))
    echo "FAIL exit=$exit_code ($duration s)" | tee -a "$summary_file"
    echo "  stdout: $out_log" | tee -a "$summary_file"
    echo "  stderr: $err_log" | tee -a "$summary_file"
    if [[ $CONTINUE_ON_ERROR -ne 1 ]]; then
      echo | tee -a "$summary_file"
      echo "Stopping at first failure. Re-run with --continue-on-error to keep going." | tee -a "$summary_file"
      break
    fi
  fi

  echo | tee -a "$summary_file"
done

{
  echo "Run finished: $(date -Is)"
  echo "Passed: $pass_count"
  echo "Failed: $fail_count"
  echo "Logs: $log_root"
} | tee -a "$summary_file"

if [[ $fail_count -gt 0 ]]; then
  exit 1
fi

exit 0
