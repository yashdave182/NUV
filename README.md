# AgriTech API - Real-time Agricultural Advisory System

A production-ready FastAPI backend for the **TetraTHON 2026 Indo-French AI Hackathon** providing real-time agricultural intelligence for smallholder farmers in India.

## 🚀 Features

### Real-time Data Integration
- **Weather**: OpenWeather, WeatherAPI, Visual Crossing, NASA POWER
- **Market Prices**: Agmarknet, data.gov.in, e-NAM mandi prices
- **Satellite**: Sentinel Hub (NDVI, EVI, soil moisture, crop health)
- **Soil Health**: ICAR Soil Health Card, state portals

### ML-Powered Predictions
| Model | Type | Target Crops |
|-------|------|--------------|
| **Yield Predictor** | Gradient Boosting | Cotton, Groundnut, Wheat, Bajra, Maize, Cumin, Castor |
| **Price Forecaster** | Prophet + ML | All major crops (14-day horizon) |
| **Disease Risk** | Gradient Boosting Classifier | 18 diseases across 6 crops |
| **Irrigation Optimizer** | Multi-target GBRT | All crops + soil types |
| **Fertilizer Optimizer** | Multi-target GBRT | NPK + micronutrients |

### API Endpoints (30+)
- **Agriculture** (9): Advisory, Irrigation, Fertilizer, Pest/Disease, Calendar, Soil Health, Variety, Intercropping, Insurance, Weather
- **Market** (10): Mandi Prices, Trends, Sell Decisions, Transport, Storage, Spoilage, Alerts
- **Livestock** (8): Vaccination, Deworming, Feed, Diagnosis, Breeding, Milk Quality, Alerts, Schemes
- **Health** (4): Advisory, Vaccination, Camps, Triage
- **Schemes** (4): Search, Details, Tracking, Eligibility

## 📦 Quick Start

### 1. Install Dependencies
```bash
cd backend/agritech_api
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Train ML Models (First Run)
```bash
python ml_models/training/train_models.py
# Or use the start script:
python start.py train
```

### 4. Run Server
```bash
python start.py run
# Or directly:
uvicorn main:app --host 0.0.0.0 --port 7860 --reload
```

### 5. Access API
- **Swagger UI**: http://localhost:7860/docs
- **ReDoc**: http://localhost:7860/redoc
- **Health Check**: http://localhost:7860/health

## 🐳 Docker Deployment

```bash
# Build and run all services
docker-compose up -d

# Train models (run once)
docker-compose run --rm model-trainer

# View logs
docker-compose logs -f agritech-api
```

## 🔑 Required API Keys

| Service | Purpose | Free Tier |
|---------|---------|-----------|
| OpenWeather | Weather forecast | 1000 calls/day |
| WeatherAPI | Weather + historical | 1M calls/month |
| Agmarknet | Mandi prices | Government portal |
| data.gov.in | Mandi prices | 1000 calls/day |
| Sentinel Hub | Satellite imagery | 5000 requests/month |
| NASA POWER | Weather + soil | No key required |
| ICAR Soil | Soil health cards | Government portal |

## 📊 Example API Usage

### Get Farm Advisory
```bash
curl -X POST "http://localhost:7860/agriculture/advisory" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "9876543210",
    "location": {"latitude": 23.0, "longitude": 72.0, "state": "Gujarat", "district": "Ahmedabad", "taluka": "Daskroi", "village": "Bavla"},
    "crop_type": "cotton",
    "season": "kharif",
    "sowing_date": "2026-06-15",
    "area_hectares": 2.5,
    "soil_type": "black_cotton",
    "irrigation_source": "borewell",
    "language": "gujlish"
  }'
```

### Get Real Mandi Prices
```bash
curl -X POST "http://localhost:7860/market/mandi-prices" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "9876543210",
    "crop_type": "cotton",
    "location": {"state": "Gujarat"},
    "language": "gujlish"
  }'
```

### Get Price Forecast (ML)
```bash
curl -X POST "http://localhost:7860/market/price-forecast" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "9876543210",
    "crop_type": "cotton",
    "horizon_days": 14,
    "language": "gujlish"
  }'
```

## 🏗 Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  External APIs  │────▶│  Data Clients    │────▶│  ML Models      │
│  (Weather,      │     │  (Weather,       │     │  (Yield, Price, │
│   Mandi, Sat,   │     │   Mandi, Sat,    │     │   Disease,      │
│   Soil)         │     │   Soil)          │     │   Irrigation,   │
└─────────────────┘     └──────────────────┘     │   Fertilizer)   │
                                                 └────────┬────────┘
                                                          │
                          ┌──────────────────┐            │
                          │  Services Layer  │◀-----------┘
                          │  (Agriculture,   │
                          │   Market,        │
                          │   Weather,       │
                          │   Livestock)     │
                          └────────┬─────────┘
                                   │
                          ┌────────▼─────────┐
                          │  FastAPI Routers │
                          │  (REST Endpoints)│
                          └────────┬─────────┘
                                   │
                          ┌────────▼─────────┐
                          │  SMS Backend     │
                          │  (VaaniAI)       │
                          └──────────────────┘
```

## 📁 Project Structure

```
backend/agritech_api/
├── main.py                    # FastAPI app entry
├── start.py                   # Management script
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── Dockerfile                 # Production container
├── Dockerfile.training        # Training container
├── clients/                   # External API clients
│   ├── weather_client.py
│   ├── mandi_client.py
│   ├── satellite_client.py
│   └── soil_client.py
├── ml_models/                 # ML models & training
│   ├── model_manager.py
│   ├── yield_model.py
│   ├── price_model.py
│   ├── disease_model.py
│   ├── irrigation_model.py
│   ├── fertilizer_model.py
│   └── training/
│       └── train_models.py
├── services/                  # Business logic
│   ├── agriculture_service.py
│   ├── market_service.py
│   ├── weather_service.py
│   ├── livestock_service.py
│   ├── health_service.py
│   └── schemes_service.py
├── routers/                   # API endpoints
│   ├── agriculture.py
│   ├── market.py
│   ├── health.py
│   ├── schemes.py
│   └── livestock.py
├── schemas/                   # Pydantic models
│   ├── agriculture.py
│   ├── market.py
│   ├── livestock.py
│   ├── health.py
│   └── common.py
└── models/                    # Trained models (gitignored)
```

## 🧪 Testing

```bash
# Run health check
curl http://localhost:7860/health

# Check model status
curl http://localhost:7860/agriculture/model-status

# Test all endpoints
python -m pytest tests/ -v
```

## 🔧 Configuration

Environment variables (`.env`):
```bash
# Weather
OPENWEATHER_API_KEY=your_key
WEATHERAPI_KEY=your_key

# Market
AGMARKNET_API_KEY=your_key
DATA_GOV_IN_API_KEY=your_key

# Satellite
SENTINEL_HUB_CLIENT_ID=your_id
SENTINEL_HUB_CLIENT_SECRET=your_secret

# ML Models
MODEL_DIR=./models
CACHE_TTL=3600

# Database (optional)
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

##  Model Performance

| Model | MAE | RMSE | R² | CV MAE |
|-------|-----|------|-----|--------|
| Yield (Cotton) | ~0.18 | ~0.25 | ~0.82 | ~0.20 |
| Yield (Wheat) | ~0.22 | ~0.30 | ~0.78 | ~0.25 |
| Price (Cotton) | ~180 | ~250 | ~0.85 | - |
| Disease Risk | - | - | Acc: ~0.87 | - |
| Irrigation | - | - | R²: ~0.89 | - |
| Fertilizer | - | - | R²: ~0.91 | - |

##  Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

##  License

MIT License - see LICENSE file for details.

##  Acknowledgments

- **TetraTHON 2026** - Indo-French AI Hackathon
- **ICAR** - Indian Council of Agricultural Research
- **Agmarknet** - Agricultural Marketing Information Network
- **Sentinel Hub** - Copernicus satellite data
- **OpenWeather/WeatherAPI** - Weather data providers

