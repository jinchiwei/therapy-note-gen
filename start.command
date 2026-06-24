#!/bin/bash
# Therapy Note Generator - double-click launcher (macOS / Linux)
# Activates the conda env, starts the app, opens the browser.
# (On macOS you can double-click this file in Finder.)

cd "$(dirname "$0")" || exit 1

ENV_NAME="therapy-note-gen"   # edit if your conda env has a different name

# load conda, then activate the env
source "$(conda info --base 2>/dev/null)/etc/profile.d/conda.sh" 2>/dev/null
if ! conda activate "$ENV_NAME" 2>/dev/null; then
  echo "Could not activate conda env '$ENV_NAME'."
  echo "Create it with: conda create -n $ENV_NAME python=3.12"
  read -r -p "Press Enter to close..."
  exit 1
fi

python app.py
