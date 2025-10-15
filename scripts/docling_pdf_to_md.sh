#!/usr/bin/env bash
set -euo pipefail

# Optional: auto-activate conda env "surveyx" if available
if [[ "${CONDA_DEFAULT_ENV:-}" != "surveyx" ]]; then
  if command -v conda >/dev/null 2>&1; then
    __conda_base="$(conda info --base 2>/dev/null || true)"
    if [[ -n "${__conda_base}" && -f "${__conda_base}/etc/profile.d/conda.sh" ]]; then
      # shellcheck disable=SC1091
      . "${__conda_base}/etc/profile.d/conda.sh" || true
      conda activate surveyx || true
    fi
  fi
fi

# Formal Docling PDF → Markdown converter for SurveyX
#
# Usage:
#   scripts/docling_pdf_to_md.sh <INPUT_PATH> <OUTPUT_DIR> [-- ...extra docling flags]
#
# Environment knobs (optional):
#   DOCLING_ARTIFACTS_PATH   Path to local cached models (default: "$HOME/.cache/docling/models")
#   DOC_IMAGE_MODE           Image export mode: placeholder|embedded|referenced (default: placeholder)
#   DOC_USE_OCRMAC           If set to 1, try to use --ocr-engine ocrmac (only if package available)
#   DOC_OCR_LANG             OCR language (default: en-US)
#   DOC_DEVICE               Device for acceleration (default: auto; on macOS uses mps)
#   DOC_THREADS              --num-threads (default: 2)
#   DOC_PAGE_BATCH           --page-batch-size (default: 2)
#   DOC_FORCE_OVERWRITE      If set to 1, bypass existing-output guard (default: 0)

INPUT_PATH=${1:-}
OUTPUT_DIR=${2:-}
shift 2 || true

if [[ -z "${INPUT_PATH}" || -z "${OUTPUT_DIR}" ]]; then
  echo "Usage: $0 <INPUT_PATH> <OUTPUT_DIR> [-- extra docling flags]" >&2
  exit 2
fi

# Defaults
: "${DOCLING_ARTIFACTS_PATH:="$HOME/.cache/docling/models"}"
: "${DOC_IMAGE_MODE:=placeholder}"
: "${DOC_USE_OCRMAC:=0}"
: "${DOC_OCR_LANG:=en-US}"
: "${DOC_FORCE_OVERWRITE:=0}"

# Device heuristic: prefer MPS on macOS, else leave default
if [[ "$(uname -s)" == "Darwin" ]]; then
  : "${DOC_DEVICE:=mps}"
else
  : "${DOC_DEVICE:=auto}"
fi

: "${DOC_THREADS:=2}"
: "${DOC_PAGE_BATCH:=2}"

# Guard against clobbering existing Markdown outputs unless explicitly allowed
DOC_INPUTS=()
existing_targets=()
if [[ -f "${INPUT_PATH}" ]]; then
  DOC_INPUTS=("${INPUT_PATH}")
  if [[ "${DOC_FORCE_OVERWRITE}" != "1" ]]; then
    input_basename="${INPUT_PATH##*/}"
    input_stem="${input_basename%.*}"
    existing_target="${OUTPUT_DIR%/}/${input_stem}.md"
    if [[ -f "${existing_target}" ]]; then
      echo "[skip] Output already exists: ${existing_target}" >&2
      echo "       Set DOC_FORCE_OVERWRITE=1 to regenerate." >&2
      exit 0
    fi
  fi
elif [[ -d "${INPUT_PATH}" ]]; then
  if [[ "${DOC_FORCE_OVERWRITE}" == "1" ]]; then
    DOC_INPUTS=("${INPUT_PATH}")
  else
    while IFS= read -r -d '' doc_src; do
      doc_base="${doc_src##*/}"
      doc_stem="${doc_base%.*}"
      candidate="${OUTPUT_DIR%/}/${doc_stem}.md"
      if [[ -f "${candidate}" ]]; then
        existing_targets+=("${candidate}")
      else
        DOC_INPUTS+=("${doc_src}")
      fi
    done < <(find "${INPUT_PATH}" -type f -iname '*.pdf' -print0 2>/dev/null)

    if (( ${#DOC_INPUTS[@]} == 0 )); then
      if (( ${#existing_targets[@]} > 0 )); then
        echo "[skip] All matching sources already have Markdown outputs. Set DOC_FORCE_OVERWRITE=1 to overwrite." >&2
        printf '  %s\n' "${existing_targets[@]}" >&2
      else
        echo "[skip] No convertible sources found under ${INPUT_PATH}" >&2
      fi
      exit 0
    fi
  fi
else
  echo "[error] Input path not found: ${INPUT_PATH}" >&2
  exit 1
fi

SKIPPED_COUNT=${#existing_targets[@]:-0}
if (( ${#DOC_INPUTS[@]} == 0 )); then
  echo "[skip] Nothing to convert." >&2
  exit 0
fi

if (( SKIPPED_COUNT > 0 )); then
  echo "[info] Skipping ${SKIPPED_COUNT} existing Markdown outputs." >&2
fi

echo "[info] Converting ${#DOC_INPUTS[@]} source(s)." >&2

DOC_CMD=(docling)
DOC_CMD+=("${DOC_INPUTS[@]}")
DOC_CMD+=(--to md --output "${OUTPUT_DIR}" \
  --image-export-mode "${DOC_IMAGE_MODE}" \
  --num-threads "${DOC_THREADS}" --page-batch-size "${DOC_PAGE_BATCH}")

# Prefer local artifacts
if [[ -n "${DOCLING_ARTIFACTS_PATH:-}" ]]; then
  DOC_CMD+=(--artifacts-path "${DOCLING_ARTIFACTS_PATH}")
fi

# Device
if [[ -n "${DOC_DEVICE}" && "${DOC_DEVICE}" != "auto" ]]; then
  DOC_CMD+=(--device "${DOC_DEVICE}")
fi

# OCR engine (optional ocrmac)
if [[ "${DOC_USE_OCRMAC}" == "1" ]]; then
  if python - <<'PY' >/dev/null 2>&1
import importlib; import sys
sys.exit(0 if importlib.util.find_spec('ocrmac') else 1)
PY
  then
    DOC_CMD+=(--ocr --ocr-engine ocrmac --ocr-lang "${DOC_OCR_LANG}")
  else
    echo "[info] ocrmac not installed, skipping --ocr-engine ocrmac" >&2
    DOC_CMD+=(--ocr)
  fi
else
  # keep default OCR behavior (enabled by Docling, image/bitmap regions only)
  DOC_CMD+=(--ocr)
fi

# Pass-through extra flags after --
if [[ "${1:-}" == "--" ]]; then
  shift
  DOC_CMD+=("$@")
fi

echo "Using DOCLING_ARTIFACTS_PATH=${DOCLING_ARTIFACTS_PATH}"
echo "Running: ${DOC_CMD[*]}"
"${DOC_CMD[@]}"

echo
echo "Listing generated files (up to 20):"
find "${OUTPUT_DIR}" -type f | head -n 20 || true
echo "Done. Markdown output at: ${OUTPUT_DIR}"
