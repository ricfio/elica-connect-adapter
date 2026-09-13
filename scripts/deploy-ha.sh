#!/usr/bin/env bash

set -euo pipefail

usage() {
    echo "Usage: $(basename "$0") [--dry-run]"
    echo
    echo "Options:"
    echo "  --dry-run    Show what would be deployed without making changes"
    echo "  -h, --help   Show this help"
}

DRY_RUN=false

case "${1:-}" in
    "")
        ;;
    --dry-run)
        DRY_RUN=true
        ;;
    -h|--help)
        usage
        exit 0
        ;;
    *)
        echo "Error: unknown option: $1"
        echo
        usage
        exit 1
        ;;
esac

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/deploy-ha.env"

if [[ ! -f "$ENV_FILE" ]]; then
    echo "Error: environment file not found:"
    echo "  $ENV_FILE"
    exit 1
fi

source "$ENV_FILE"

if [[ ! -d "$SOURCE_FOLDER" ]]; then
    echo "Error: source folder not found:"
    echo "  $SOURCE_FOLDER"
    exit 1
fi

if [[ ! -d "$TARGET_FOLDER" ]]; then
    echo "Error: target folder not found:"
    echo "  $TARGET_FOLDER"
    exit 1
fi

echo "Deploying Elica Connect Adapter..."
echo
echo "Source: $SOURCE_FOLDER"
echo "Target: $TARGET_FOLDER"

if [[ "$DRY_RUN" == true ]]; then
    echo "Mode: dry-run"
fi

echo

RSYNC_ARGS=(
    -av
    --delete
    --inplace
    --exclude='__pycache__/'
    --exclude='*.pyc'
    --exclude='*.pyo'
)

if [[ "$DRY_RUN" == true ]]; then
    RSYNC_ARGS+=(--dry-run)
fi

rsync "${RSYNC_ARGS[@]}" \
    "$SOURCE_FOLDER/" \
    "$TARGET_FOLDER/"

echo
echo "Deployment completed successfully."
