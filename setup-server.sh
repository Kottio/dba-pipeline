#!/usr/bin/env bash
set -euo pipefail

# Machine-level recipe: everything uv CANNOT carry (binaries, pinned).
# macOS: brew · droplet (Ubuntu): see comments. This file is the Dockerfile's first draft.

# uv — Python toolchain
curl -LsSf https://astral.sh/uv/install.sh | sh

# DuckDB CLI (pinned 1.5.4)
curl https://install.duckdb.org | sh

# just — command runner (see justfile)
brew install just              # droplet: apt install just  (or prebuilt binary)

# dbt Fusion (pinned 2.0.0-preview.196 — .200 untested beyond the exam, upgrade deliberately)
curl -fsSL https://public.cdn.getdbt.com/fs/install/install.sh | sh
