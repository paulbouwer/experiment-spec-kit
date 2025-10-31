#!/bin/bash

echo ----------------------------------------------
echo Devcontainer post-create script running...
echo ----------------------------------------------

# Install spec-kit
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git