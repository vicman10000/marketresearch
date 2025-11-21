#!/bin/bash
set -e

echo "============================================"
echo "Market Research Visualization - Docker"
echo "============================================"
echo ""

# Check if we should generate sample data
if [ "$USE_SAMPLE_DATA" = "true" ]; then
    echo "Generating sample data..."
    python create_sample_data.py
fi

# Run the main application
echo "Starting market visualization..."
python app.py "$@"

echo ""
echo "============================================"
echo "Visualizations complete!"
echo "============================================"
echo ""
echo "To access the files, copy them from the container:"
echo "  docker cp CONTAINER_ID:/app/outputs ./outputs"
echo ""
echo "Or mount a volume when running:"
echo "  docker run -v \$(pwd)/outputs:/app/outputs market-viz"
