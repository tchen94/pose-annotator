#!/usr/bin/env bash
set -euo pipefail

# Go to repo root
cd "$(dirname "$0")"

# Start the app in the background
bash start.sh &
APP_PID=$!

# Give the server a moment to start
sleep 1

# Open the browser
open "http://localhost:8000"

# Bring logs to the Terminal and keep the process alive
wait $APP_PID