from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime


class AlertType(str, Enum):
    PRICE_THRESHOLD = "price_threshold"
    PRICE_DROP = "price_drop"
    PRICE_SPIKE = "price_spike"
    SPOILAGE_RISK = "spoilage_risk"
    WEATHER_ALERT = "weather_alert"
    PEST_OUTBREAK = "pest_outbreak"
    VACCINATION_DUE = "vaccination_due"
    HEAT_STRESS = "heat_stress"
    DISEASE_OUTBREAK = "disease_outbreak"