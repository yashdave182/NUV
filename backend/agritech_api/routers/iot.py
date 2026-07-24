from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from agritech_api.schemas.iot import ThingSpeakTelemetryResponse, ParsedTelemetry
from agritech_api.clients.thingspeak_client import get_thingspeak_client

router = APIRouter(prefix="/iot", tags=["IoT Telemetry"])


@router.get(
    "/thingspeak/telemetry",
    response_model=ThingSpeakTelemetryResponse,
    summary="Get ThingSpeak IoT Channel Feeds & Telemetry",
    description="Fetch live channel metadata and feed records from ThingSpeak channel #3430931."
)
async def get_thingspeak_telemetry(results: int = Query(5, ge=1, le=100, description="Number of results to retrieve")):
    try:
        client = get_thingspeak_client()
        telemetry = await client.get_telemetry(results=results)
        return telemetry
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching IoT telemetry: {str(e)}")


@router.get(
    "/thingspeak/latest",
    response_model=ParsedTelemetry,
    summary="Get Latest Sensor Reading",
    description="Fetch the single latest parsed reading (Soil Moisture SML, Temperature, Humidity)."
)
async def get_thingspeak_latest():
    try:
        client = get_thingspeak_client()
        telemetry = await client.get_telemetry(results=1)
        return telemetry.latest
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching latest reading: {str(e)}")
