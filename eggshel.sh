#!/usr/bin/env bash
set -e

# runs an eggshel program, appends output to the file
while IFS= read -r line || [ -n "$line" ]; do
    [ -z "$line" ] && continue
    name=$(echo "$line" | awk '{print $1}')
    program=$(echo "$line" | cut -d' ' -f2-)
    python3 -c "from scripts.generate import generate_program; generate_program('$name', '$program')"
    python3 -c "from scripts.runner import run_program; run_program('$name')"
done < "$1"
