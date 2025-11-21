# Quick Start Guide

Get up and running with Market Research Visualization in 5 minutes!

## Choose Your Setup Method

### 🐳 Docker (Recommended - Easiest)
**No Python installation needed!** Just Docker.

```bash
# 1. Build the image
docker-compose build

# 2. Run with sample data (2 minutes)
docker-compose --profile test up market-viz-test

# 3. Open outputs/static/dashboard.html in your browser
```

**Benefits:** Zero dependency issues, works everywhere, clean environment.

📖 **See [DOCKER.md](DOCKER.md) for full Docker guide**

---

### 🐍 Python (Alternative)

**Prerequisites:**
- Python 3.8+ installed
- pip package manager
- Internet connection (for data fetching)

## Installation

```bash
# 1. Navigate to the project directory
cd marketresearchvisualization

# 2. Install dependencies
pip install -r requirements.txt
```

## Your First Visualization (3 commands)

```bash
# Run with 20 stocks for quick testing
python app.py --max-stocks 20

# This will:
# - Fetch S&P 500 constituent list
# - Download stock data for 20 stocks
# - Process and calculate metrics
# - Create static visualizations
# - Create animated visualizations
# - Generate reports

# Expected runtime: 2-3 minutes
```

## View Your Results

After the script completes, open these files in your browser:

### Static Visualizations
```
outputs/static/bubble_chart.html          # Main bubble chart
outputs/static/dashboard.html             # Comprehensive dashboard
outputs/static/sector_performance.html    # Sector comparison
```

### Animated Visualizations
```
outputs/animated/animated_bubble_chart.html    # Time-series animation
outputs/animated/animated_swarm_plot.html      # Chartfleau-style swarm
outputs/animated/animated_sector_race.html     # Sector performance race
```

## Next Steps

### Full S&P 500 Analysis
```bash
# Process all ~500 stocks (takes 15-30 minutes first time)
python app.py

# Subsequent runs use cache (much faster)
python app.py
```

### Custom Date Range
```bash
# Last 6 months
python app.py --start-date 2024-05-01 --max-stocks 30

# Specific year
python app.py --start-date 2023-01-01 --end-date 2023-12-31
```

### Weekly Animations (More Frames)
```bash
# Use weekly periods instead of monthly
python app.py --animation-period W --max-stocks 50
```

### Static Only (Faster)
```bash
# Skip animations for quick analysis
python app.py --skip-animated --max-stocks 100
```

## Interactive Examples

Try the interactive examples:

```bash
python examples/example_usage.py

# Select from menu:
# 1. Quick start
# 2. Custom visualization
# 3. Animated visualizations
# 4. Sector analysis
# 5. Complete dashboard
# 6. Specific stocks
```

## Command Line Options

```bash
python app.py --help

# Key options:
--max-stocks N         # Limit number of stocks (for testing)
--start-date YYYY-MM-DD # Start date
--end-date YYYY-MM-DD   # End date
--animation-period M    # M=Monthly, W=Weekly, D=Daily
--skip-animated        # Skip animations (faster)
--no-cache            # Fetch fresh data
```

## Common Use Cases

### Quick Test (30 seconds)
```bash
python app.py --max-stocks 10 --skip-animated
```

### Presentation Ready (5 minutes)
```bash
python app.py --max-stocks 50 --animation-period M
```

### Full Analysis (30 minutes first time, then 2 minutes)
```bash
python app.py
```

### Fresh Data (ignore cache)
```bash
python app.py --no-cache --max-stocks 30
```

## Troubleshooting

**Problem**: Installation fails
```bash
# Try installing core packages first
pip install pandas numpy plotly beautifulsoup4
pip install yfinance
```

**Problem**: Data fetch is slow
```bash
# Normal for first run - downloads all historical data
# Use cache on subsequent runs (automatic)
# Or limit stocks: --max-stocks 20
```

**Problem**: Import errors
```bash
# Make sure you're in the project directory
cd marketresearchvisualization
python app.py
```

## Understanding the Output

### Data Files (`data/`)
- Raw data cached for 24 hours
- Processed CSV files for analysis

### Static Visualizations (`outputs/static/`)
- Interactive HTML charts
- No animation, instant loading
- Good for reports and analysis

### Animated Visualizations (`outputs/animated/`)
- Time-series animations
- Show evolution over time
- Great for presentations and social media

### Reports (`outputs/`)
- `market_report.txt` - Text summary
- `metadata.json` - Run configuration

## Tips for Best Results

1. **First Run**: Use `--max-stocks 20` to test quickly
2. **Production**: Run full S&P 500 once, then use cache
3. **Presentations**: Use `--animation-period W` for smoother animations
4. **Analysis**: Use `--skip-animated` for faster iteration
5. **Fresh Data**: Run `--no-cache` once per day for latest data

## What's Next?

- Read the full [README.md](README.md) for advanced usage
- Check [examples/example_usage.py](examples/example_usage.py) for code samples
- Customize [config.py](config.py) for your preferences
- Explore the source code in `src/` directory

## Support

If you run into issues:
1. Check that all dependencies installed: `pip list | grep -E "pandas|plotly|yfinance"`
2. Verify Python version: `python --version` (should be 3.8+)
3. Try with fewer stocks first: `--max-stocks 10`
4. Check the error message and consult README.md

---

**Happy Visualizing!** 🚀📊
