#!/bin/bash
# Build multi-architecture Docker images
# Builds for both ARM64 (Apple Silicon) and x86_64 (Intel Mac/PC)

set -e

echo "=========================================="
echo "Multi-Architecture Docker Build"
echo "=========================================="

# Check if buildx is available
if ! docker buildx version &> /dev/null; then
    echo "❌ docker buildx not found"
    echo "   Install Docker Desktop (includes buildx)"
    exit 1
fi

# Create builder if it doesn't exist
if ! docker buildx ls | grep -q "multiplatform"; then
    echo "📦 Creating multiplatform builder..."
    docker buildx create --name multiplatform --use
else
    echo "✅ Using existing multiplatform builder"
    docker buildx use multiplatform
fi

# Inspect builder
docker buildx inspect --bootstrap

echo ""
echo "=========================================="
echo "Building for multiple platforms..."
echo "=========================================="
echo "Platforms: linux/amd64, linux/arm64"
echo "Image: live-vlm-webui:multiarch"
echo ""

# Build for both platforms
# Note: Multi-arch images must be pushed to registry, can't be loaded locally
echo "⚠️  Multi-arch images must be pushed to a registry"
echo "   They cannot be loaded to local Docker"
echo ""
read -p "Do you want to push to a registry? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter registry URL (e.g., username/live-vlm-webui): " REGISTRY_URL

    if [ -z "$REGISTRY_URL" ]; then
        echo "❌ Registry URL required"
        exit 1
    fi

    echo ""
    echo "Building and pushing to: $REGISTRY_URL"
    echo ""

    docker buildx build \
      --platform linux/amd64,linux/arm64 \
      -f Dockerfile.mac \
      -t "$REGISTRY_URL:mac" \
      --push \
      .

    echo ""
    echo "=========================================="
    echo "✅ Multi-arch build complete!"
    echo "=========================================="
    echo ""
    echo "Image pushed to: $REGISTRY_URL:mac"
    echo "Platforms:"
    echo "  - linux/amd64 (Intel Mac, PC)"
    echo "  - linux/arm64 (Apple Silicon Mac)"
    echo ""
    echo "Pull on any platform with:"
    echo "  docker pull $REGISTRY_URL:mac"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "Building for local platform only..."
    echo "=========================================="
    echo ""

    # Build for current platform only
    docker build -f Dockerfile.mac -t live-vlm-webui:mac .

    echo ""
    echo "✅ Single-arch build complete!"
    echo "Image: live-vlm-webui:mac"
    echo ""
fi

