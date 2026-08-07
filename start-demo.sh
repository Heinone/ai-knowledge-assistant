#!/usr/bin/env bash

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

echo
echo "Answer.ly demo"
echo "=============="
echo "1) Reset to Answer.ly"
echo "2) Start Aster & Loom"
echo "3) Start Vertex Systems"
echo "4) Start Northstar eBikes"
echo

read -r -p "Choose demo: " choice

case "$choice" in
  1)
  echo
  echo "Answer.ly setup mode"
  echo "===================="
  echo "1) Internal knowledge"
  echo "2) Customer support"
  echo "3) Both"
  echo

  read -r -p "Choose assistant setup: " mode_choice

  case "$mode_choice" in
    1)
      available_modes="internal_knowledge"
      ;;
    2)
      available_modes="customer_support"
      ;;
    3)
      available_modes="customer_support,internal_knowledge"
      ;;
    *)
      echo "Invalid option."
      exit 1
      ;;
  esac

  echo "Resetting to Answer.ly..."
  venv/bin/python -m scripts.reset_app_state

  printf 'AVAILABLE_MODES=%s\n' "$available_modes" > .env.runtime
  ;;
  2)
    echo "Activating Aster & Loom..."
    venv/bin/python -m scripts.activate_example_company aster_loom --apply
    ;;
  3)
    echo "Activating Vertex Systems..."
    venv/bin/python -m scripts.activate_example_company vertex_systems --apply
    ;;
  4)
    echo "Activating Northstar eBikes..."
    venv/bin/python -m scripts.activate_example_company northstar_ebikes --apply
    ;;
  *)
    echo "Invalid option."
    exit 1
    ;;
esac

cleanup() {
  echo
  echo "Stopping Answer.ly..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
  wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

echo
echo "Starting backend..."
venv/bin/uvicorn app.main:app --reload &
BACKEND_PID=$!

echo "Starting frontend..."
python3 -m http.server 5500 --directory "$PROJECT_ROOT/frontend" &
FRONTEND_PID=$!

echo
echo "Answer.ly is running:"
echo "Admin: http://localhost:5500/admin.html"
echo "Chat:  http://localhost:5500/chat.html"
echo
echo "Press Ctrl+C to stop both servers."
echo

wait