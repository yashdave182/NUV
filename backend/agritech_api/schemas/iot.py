from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ThingSpeakChannelInfo(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    latitude: Optional[str] = "0.0"
    longitude: Optional[str] = "0.0"
    field1: Optional[str] = "Soil Moisture (SML)"
    field2: Optional[str] = "Temperature"
    field3: Optional[str] = "Humidity"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_entry_id: Optional[int] = None


class ThingSpeakFeedEntry(BaseModel):
    entry_id: int
    created_at: str
    field1: Optional[str] = None  # Soil Moisture (SML)
    field2: Optional[str] = None  # Temperature
    field3: Optional[str] = None  # Humidity


class ParsedTelemetry(BaseModel):
    soil_moisture_sml: Optional[float] = Field(None, description="Soil Moisture level (SML)")
    temperature_c: Optional[float] = Field(None, description="Ambient temperature (°C)")
    humidity_percent: Optional[float] = Field(None, description="Relative humidity (%)")
    timestamp: Optional[str] = Field(None, description="ISO timestamp of telemetry reading")
    status: str = Field("active", description="Reading status: active / fallback")


class ThingSpeakTelemetryResponse(BaseModel):
    success: bool = True
    channel: Optional[ThingSpeakChannelInfo] = None
    feeds: List[ThingSpeakFeedEntry] = []
    latest: ParsedTelemetry
    message: str = "ThingSpeak IoT telemetry retrieved successfully"
