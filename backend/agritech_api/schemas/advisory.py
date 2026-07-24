from enum import Enum
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime, timedelta
from .common import (
    Language, Location, CropType, SoilType, IrrigationSource,
    WeatherCondition, AdvisoryCategory, AdvisoryPriority, ConfidenceLevel,
    BaseRequest, BaseResponse
)


class GrowthStage(str, Enum):
    GERMINATION = "germination"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    MATURITY = "maturity"
    HARVEST = "harvest"


class FarmInputRequest(BaseModel):
    phone: Optional[str] = "9876543210"
    location: Location
    crop_type: CropType
    variety: Optional[str] = None
    season: Optional[str] = None
    sowing_date: Optional[date] = None
    area_hectares: float = Field(2.5, gt=0, le=100)
    soil_type: Optional[SoilType] = None
    irrigation_source: Optional[IrrigationSource] = None
    previous_crop: Optional[CropType] = None
    weather_observation: Optional[str] = None
    current_weather: Optional[WeatherCondition] = None
    weather_forecast: Optional[List[Any]] = None
    temperature_celsius: Optional[float] = Field(None, ge=-10, le=55)
    humidity_percent: Optional[float] = Field(None, ge=0, le=100)
    rainfall_mm: Optional[float] = Field(None, ge=0, le=500)
    wind_speed_kmph: Optional[float] = Field(None, ge=0, le=200)
    leaf_photo_base64: Optional[str] = None
    pest_disease_observed: Optional[List[str]] = None
    language: Optional[Language] = Language.ENGLISH

    @validator('sowing_date', pre=True, always=True)
    def validate_sowing_date(cls, v):
        if not v:
            return date.today() - timedelta(days=45)
        if isinstance(v, str):
            try:
                v = date.fromisoformat(v)
            except Exception:
                return date.today() - timedelta(days=45)
        if isinstance(v, date) and v > date.today():
            return date.today()
        return v

    @validator('phone', pre=True, always=True)
    def validate_phone(cls, v):
        if not v or not isinstance(v, str) or len(str(v).strip()) == 0:
            return "9876543210"
        return str(v).strip()


class AdvisoryItem(BaseModel):
    category: AdvisoryCategory
    priority: AdvisoryPriority
    title: str
    description: str
    rationale: str
    confidence: ConfidenceLevel
    action_items: List[str]
    timeline_days: int = Field(..., ge=1, le=30)
    dosage_info: Optional[str] = None
    cost_estimate_inr: Optional[float] = Field(None, ge=0)
    weather_dependent: bool = False
    pest_disease_name: Optional[str] = None
    threshold_reached: Optional[bool] = None


class FarmAdvisoryResponse(BaseResponse):
    request_id: str
    phone: str
    crop_type: CropType
    growth_stage: GrowthStage
    days_after_sowing: int
    advisories: List[AdvisoryItem]
    weather_forecast: List[Dict[str, Any]] = []
    soil_moisture_status: Optional[str] = None
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str
    detailed_report_id: Optional[str] = None


class IrrigationAdvisory(AdvisoryItem):
    category: AdvisoryCategory = AdvisoryCategory.IRRIGATION
    irrigation_method: Optional[str] = None
    water_amount_mm: Optional[float] = None
    frequency_days: Optional[int] = None
    critical_stage: bool = False


class FertilizerAdvisory(AdvisoryItem):
    category: AdvisoryCategory = AdvisoryCategory.FERTILIZER
    fertilizer_name: Optional[str] = None
    npk_ratio: Optional[str] = None
    dosage_per_hectare: Optional[str] = None
    application_method: Optional[str] = None
    split_application: bool = False


class PestDiseaseAdvisory(AdvisoryItem):
    category: AdvisoryCategory = AdvisoryCategory.PEST_DISEASE
    pest_disease_name: str
    severity: str = Field(..., pattern="^(low|moderate|high|severe)$")
    affected_area_percent: Optional[float] = Field(None, ge=0, le=100)
    identification_tips: List[str] = []
    preventive_measures: List[str] = []
    chemical_control: Optional[List[str]] = None
    organic_control: Optional[List[str]] = None
    pre_harvest_interval_days: Optional[int] = None


class WeatherForecastItem(BaseModel):
    date: date
    condition: WeatherCondition
    temp_min_c: float
    temp_max_c: float
    humidity_percent: int
    rainfall_mm: float
    wind_speed_kmph: float
    advisory_note: Optional[str] = None


class DiseaseDetectionRequest(BaseModel):
    phone: str = Field(default="9876543210")
    crop_type: CropType = CropType.COTTON
    image_base64: str
    location: Location = Field(default_factory=lambda: Location(state="Gujarat"))
    language: Language = Language.GUJLISH


class DiseaseDetectionResult(BaseModel):
    disease_name: str
    scientific_name: Optional[str] = None
    confidence: float = Field(..., ge=0, le=1)
    severity: str = Field(..., pattern="^(mild|moderate|severe)$")
    affected_area_percent: Optional[float] = Field(None, ge=0, le=100)
    symptoms: List[str] = []
    treatment_recommendations: List[str] = []
    preventive_measures: List[str] = []


class DiseaseDetectionResponse(BaseResponse):
    request_id: str
    phone: str
    crop_type: CropType
    detections: List[DiseaseDetectionResult]
    overall_risk: str = Field(..., pattern="^(low|medium|high)$")
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str


class CropCalendarRequest(BaseModel):
    phone: str = Field(default="9876543210")
    location: Location = Field(default_factory=lambda: Location(state="Gujarat"))
    crop_type: CropType = CropType.COTTON
    language: Language = Language.GUJLISH


class CropCalendarEvent(BaseModel):
    stage: GrowthStage
    start_day: int
    end_day: int
    key_activities: List[str]
    critical_operations: List[str]
    weather_watch: List[str]
    pest_disease_risk: List[str]


class CropCalendarResponse(BaseResponse):
    request_id: str
    phone: str
    crop_type: CropType
    calendar: List[CropCalendarEvent]
    total_duration_days: int
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str


class SoilHealthCardRequest(BaseModel):
    phone: str = Field(default="9876543210")
    location: Location = Field(default_factory=lambda: Location(state="Gujarat"))
    survey_number: Optional[str] = None
    language: Language = Language.GUJLISH


class SoilParameter(BaseModel):
    parameter: str
    value: float
    unit: str
    status: str = Field(..., pattern="^(low|medium|high|optimal|deficient)$")
    recommendation: str


class SoilHealthCardResponse(BaseResponse):
    request_id: str
    phone: str
    location: Location
    parameters: List[SoilParameter]
    ph: Optional[float] = None
    ec_ds_m: Optional[float] = None
    organic_carbon_percent: Optional[float] = None
    nitrogen_kg_ha: Optional[float] = None
    phosphorus_kg_ha: Optional[float] = None
    potassium_kg_ha: Optional[float] = None
    sulphur_ppm: Optional[float] = None
    zinc_ppm: Optional[float] = None
    boron_ppm: Optional[float] = None
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str