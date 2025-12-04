#!/bin/sh

# Load the environment based on non-comment lines in .env, then run the app.
env -S $(grep -v '^\s*#' .env) uv run python main.py
