#!/bin/sh
set -u

interval=${SYNC_INTERVAL:-300}
case "$interval" in
    *[!0-9]*|""|0) echo "SYNC_INTERVAL must be a positive number of seconds" >&2; exit 1 ;;
esac
: "${POSTFIX_RECIPIENT_FILE:?POSTFIX_RECIPIENT_FILE must be set}"
target=$POSTFIX_RECIPIENT_FILE

while :; do
    temporary="${target}.tmp"
    if POSTFIX_RECIPIENT_FILE="$temporary" python /app/main.py && postmap "$temporary"; then
        mv -f "$temporary" "$target"
        mv -f "${temporary}.db" "${target}.db"
    else
        echo "Sync failed; will retry in $interval seconds" >&2
        rm -f "$temporary" "${temporary}.db"
    fi
    sleep "$interval"
done
