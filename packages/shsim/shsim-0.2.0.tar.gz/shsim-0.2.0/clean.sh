#!/usr/bin/env bash
[ -f _shsim.log ] && rm -rf _shsim.log
[ -d src/shsim.egg-info ] && rm -rf src/shsim.egg-info
[ -d .pytest_cache ] && rm -rf .pytest_cache
[ -d dist ] && rm -rf dist
find . -type d -name "__pycache__" -exec rm -rf {} +
