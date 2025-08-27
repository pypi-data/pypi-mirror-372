#!/bin/bash -e

make setup # should this be moved outside of the file?

attempts=0
echo "🔍 Checking if lila is ready..."
while [ $attempts -lt 30 ]; do
    if [ "$(curl -s -o /dev/null -w '%{http_code}' http://bdit_lila:8080)" -eq 200 ]; then
        break
    fi
    echo "⌛ Waiting for lila to start... (attempt $((attempts + 1)))"
    sleep 1
    attempts=$((attempts + 1))
done

uv run pytest integration
