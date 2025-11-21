# Quick Start - Web Server

Get the Market Research Visualization web server running in minutes!

## Option 1: Docker (Recommended - Easiest)

### Step 1: Generate Initial Data
```bash
# Generate sample visualizations first
docker-compose --profile test up market-viz-test

# This creates the visualizations in the outputs/ folder
# Wait for it to complete (about 2-3 minutes)
```

### Step 2: Start Web Server
```bash
# Start the web server and database
docker-compose up web db

# The server will start on http://localhost:8000
```

### Step 3: Access Dashboard
Open your browser to: **http://localhost:8000**

Navigation should now work perfectly! ✅

---

## Option 2: Local Development

### Prerequisites
- Python 3.11+
- pip

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Generate Initial Data (Optional)
```bash
# Generate sample data
python create_sample_data.py

# Or run full pipeline
python app.py --max-stocks 10
```

### Step 3: Start Server
```bash
# Start the FastAPI server
python -m uvicorn server.main:app --reload --port 8000
```

### Step 4: Access Dashboard
Open: **http://localhost:8000**

---

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

---

## Features

### ✅ Working Now
- **Navigation**: All sidebar links work via HTTP server
- **Static Visualizations**: Bubble charts, sector performance, etc.
- **Animated Visualizations**: Time-series animations
- **API Endpoints**: REST API for market data
- **Health Checks**: `/health` and `/api/status` endpoints

### 🚀 Advanced Features (Configured)
- **Authentication**: JWT-based user auth
- **Database**: PostgreSQL support with SQLAlchemy
- **WebSocket**: Real-time market updates
- **Background Tasks**: Scheduled data refresh
- **User Preferences**: Theme, favorites, etc.

---

## Configuration

### Environment Variables
Copy `env.example` to `.env` and customize:

```bash
# Security
JWT_SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:pass@db:5432/marketviz
# Or for SQLite
DATABASE_URL=sqlite:///./data/market_viz.db

# Updates
MARKET_UPDATE_INTERVAL_MINUTES=15
```

### Docker Compose Services

```bash
# Web server only
docker-compose up web

# Web server + database
docker-compose up web db

# Web server + database + background worker
docker-compose up web db worker

# Stop all services
docker-compose down
```

---

## Authentication (Optional)

### Register a User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "SecurePass123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

Returns: `{ "access_token": "...", "refresh_token": "..." }`

### Use API with Token
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/auth/me
```

---

## Troubleshooting

### Port 8000 Already in Use
```bash
# On Windows
netstat -ano | findstr :8000

# On Linux/Mac
lsof -i :8000

# Change port in docker-compose.yml or when running:
uvicorn server.main:app --port 8080
```

### Database Connection Issues
```bash
# Check database is running
docker ps | grep postgres

# View logs
docker logs market-viz-db

# Reset database
docker-compose down -v
docker-compose up db
```

### Visualizations Not Showing
1. Make sure you generated them first:
   ```bash
   docker-compose --profile test up market-viz-test
   ```

2. Check `/api/status` endpoint:
   ```bash
   curl http://localhost:8000/api/status
   ```

3. Verify outputs directory exists and has HTML files

### Import Errors
Make sure you're in the project root directory and have installed all dependencies:
```bash
cd /path/to/marketresearchvisualization
pip install -r requirements.txt
```

---

## Development

### Hot Reload
```bash
# Server automatically reloads on code changes
uvicorn server.main:app --reload --port 8000
```

### View Logs
```bash
# Docker logs
docker logs -f market-viz-web

# Or check logs directory
tail -f logs/market_viz.log
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Next Steps

1. ✅ **You're Done!** Navigation works via web server
2. 📊 Generate more data: `docker-compose up market-viz` (30 stocks)
3. 🔐 Set up authentication for multi-user access
4. 📡 Enable WebSocket for live updates
5. ⚙️ Configure background tasks for auto-refresh
6. 🚀 Deploy to production with proper security

---

## Production Deployment

### Security Checklist
- [ ] Change `JWT_SECRET_KEY` to a strong random value
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS/TLS
- [ ] Set up proper CORS origins
- [ ] Configure rate limiting
- [ ] Set up monitoring (Sentry)
- [ ] Use environment variables for secrets
- [ ] Enable database backups

### Docker Production
```bash
# Build production image
docker build -f Dockerfile.web -t market-viz-web:prod .

# Run with production settings
docker run -p 8000:8000 \
  -e JWT_SECRET_KEY=your-secret \
  -e DATABASE_URL=postgresql://... \
  market-viz-web:prod
```

---

## Support

- Check `/api/docs` for API documentation
- Review `server/README.md` for detailed architecture
- Check logs in `logs/` directory
- View Docker logs: `docker logs market-viz-web`

Happy analyzing! 📈

