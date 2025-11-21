FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir pandas numpy requests beautifulsoup4 lxml plotly kaleido tqdm python-dateutil && \
    pip install --no-cache-dir --no-deps yfinance

# Create multitasking stub (workaround for yfinance)
RUN echo 'def task(func):\n    return func\n\ndef set_max_threads(n):\n    pass\n\ndef wait_for_tasks():\n    pass\n\n__version__ = "0.0.9"' > /usr/local/lib/python3.11/site-packages/multitasking.py

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/cache outputs/static outputs/animated

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MPLBACKEND=Agg

# Expose port for potential web server (future enhancement)
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Default command
CMD ["--max-stocks", "30"]
