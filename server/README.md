# Market Research Visualization - Web Server

FastAPI-based web server for real-time market analytics with authentication, WebSocket support, and API access.

## Quick Start

### Using Docker (Recommended)

```bash
# 1. Start the web server and database
docker-compose up web db

# 2. Generate visualizations (optional, in another terminal)
docker-compose run --rm market-viz-test

# 3. Access the dashboard
open http://localhost:8000
```

### Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server
python -m uvicorn server.main:app --reload

# 3. Access the dashboard
open http://localhost:8000
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## Available Endpoints

### Health & Status
- `GET /health` - Health check
- `GET /api/status` - API status and available visualizations

### Market Data (Phase 2)
- `GET /api/stocks` - List all stocks
- `GET /api/stocks/{symbol}` - Get stock details
- `GET /api/sectors` - Sector performance
- `POST /api/data/refresh` - Trigger data refresh

### Analytics (Phase 2)
- `GET /api/analytics/summary` - Dashboard summary
- `GET /api/analytics/top-performers` - Top performers
- `GET /api/analytics/sector-breakdown` - Sector breakdown

### Authentication (Phase 4)
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user
- `PUT /api/auth/preferences` - Update preferences

### WebSocket (Phase 5)
- `WS /api/ws/market-updates` - Real-time market data
- `WS /api/ws/notifications` - User notifications

## Configuration

Copy `env.example` to `.env` and configure:

```bash
# Required
JWT_SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost:5432/marketviz

# Optional
ALPHA_VANTAGE_API_KEY=your-api-key
ENABLE_SCHEDULER=true
```

## Architecture

```
server/
├── main.py              # FastAPI application
├── config.py            # Configuration
├── api/                 # API endpoints
│   ├── market_data.py   # Market data endpoints
│   └── analytics.py     # Analytics endpoints
├── auth/                # Authentication
│   ├── security.py      # JWT & password hashing
│   ├── routes.py        # Auth endpoints
│   └── dependencies.py  # Auth dependencies
├── models/              # Database models
│   ├── user.py          # User model
│   └── market_data.py   # Market data models
├── websocket/           # WebSocket support
│   ├── manager.py       # Connection manager
│   └── routes.py        # WebSocket routes
└── tasks/               # Background tasks
    └── scheduler.py     # Scheduled jobs
```

## Development

### Run with hot reload
```bash
uvicorn server.main:app --reload --port 8000
```

### Run tests
```bash
pytest tests/ -v
```

### Database migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Deployment

### Docker
```bash
# Build
docker build -f Dockerfile.web -t market-viz-web .

# Run
docker run -p 8000:8000 market-viz-web
```

### Production
```bash
# Use gunicorn with uvicorn workers
gunicorn server.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## Troubleshooting

### Port already in use
```bash
# Check what's using port 8000
lsof -i :8000
# or on Windows
netstat -ano | findstr :8000
```

### Database connection issues
```bash
# Check database is running
docker ps | grep postgres

# Check logs
docker logs market-viz-db
```

### Visualizations not showing
1. Generate visualizations first: `docker-compose run --rm market-viz-test`
2. Check `/api/status` endpoint for available visualizations
3. Verify outputs directory is mounted correctly

