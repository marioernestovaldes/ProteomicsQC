#!/usr/bin/env bash

set -euo pipefail

python_bin="${PYTHON_BIN:-/opt/conda/bin/python}"
max_attempts="${MIGRATE_MAX_ATTEMPTS:-30}"
sleep_seconds="${MIGRATE_RETRY_DELAY_SECONDS:-2}"

attempt=1
while true; do
    if "${python_bin}" manage.py migrate --noinput; then
        break
    fi

    if [[ "${attempt}" -ge "${max_attempts}" ]]; then
        echo "Database migrations failed after ${attempt} attempts." >&2
        exit 1
    fi

    echo "Migration attempt ${attempt} failed; retrying in ${sleep_seconds}s..." >&2
    attempt=$((attempt + 1))
    sleep "${sleep_seconds}"
done

exec "$@"
