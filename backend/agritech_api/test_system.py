#!/usr/bin/env python3
"""
Test script to verify AgriTech API services and ML models
"""

import asyncio
import sys
from pathlib import Path

# Configure utf-8 encoding for Windows console output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from agritech_api.clients import (
    get_weather_client, get_mandi_client, 
    get_satellite_client, get_soil_client
)
from agritech_api.ml_models import get_model_manager
from agritech_api.services.agriculture_service import (
    get_crop_data, get_growth_stage, get_real_weather_data,
    get_soil_data, get_satellite_data
)
from agritech_api.schemas import CropType, Location, SoilType, IrrigationSource


async def test_weather_client():
    print("\n=== Testing Weather Client ===")
    client = get_weather_client()
    try:
        forecast = await client.get_forecast(23.0, 72.0, 3)
        print(f"✓ Weather forecast: {len(forecast)} days")
        for day in forecast[:2]:
            print(f"  {day.date}: {day.condition}, {day.temp_max_c:.1f}/{day.temp_min_c:.1f}°C, Rain: {day.rainfall_mm:.1f}mm")
    except Exception as e:
        print(f"✗ Weather client error: {e}")
    finally:
        await client.close()


async def test_mandi_client():
    print("\n=== Testing Mandi Client ===")
    client = get_mandi_client()
    try:
        prices = await client.get_prices(CropType.COTTON, "Gujarat", days=3)
        print(f"✓ Mandi prices: {len(prices)} records")
        for p in prices[:3]:
            print(f"  {p.mandi_name}: ₹{p.modal_price}/q, Arrival: {p.arrival_tonnes}t")
    except Exception as e:
        print(f"✗ Mandi client error: {e}")
    finally:
        await client.close()


async def test_satellite_client():
    print("\n=== Testing Satellite Client ===")
    client = get_satellite_client()
    try:
        from datetime import date, timedelta
        data = await client.get_field_data(
            23.0, 72.0, 2.0, CropType.COTTON, 
            date.today() - timedelta(days=60), 14
        )
        print(f"✓ Satellite data: {len(data)} days")
        for d in data[-3:]:
            print(f"  {d.date}: NDVI={d.ndvi:.3f}, Health={d.crop_health_score:.1f}, SM={d.soil_moisture_percent:.1f}%")
    except Exception as e:
        print(f"✗ Satellite client error: {e}")
    finally:
        await client.close()


async def test_soil_client():
    print("\n=== Testing Soil Client ===")
    client = get_soil_client()
    try:
        soil = await client.get_soil_health(23.0, 72.0)
        print(f"✓ Soil data: pH={soil.ph}, EC={soil.ec_ds_m}, OC={soil.organic_carbon_percent}%")
        print(f"  NPK: N={soil.available_n_kg_ha}, P={soil.available_p_kg_ha}, K={soil.available_k_kg_ha}")
        print(f"  Type: {soil.soil_type.value}, Source: {soil.source}")
    except Exception as e:
        print(f"✗ Soil client error: {e}")
    finally:
        await client.close()


async def test_ml_models():
    print("\n=== Testing ML Models ===")
    manager = get_model_manager()
    status = manager.get_model_status()
    print(f"Model Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")


async def test_agriculture_service():
    print("\n=== Testing Agriculture Service ===")
    location = Location(
        latitude=23.0, longitude=72.0,
        state="Gujarat", district="Ahmedabad", 
        taluka="Daskroi", village="Bavla"
    )
    
    try:
        crop_data = await get_crop_data(CropType.COTTON)
        print(f"✓ Crop data: {crop_data['duration_days']} days, base yield: {crop_data.get('base_yield_tonnes_ha', 'N/A')} t/ha")
        
        stage = await get_growth_stage(CropType.COTTON, 45)
        print(f"✓ Growth stage at 45 DAS: {stage.value}")
        
        weather = await get_real_weather_data(location, 3)
        print(f"✓ Real weather: {len(weather)} days")
        
        soil = await get_soil_data(location)
        print(f"✓ Soil data: pH={soil.get('ph')}, Type={soil.get('soil_type')}")
        
        satellite = await get_satellite_data(location, CropType.COTTON, 2.0, 
                                              date.today() - timedelta(days=60), 7)
        print(f"✓ Satellite: {len(satellite)} days, NDVI={satellite[-1]['ndvi']:.3f}")
        
    except Exception as e:
        print(f"✗ Agriculture service error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    print("=" * 60)
    print("AgriTech API - System Verification Tests")
    print("=" * 60)
    
    await test_weather_client()
    await test_mandi_client()
    await test_satellite_client()
    await test_soil_client()
    await test_ml_models()
    await test_agriculture_service()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    from datetime import date, timedelta
    asyncio.run(main())