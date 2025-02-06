#!/usr/bin/env bash

for python in 3.9 3.10 3.11 3.12 3.13; do
  uv run --frozen --isolated --python=$python pytest
done
