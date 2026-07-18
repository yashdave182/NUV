from enum import Enum
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from .common import Language, Location


class CropType(str, Enum):
    COTTON = "cotton"
    GROUNDNUT = "groundnut"
    WHEAT = "wheat"
    BAJRA = "bajra"
    MAIZE = "maize"
    CUMIN = "cumin"
    CASTOR = "castor"
    SESAME = "sesame"


class CropStage(str, Enum):
    GERMINATION = "germination"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    MATURITY = "maturity"
    HARVEST = "harvest"


class WeatherObservation(BaseModel):
    temperature_max: Optional[float] = Field(None, ge=-10, le=55)
    temperature_min: Optional[float] = Field(None, ge=-10, le=55)
    humidity: Optional[float] = Field(None, ge=0, le=100)
    rainfall_mm: Optional[float] = Field(None, ge=0)
    wind_speed_kmph: Optional[float] = Field(None, ge=0)
    cloud_cover: Optional[str] = None
    observation_date: date = Field(default_factory=date.today)


class LeafImageInput(BaseModel):
    image_base64: str
    content_type: str = "image/jpeg"
    crop_type: CropType


class AdvisoryItem(BaseModel):
    category: str = Field(..., description="irrigation, fertiliser, pest_alert")
    title: str
    description: str
    confidence: str = Field(..., pattern="^(High|Medium|Low)$")
    rationale: str
    action_items: List[str]
    timeline_days: int = Field(..., ge=1, le=7)
    priority: int = Field(..., ge=1, le=3)


class CropAdvisoryRequest(BaseModel):
    farmer_phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    location: Location
    crop_type: CropType
    sowing_date: date
    crop_stage: Optional[CropStage] = None
    weather_observation: Optional[WeatherObservation] = None
    leaf_image: Optional[LeafImageInput] = None
    language: Language = Language.GUJLISH
    farm_size_hectares: Optional[float] = Field(None, gt=0, le=10)


class CropAdvisoryResponse(BaseModel):
    request_id: str
    farmer_phone: str
    crop_type: CropType
    advisories: List[AdvisoryItem]
    weather_summary: Dict[str, Any]
    disease_detection: Optional[Dict[str, Any]] = None
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str
    detailed_report_id: Optional[str] = None

    @validator('sms_summary')
    def validate_sms_length(cls, v):
        if len(v) > 155:
            raise ValueError('SMS summary must be <= 155 characters')
        return v


class PostHarvestRequest(BaseModel):
    farmer_phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    location: Location
    crop_type: CropType
    quantity_quintals: float = Field(..., gt=0, le=1000)
    storage_condition: str = Field(..., pattern="^(open|covered|cold_storage|warehouse)$")
    storage_days: int = Field(..., ge=0, le=180)
    expected_selling_date: Optional[date] = None
    language: Language = Language.GUJLISH


class DecisionOption(BaseModel):
    action: str = Field(..., pattern="^(sell_now|store|transport_to_mandi)$")
    mandi_name: Optional[str] = None
    expected_price_per_quintal: float
    transport_cost: float
    spoilage_loss_percent: float
    net_return: float
    confidence: str = Field(..., pattern="^(High|Medium|Low)$")
    rationale: str


class PostHarvestResponse(BaseModel):
    request_id: str
    farmer_phone: str
    crop_type: CropType
    current_mandi_prices: List[Dict[str, Any]]
    spoilage_curve: List[Dict[str, Any]]
    recommendations: List[DecisionOption]
    best_option: DecisionOption
    price_alert_threshold: Optional[float] = None
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str
    detailed_report_id: Optional[str] = None


class PriceAlertRequest(BaseModel):
    farmer_phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    crop_type: CropType
    mandi_name: str
    threshold_price: float = Field(..., gt=0)
    language: Language = Language.GUJLISH


class PriceAlertResponse(BaseModel):
    alert_id: str
    farmer_phone: str
    crop_type: CropType
    mandi_name: str
    threshold_price: float
    current_price: float
    is_triggered: bool
    message: str
    language: Language