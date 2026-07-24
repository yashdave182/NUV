from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
from contextlib import asynccontextmanager

from agritech_api.routers import agriculture, market, health, schemes, livestock, iot, auth
from agritech_api.schemas.common import Language
from agritech_api.clients import get_weather_client, get_mandi_client, get_satellite_client, get_soil_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AgriTech API server...")
    logger.info("Loaded routers: agriculture, market, health, schemes, livestock, iot, auth")
    yield
    logger.info("Shutting down AgriTech API server...")
    # Close HTTP clients
    try:
        weather_client = get_weather_client()
        await weather_client.close()
        mandi_client = get_mandi_client()
        await mandi_client.close()
        satellite_client = get_satellite_client()
        await satellite_client.close()
        soil_client = get_soil_client()
        await soil_client.close()
    except Exception as e:
        logger.warning(f"Error closing clients: {e}")


app = FastAPI(
    title="AgriTech API",
    description="Precision Crop Advisory System & Post-Harvest Loss Reduction Planner for Smallholder Farmers",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


app.include_router(auth.router)
app.include_router(agriculture.router)
app.include_router(market.router)
app.include_router(health.router)
app.include_router(schemes.router)
app.include_router(livestock.router)
app.include_router(iot.router)


@app.get("/")
async def root():
    return {
        "name": "AgriTech API",
        "version": "1.0.0",
        "description": "Precision Crop Advisory System & Post-Harvest Loss Reduction Planner",
        "hackathon": "TetraTHON 2026 - Indo-French AI Hackathon",
        "team": "AgriTech AT",
        "endpoints": {
            "agriculture": "/agriculture",
            "market": "/market",
            "health": "/health",
            "schemes": "/schemes",
            "livestock": "/livestock",
            "iot": "/iot",
        },

        "features": [
            "Multi-input crop advisory (location, crop, sowing date, weather, leaf photo)",
            "3 ranked advisories: irrigation, fertiliser, pest/disease with confidence",
            "Post-harvest sell/store/transport decision engine",
            "Mandi price feeds with spoilage curves & transport cost models",
            "SMS/WhatsApp price threshold alert simulation",
            "Health advisory with emergency triage",
            "Government scheme discovery & eligibility checker",
            "Livestock management: vaccination, deworming, feed, breeding, milk quality",
            "19 Indian language support (native scripts + Romanized)",
        ],
        "supported_crops": [
            "cotton", "groundnut", "wheat", "bajra", "maize",
            "cumin", "castor", "sesame", "tobacco", "green_gram",
            "black_gram", "pigeon_pea", "chilli", "onion", "potato",
            "banana", "papaya", "mango",
        ],
        "supported_states": ["Gujarat", "Maharashtra", "Rajasthan", "Madhya Pradesh", "Uttar Pradesh"],
        "languages": [lang.value for lang in Language],
        "docs": "/docs",
        "health_check": "/health",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AgriTech API",
        "version": "1.0.0",
        "timestamp": "2026-07-16T00:00:00Z",
    }


@app.get("/api/v1/info")
async def api_info():
    return {
        "api_version": "v1",
        "base_url": "/api/v1",
        "modules": {
            "agriculture": {
                "prefix": "/agriculture",
                "endpoints": [
                    "POST /advisory - Comprehensive farm advisory",
                    "POST /irrigation - Irrigation scheduling",
                    "POST /fertilizer - Fertilizer recommendation",
                    "POST /pest-disease - Pest/disease identification",
                    "POST /calendar - Crop calendar",
                    "POST /soil-health - Soil health card",
                    "POST /variety-recommendation - Variety recommendation",
                    "POST /intercropping - Intercropping advice",
                    "POST /crop-insurance - Crop insurance info",
                    "POST /weather-advisory - Weather-based advisory",
                ],
            },
            "market": {
                "prefix": "/market",
                "endpoints": [
                    "POST /mandi-prices - Current mandi prices",
                    "POST /price-trend - Price trend analysis",
                    "POST /sell-decision - Sell/store/transport decision",
                    "POST /transport-optimize - Transport cost optimization",
                    "POST /storage-advisory - Storage advisory",
                    "POST /spoilage-prediction - Spoilage prediction",
                    "POST /price-alert - Price alert setup",
                    "POST /price-alert/check - Check price alert",
                    "POST /market-intelligence - Market intelligence report",
                    "POST /mandi-list - Nearby mandi list",
                ],
            },
            "health": {
                "prefix": "/health",
                "endpoints": [
                    "POST /advisory - Health advisory with triage",
                    "POST /vaccination-schedule - Child vaccination schedule",
                    "POST /health-camps - Nearby health camps",
                    "POST /emergency-triage - Emergency triage",
                ],
            },
            "schemes": {
                "prefix": "/schemes",
                "endpoints": [
                    "POST /search - Search government schemes",
                    "POST /detail - Scheme details with application process",
                    "POST /track - Track application status",
                    "POST /eligibility - Check eligibility",
                ],
            },
            "livestock": {
                "prefix": "/livestock",
                "endpoints": [
                    "POST /profile - Animal profile & health assessment",
                    "POST /vaccination-schedule - Vaccination schedule",
                    "POST /health-diagnosis - Symptom-based diagnosis",
                    "POST /deworming - Deworming schedule",
                    "POST /feed-formulation - Least-cost feed formulation",
                    "POST /breeding-advice - Breeding & AI advice",
                    "POST /milk-quality - Milk quality assessment",
                    "POST /disease-alerts - Disease outbreak alerts",
                    "POST /schemes - Livestock government schemes",
                ],
            },
        },
        "input_format": "JSON",
        "output_format": "JSON with SMS summary (<=155 chars)",
        "authentication": "Phone number based (Indian format: 10 digits starting with 6-9)",
        "rate_limit": "100 requests/minute per phone number",
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)