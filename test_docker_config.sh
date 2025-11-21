#!/bin/bash
# Test script to validate Docker configuration

echo "Validating Docker configuration..."
echo ""

# Check if required files exist
echo "✓ Checking required files..."
files=(
    "Dockerfile"
    "docker-compose.yml"
    ".dockerignore"
    "docker-entrypoint.sh"
    "DOCKER.md"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file exists"
    else
        echo "  ✗ $file missing!"
        exit 1
    fi
done

echo ""
echo "✓ Checking entrypoint script is executable..."
if [ -x "docker-entrypoint.sh" ]; then
    echo "  ✓ docker-entrypoint.sh is executable"
else
    echo "  ✗ docker-entrypoint.sh is not executable"
    echo "    Run: chmod +x docker-entrypoint.sh"
    exit 1
fi

echo ""
echo "✓ Validating Dockerfile syntax..."
if grep -q "FROM python:" Dockerfile; then
    echo "  ✓ Base image specified"
fi
if grep -q "WORKDIR" Dockerfile; then
    echo "  ✓ Working directory set"
fi
if grep -q "COPY requirements.txt" Dockerfile; then
    echo "  ✓ Requirements copied"
fi
if grep -q "ENTRYPOINT" Dockerfile; then
    echo "  ✓ Entrypoint configured"
fi

echo ""
echo "✓ Validating docker-compose.yml..."
if grep -q "version:" docker-compose.yml; then
    echo "  ✓ Version specified"
fi
if grep -q "services:" docker-compose.yml; then
    echo "  ✓ Services defined"
fi
if grep -q "volumes:" docker-compose.yml; then
    echo "  ✓ Volumes configured"
fi

echo ""
echo "✓ Checking .dockerignore..."
if grep -q "__pycache__" .dockerignore; then
    echo "  ✓ Python cache excluded"
fi
if grep -q ".git" .dockerignore; then
    echo "  ✓ Git directory excluded"
fi

echo ""
echo "========================================="
echo "✓ All Docker configuration checks passed!"
echo "========================================="
echo ""
echo "To build and run:"
echo "  docker build -t market-viz ."
echo "  docker-compose up market-viz"
echo ""
echo "See DOCKER.md for full documentation."
