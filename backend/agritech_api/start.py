#!/usr/bin/env python3
"""
AgriTech API Startup Script
Runs the FastAPI server with proper configuration
"""

import os
import sys
import asyncio
from pathlib import Path

# Add backend root and agritech_api package to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir.parent))
sys.path.insert(0, str(backend_dir))

import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv(backend_dir / ".env")


def run_server():
    """Run the AgriTech API server"""
    port = int(os.environ.get("PORT", 7860))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"Starting AgriTech API on {host}:{port}")
    print(f"Environment: {os.environ.get('APP_ENV', 'development')}")
    print(f"Model directory: {os.environ.get('MODEL_DIR', './models')}")
    print(f"Docs available at: http://{host}:{port}/docs")
    print("-" * 60)
    
    uvicorn.run(
        "agritech_api.main:app",
        host=host,
        port=port,
        reload=os.environ.get("APP_ENV") == "development",
        log_level=os.environ.get("LOG_LEVEL", "info").lower(),
        access_log=True,
    )


def train_models():
    """Train all ML models"""
    from ml_models.training.train_models import main as train_main
    asyncio.run(train_main())


def check_services():
    """Check all external service connections"""
    import httpx
    
    async def check_all():
        checks = []
        
        # Weather APIs
        openweather_key = os.environ.get("OPENWEATHER_API_KEY")
        if openweather_key:
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.get(
                        "https://api.openweathermap.org/data/2.5/weather",
                        params={"lat": 23.0, "lon": 72.0, "appid": openweather_key}
                    )
                    checks.append(("OpenWeather", "OK" if resp.status_code == 200 else f"Error {resp.status_code}"))
            except Exception as e:
                checks.append(("OpenWeather", f"Error: {e}"))
        else:
            checks.append(("OpenWeather", "No API key"))
        
        # Agmarknet
        agmarknet_key = os.environ.get("AGMARKNET_API_KEY")
        if agmarknet_key:
            checks.append(("Agmarknet", "Key configured"))
        else:
            checks.append(("Agmarknet", "No API key"))
        
        # Sentinel Hub
        sh_id = os.environ.get("SENTINEL_HUB_CLIENT_ID")
        sh_secret = os.environ.get("SENTINEL_HUB_CLIENT_SECRET")
        if sh_id and sh_secret:
            checks.append(("Sentinel Hub", "Keys configured"))
        else:
            checks.append(("Sentinel Hub", "No credentials"))
        
        print("Service Health Checks:")
        print("-" * 40)
        for name, status in checks:
            print(f"  {name}: {status}")
    
    asyncio.run(check_all())


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AgriTech API Management")
    parser.add_argument("command", choices=["run", "train", "check"], 
                       help="Command to execute")
    args = parser.parse_args()
    
    if args.command == "run":
        run_server()
    elif args.command == "train":
        train_models()
    elif args.command == "check":
        check_services()