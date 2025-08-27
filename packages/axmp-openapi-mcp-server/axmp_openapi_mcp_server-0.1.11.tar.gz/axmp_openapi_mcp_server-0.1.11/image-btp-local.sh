#!/bin/zsh
set -e

# Load shell configuration to get aliases
if [ -f ~/.zshrc ]; then
    source ~/.zshrc
elif [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi

APP_NAME=axmp-openapi-mcp-server
APP_VERSION=0.1.10-hotfix9

docker build --platform linux/arm64 --tls-verify=false -t localhost/${APP_NAME}:${APP_VERSION} .
