#!/bin/bash

set -e

CURR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( dirname ${CURR_DIR} )"
REPO="repo"
NAME="ai001"
TAG="prd"

# Run docker buildx create --use before running this script
echo "Running: docker buildx build --platform=linux/amd64,linux/arm64 -t $REPO/$NAME:$TAG $REPO_ROOT"
docker buildx build --platform=linux/amd64,linux/arm64 -t $REPO/$NAME:$TAG $REPO_ROOT --push
