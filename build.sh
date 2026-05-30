#!/bin/bash
set -e

# Generate version.txt: [git revision] Build: [timestamp]
GIT_REV=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# Registry details
REGISTRY="registry.shifamily.com"
REPOSITORY="homestack/stock-check-mcp"
IMAGE_TAG_LATEST="${REGISTRY}/${REPOSITORY}:latest"
IMAGE_TAG_REV="${REGISTRY}/${REPOSITORY}:${GIT_REV}"

echo "Building docker image..."
docker build --build-arg "GIT_REV=${GIT_REV}" -t "${IMAGE_TAG_LATEST}" -t "${IMAGE_TAG_REV}" .

echo "Pushing docker image tags..."
echo "Pushing ${IMAGE_TAG_LATEST}..."
docker push "${IMAGE_TAG_LATEST}"

echo "Pushing ${IMAGE_TAG_REV}..."
docker push "${IMAGE_TAG_REV}"

echo "Docker build and push completed successfully!"
