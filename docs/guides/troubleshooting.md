# Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### Problem: `ModuleNotFoundError: No module named 'yfinance'`

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

If that doesn't work, try installing packages individually:
```bash
pip install pandas numpy plotly beautifulsoup4 yfinance requests tqdm
```

#### Problem: Permission denied during installation

**Solution**: Use user installation or virtual environment
```bash
# Option 1: Install for user only
pip install --user -r requirements.txt

# Option 2: Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Problem: Conflicting package versions

**Solution**: Use a fresh virtual environment
```bash
# Remove old environment
rm -rf venv  # On Windows: rmdir /s venv

# Create fresh environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Data Fetching Issues

#### Problem: Data fetching is very slow

**Cause**: First run downloads historical data for all stocks

**Solutions**:
```bash
# 1. Use fewer stocks for testing
python app.py --max-stocks 20

# 2. Use cache on subsequent runs (automatic)
python app.py  # Second run is much faster

# 3. Use sample data for development
python app.py --use-sample-data
```

#### Problem: yfinance fails to fetch data

**Possible Causes**:
- Yahoo Finance API is temporarily down
- Rate limiting by Yahoo Finance
- Network connectivity issues
- Invalid stock symbols

**Solutions**:
```bash
# 1. Wait and retry later
python app.py --no-cache

# 2. Use fewer stocks to avoid rate limits
python app.py --max-stocks 30

# 3. Check your internet connection
ping yahoo.com

# 4. Use sample data for testing
python app.py --use-sample-data
```

#### Problem: Some stocks fail to download

**Cause**: Delisted stocks or invalid symbols in S&P 500 list

**Solution**: This is normal - the application will skip failed stocks and continue
```python
# The application logs which stocks failed
# Check the logs for details
```

### Performance Issues

#### Problem: Animations are choppy or slow to load

**Solutions**:
```bash
# 1. Reduce number of stocks
python app.py --max-stocks 50

# 2. Use monthly periods instead of weekly
python app.py --animation-period M

# 3. Skip animations entirely for faster processing
python app.py --skip-animated

# 4. Increase your browser's JavaScript heap size
# Chrome: --js-flags="--max-old-space-size=4096"
```

#### Problem: Memory errors with full S&P 500

**Solutions**:
```bash
# 1. Process in batches
python app.py --max-stocks 250

# 2. Increase system swap/virtual memory

# 3. Use database storage (more efficient)
# Set in .env: USE_DATABASE=true
```

#### Problem: Plotly visualizations fail to render

**Solutions**:
```bash
# 1. Update Plotly
pip install --upgrade plotly

# 2. Clear browser cache
# Chrome: Ctrl+Shift+Del

# 3. Try different browser
# Chrome, Firefox, Safari, Edge are all supported
```

### Import/Path Issues

#### Problem: `ImportError: No module named 'src'`

**Solution**: Make sure you're in the correct directory
```bash
cd marketresearchvisualization  # Or your project directory
python app.py
```

#### Problem: Files not found errors

**Solution**: Check current working directory
```bash
# Should be in project root
pwd  # On Windows: cd

# Should see these directories
ls  # On Windows: dir
# Expected: src/ data/ outputs/ examples/
```

### Docker Issues

#### Problem: Docker container exits immediately

**Solution**: Check logs for errors
```bash
docker-compose logs market-viz

# Common issues:
# - Volume mount permissions
# - Environment variable issues
# - Network connectivity
```

#### Problem: No visualizations generated in Docker

**Solution**: Check volume mounts
```bash
# Verify volumes are mounted correctly
docker-compose run market-viz ls -la /app/outputs

# Fix permissions if needed (Linux/Mac)
sudo chown -R $USER:$USER outputs/ data/
```

#### Problem: Docker out of memory

**Solution**: Increase Docker memory limit
```
Docker Desktop → Preferences → Resources
Set Memory to at least 4GB
```

### Configuration Issues

#### Problem: Environment variables not being read

**Solution**: Check .env file location and format
```bash
# .env file should be in project root
ls -la .env

# Check format (no spaces around =)
cat .env
# Correct: LOG_LEVEL=INFO
# Incorrect: LOG_LEVEL = INFO
```

#### Problem: Log file not being created

**Solution**: Ensure directory exists and permissions are correct
```bash
# Create logs directory
mkdir -p logs

# Check permissions (Linux/Mac)
chmod 755 logs
```

### Visualization Issues

#### Problem: Charts display but are empty

**Possible Causes**:
- No valid data after processing
- All stocks filtered out
- Data validation failures

**Solution**: Check the data files and logs
```bash
# Check if data files exist
ls -la data/*.csv

# Check logs for errors
cat logs/market_viz.log  # If logging is enabled

# Try with fewer stocks to isolate issue
python app.py --max-stocks 5
```

#### Problem: Sector colors don't display correctly

**Solution**: Clear cache and regenerate
```bash
# Remove cache
rm -rf data/cache/*

# Regenerate with fresh data
python app.py --no-cache --max-stocks 30
```

### Database Issues

#### Problem: Database connection errors

**Solution**: Check database URL and permissions
```bash
# For SQLite, ensure directory exists
mkdir -p data

# Check DATABASE_URL in .env
cat .env | grep DATABASE_URL

# Example: DATABASE_URL=sqlite:///./data/market.db
```

#### Problem: Migration errors with Alembic

**Solution**: Reset database (for development)
```bash
# Backup first!
cp data/market.db data/market.db.backup

# Drop all tables and recreate
rm data/market.db
python -c "from src.database import create_tables; create_tables()"
```

### Testing Issues

#### Problem: Tests fail with import errors

**Solution**: Install test dependencies
```bash
pip install pytest pytest-cov pytest-mock
```

#### Problem: Tests timeout or hang

**Solution**: Skip slow tests
```bash
pytest -m "not slow"
```

### API Key Issues

#### Problem: Alpha Vantage API key not working

**Solutions**:
```bash
# 1. Verify key is correct
echo $ALPHA_VANTAGE_API_KEY

# 2. Set in .env file
echo "ALPHA_VANTAGE_API_KEY=your_key_here" >> .env

# 3. Note: yfinance doesn't require API key (default)
```

## Debugging Tips

### Enable Debug Logging

```bash
# Set in .env file
LOG_LEVEL=DEBUG

# Or via environment variable
export LOG_LEVEL=DEBUG
python app.py
```

### Check System Requirements

```bash
# Python version (should be 3.8+)
python --version

# Pip version
pip --version

# Available memory
free -h  # Linux
top  # Mac
wmic OS get FreePhysicalMemory  # Windows PowerShell

# Disk space
df -h  # Linux/Mac
wmic logicaldisk get size,freespace  # Windows
```

### Verify Dependencies

```bash
# List installed packages
pip list

# Check specific packages
pip show pandas plotly yfinance
```

### Generate Diagnostic Report

```python
# Run this to get system info
import sys
import platform
import pandas as pd
import plotly
import yfinance as yf

print(f"Python: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Pandas: {pd.__version__}")
print(f"Plotly: {plotly.__version__}")
print(f"yfinance: {yf.__version__}")
```

## Getting More Help

If your issue isn't covered here:

1. **Check Documentation**
   - [Quickstart Guide](../quickstart.md)
   - [Architecture Documentation](../development/architecture.md)
   - [API Reference](../api/overview.md)

2. **Search Issues**
   - Check GitHub issues for similar problems
   - Search closed issues for solutions

3. **Create an Issue**
   - Include error messages
   - Include steps to reproduce
   - Include system information
   - Include relevant logs

4. **Community Support**
   - Ask in GitHub Discussions
   - Check Stack Overflow

## Best Practices to Avoid Issues

1. **Always use a virtual environment**
2. **Keep dependencies updated** (but test after updating)
3. **Use Docker for consistent environment**
4. **Start with fewer stocks for testing**
5. **Enable caching** to speed up subsequent runs
6. **Monitor system resources** when processing large datasets
7. **Keep backups** of important data
8. **Read error messages carefully** - they often contain the solution

---

**Still having issues?** Open an issue on GitHub with:
- Error message (full traceback)
- Steps to reproduce
- System information (OS, Python version, etc.)
- What you've already tried

