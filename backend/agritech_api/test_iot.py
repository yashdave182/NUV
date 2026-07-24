#!/usr/bin/env python3
"""
Test script for ThingSpeak IoT Telemetry Integration
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
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


from agritech_api.clients import get_thingspeak_client
from fastapi.testclient import TestClient
from agritech_api.main import app


async def test_thingspeak_client():
    print("\n=== Testing ThingSpeak Client ===")
    client = get_thingspeak_client()
    try:
        telemetry = await client.get_telemetry(results=5)
        print(f"✓ Success: {telemetry.success}")
        print(f"✓ Channel Name: {telemetry.channel.name} (ID: {telemetry.channel.id})")
        print(f"✓ Feeds returned: {len(telemetry.feeds)}")
        print(f"✓ Latest reading status: {telemetry.latest.status}")
        print(f"  - Soil Moisture (SML): {telemetry.latest.soil_moisture_sml}%")
        print(f"  - Temperature: {telemetry.latest.temperature_c}°C")
        print(f"  - Humidity: {telemetry.latest.humidity_percent}%")
        print(f"  - Timestamp: {telemetry.latest.timestamp}")
        assert telemetry.latest.soil_moisture_sml is not None
        assert telemetry.latest.temperature_c is not None
        assert telemetry.latest.humidity_percent is not None
        print("✓ Client unit test PASSED!")
    except Exception as e:
        print(f"✗ ThingSpeak client error: {e}")
        raise e


def test_fastapi_endpoints():
    print("\n=== Testing FastAPI IoT Endpoints ===")
    test_client = TestClient(app)

    # Test /iot/thingspeak/telemetry
    res_telemetry = test_client.get("/iot/thingspeak/telemetry?results=3")
    print(f"GET /iot/thingspeak/telemetry status: {res_telemetry.status_code}")
    assert res_telemetry.status_code == 200
    data_telemetry = res_telemetry.json()
    assert data_telemetry["success"] is True
    assert "channel" in data_telemetry
    assert "latest" in data_telemetry

    print("✓ GET /iot/thingspeak/telemetry returned valid JSON response")

    # Test /iot/thingspeak/latest
    res_latest = test_client.get("/iot/thingspeak/latest")
    print(f"GET /iot/thingspeak/latest status: {res_latest.status_code}")
    assert res_latest.status_code == 200
    data_latest = res_latest.json()
    assert "status" in data_latest
    print(f"✓ GET /iot/thingspeak/latest returned: SML={data_latest.get('soil_moisture_sml')}, Temp={data_latest.get('temperature_c')}, Hum={data_latest.get('humidity_percent')}")
    print("✓ FastAPI endpoints test PASSED!")


if __name__ == "__main__":
    asyncio.run(test_thingspeak_client())
    test_fastapi_endpoints()
    print("\n🎉 ALL THINGSPEAK IOT TESTS PASSED SUCCESSFULLY!")
