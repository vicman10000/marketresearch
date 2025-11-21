# Docker Deployment Guide

This guide explains how to run the Market Research Visualization application using Docker, which simplifies deployment and eliminates dependency issues.

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose (included with Docker Desktop)

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Build and run with default settings (30 stocks)
docker-compose up market-viz

# Run with sample data (fast test)
docker-compose --profile test up market-viz-test

# Run full S&P 500 analysis
docker-compose --profile full up market-viz-full
```

After completion, find your visualizations in `./outputs/`

### Option 2: Using Docker Directly

```bash
# Build the image
docker build -t market-viz .

# Run with volume mounts
docker run -v $(pwd)/outputs:/app/outputs \
           -v $(pwd)/data:/app/data \
           market-viz --max-stocks 30

# Run with sample data
docker run -e USE_SAMPLE_DATA=true \
           -v $(pwd)/outputs:/app/outputs \
           market-viz --max-stocks 10
```

## Docker Compose Services

### 1. Default Service: `market-viz`
```bash
docker-compose up market-viz
```
- Processes 30 stocks
- Monthly animation periods
- Uses real data from Yahoo Finance (or cache)

### 2. Test Service: `market-viz-test`
```bash
docker-compose --profile test up market-viz-test
```
- Generates sample data (fast)
- Processes 10 stocks
- Perfect for testing the application

### 3. Full Service: `market-viz-full`
```bash
docker-compose --profile full up market-viz-full
```
- Processes all ~500 S&P 500 stocks
- Takes 15-30 minutes on first run
- Subsequent runs use cache (much faster)

## Command Line Options

Pass arguments to the application:

```bash
# Custom date range
docker-compose run market-viz --start-date 2023-01-01 --end-date 2023-12-31 --max-stocks 50

# Weekly animation periods
docker-compose run market-viz --animation-period W --max-stocks 100

# Skip animations (faster)
docker-compose run market-viz --skip-animated --max-stocks 50

# Use fresh data (ignore cache)
docker-compose run market-viz --no-cache --max-stocks 30
```

## Environment Variables

Configure via `.env` file or command line:

```bash
# .env file
USE_SAMPLE_DATA=false
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

Or inline:

```bash
docker-compose run -e USE_SAMPLE_DATA=true market-viz
```

## Volume Mounts

The Docker setup uses two volumes:

### 1. Outputs Volume: `./outputs:/app/outputs`
Contains generated visualizations:
- `outputs/static/` - Static HTML charts
- `outputs/animated/` - Animated HTML charts
- `outputs/market_report.txt` - Text report
- `outputs/metadata.json` - Run metadata

### 2. Data Volume: `./data:/app/data`
Contains cached data:
- `data/cache/` - Cached API responses
- `data/*.csv` - Processed datasets

**Benefits:**
- Visualizations are immediately accessible on your host
- Cache persists between runs (faster subsequent runs)
- Data survives container deletion

## Common Use Cases

### Quick Demo (2 minutes)
```bash
docker-compose --profile test up market-viz-test
```

### Production Analysis (30 stocks)
```bash
docker-compose up market-viz
```

### Full S&P 500 Report (30 minutes first time)
```bash
docker-compose --profile full up market-viz-full
```

### Custom Analysis
```bash
docker-compose run market-viz \
  --start-date 2024-01-01 \
  --max-stocks 50 \
  --animation-period W
```

### With Your API Key
```bash
docker-compose run \
  -e ALPHA_VANTAGE_API_KEY=your_key_here \
  market-viz --max-stocks 100
```

## Viewing Results

After the container finishes:

```bash
# List generated files
ls -lh outputs/static/
ls -lh outputs/animated/

# Open in browser (macOS)
open outputs/static/dashboard.html

# Open in browser (Linux)
xdg-open outputs/static/dashboard.html

# Open in browser (Windows)
start outputs/static/dashboard.html
```

## Building the Image

### Standard Build
```bash
docker build -t market-viz .
```

### Build with Different Tag
```bash
docker build -t myregistry/market-viz:v1.0 .
```

### Build with No Cache (fresh build)
```bash
docker build --no-cache -t market-viz .
```

## Troubleshooting

### Issue: Container exits immediately
**Solution:** Check logs:
```bash
docker-compose logs market-viz
```

### Issue: No visualizations generated
**Solution:** Check that volumes are mounted:
```bash
docker-compose run market-viz ls -la /app/outputs
```

### Issue: "Permission denied" on outputs
**Solution:** Fix permissions:
```bash
sudo chown -R $USER:$USER outputs/ data/
```

### Issue: Out of memory
**Solution:** Increase Docker memory limit (Docker Desktop → Preferences → Resources)

### Issue: API rate limiting
**Solution:** Use sample data or cache:
```bash
# Use sample data
docker-compose run -e USE_SAMPLE_DATA=true market-viz

# Or use cached data (run twice)
docker-compose up market-viz  # First run (slow)
docker-compose up market-viz  # Second run (fast, uses cache)
```

## Advanced Usage

### Run Interactive Shell
```bash
docker-compose run --entrypoint /bin/bash market-viz
```

### Copy Files from Container
```bash
# Get container ID
docker ps -a

# Copy outputs
docker cp CONTAINER_ID:/app/outputs ./my-outputs
```

### Run Examples
```bash
docker-compose run --entrypoint python market-viz examples/example_usage.py
```

### Debug Mode
```bash
docker-compose run --entrypoint /bin/bash market-viz
# Inside container:
python app.py --max-stocks 5
```

## Performance Tips

### 1. Use Cache
- First run downloads all data (slow)
- Subsequent runs use cache (fast)
- Cache expires after 24 hours (configurable)

### 2. Limit Stocks for Testing
```bash
docker-compose run market-viz --max-stocks 20
```

### 3. Skip Animations
```bash
docker-compose run market-viz --skip-animated
```

### 4. Use Sample Data for Development
```bash
docker-compose --profile test up market-viz-test
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Generate Market Visualizations

on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9am

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: docker build -t market-viz .

      - name: Run visualization
        run: |
          docker run -v $(pwd)/outputs:/app/outputs \
                     market-viz --max-stocks 100

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: visualizations
          path: outputs/
```

### Docker Hub Deployment
```bash
# Tag image
docker tag market-viz username/market-viz:latest

# Push to Docker Hub
docker push username/market-viz:latest

# Others can pull and run
docker pull username/market-viz:latest
docker run -v $(pwd)/outputs:/app/outputs username/market-viz:latest
```

## Cleanup

### Remove Containers
```bash
docker-compose down
```

### Remove Containers and Volumes
```bash
docker-compose down -v
```

### Remove Images
```bash
docker rmi market-research-visualization:latest
```

### Full Cleanup
```bash
docker-compose down -v
docker system prune -a
```

## Production Deployment

### AWS ECS / Fargate
1. Push image to ECR
2. Create ECS task definition
3. Mount EFS for persistent cache
4. Configure S3 for outputs

### Kubernetes
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: market-viz
spec:
  schedule: "0 9 * * 1"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: market-viz
            image: market-viz:latest
            args: ["--max-stocks", "100"]
            volumeMounts:
            - name: outputs
              mountPath: /app/outputs
          volumes:
          - name: outputs
            persistentVolumeClaim:
              claimName: market-viz-outputs
          restartPolicy: OnFailure
```

## Support

For issues or questions:
- Check the main [README.md](README.md)
- Review [QUICKSTART.md](QUICKSTART.md)
- Open an issue on GitHub

---

**Pro Tip**: Use `docker-compose run` instead of `docker-compose up` when you want to pass custom arguments to the application!
