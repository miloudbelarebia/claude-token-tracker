#!/usr/bin/env bash
# Parse les sessions Claude Code puis lance le dashboard
set -euo pipefail
cd "$(dirname "$0")"

# Crée le venv au premier run
if [ ! -d ".venv" ]; then
  echo "📦 Création du venv et installation des dépendances…"
  python3 -m venv .venv
  ./.venv/bin/pip install --quiet -r requirements.txt
fi

PY="./.venv/bin/python"

echo "🔧 Parsing des sessions…"
$PY tracker.py

echo ""
echo "🚀 Lancement du dashboard sur http://localhost:8501"
$PY -m streamlit run app.py
