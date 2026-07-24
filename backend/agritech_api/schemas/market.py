from enum import Enum
from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from .common import Language, Location, CropType, MandiType, TransportMode, StorageCondition, DecisionAction, PriceTrend, AlertType


class MandiPriceRequest(BaseModel):
    phone: str = Field(default="9876543210")
    location: Location = Field(default_factory=lambda: Location(state="Gujarat"))
    crop_type: CropType = CropType.COTTON
    variety: Optional[str] = None
    radius_km: int = Field(50, ge=5, le=200)
    days: int = Field(7, ge=1, le=30)
    language: Language = Language.GUJLISH


class MandiPriceData(BaseModel):
    mandi_name: str
    mandi_type: MandiType
    district: str
    state: str
    distance_km: float
    date: date
    min_price: float
    max_price: float
    modal_price: float
    arrival_tonnes: Optional[float] = None
    variety: Optional[str] = None
    grade: Optional[str] = None


class MandiPriceResponse(BaseModel):
    request_id: str
    phone: str
    crop_type: CropType
    prices: List[MandiPriceData]
    best_price: MandiPriceData
    average_modal_price: float
    price_trend: PriceTrend
    total_arrivals_tonnes: float
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str


class PriceTrendRequest(BaseModel):
    phone: str = Field(default="9876543210")
    location: Location = Field(default_factory=lambda: Location(state="Gujarat"))
    crop_type: CropType = CropType.COTTON
    mandi_name: Optional[str] = None
    days: int = Field(30, ge=7, le=365)
    language: Language = Language.GUJLISH


class PriceTrendPoint(BaseModel):
    date: date
    modal_price: float
    min_price: float
    max_price: float
    arrival_tonnes: Optional[float] = None


class PriceTrendResponse(BaseModel):
    request_id: str
    phone: str
    crop_type: CropType
    mandi_name: Optional[str] = None
    trend_data: List[PriceTrendPoint]
    trend: PriceTrend
    statistics: Dict[str, float]
    price_volatility: str = Field(..., pattern="^(low|medium|high)$")
    key_observations: List[str]
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str


class SellDecisionRequest(BaseModel):
    phone: str = Field(default="9876543210")
    location: Location = Field(default_factory=lambda: Location(state="Gujarat"))
    crop_type: CropType = CropType.COTTON
    variety: Optional[str] = None
    quantity_kg: float = Field(default=1000, gt=0, le=50000)
    quality_grade: Optional[str] = None
    storage_condition: StorageCondition = StorageCondition.SHED
    days_stored: int = Field(0, ge=0, le=365)
    current_mandi_price: Optional[float] = None
    farmer_price_expectation: Optional[float] = Field(None, gt=0)
    max_transport_distance_km: float = Field(50, ge=0, le=500)
    transport_mode: TransportMode = TransportMode.TRUCK
    transport_cost_per_km: float = Field(15.0, ge=0)
    loading_unloading_cost_per_quintal: float = Field(10.0, ge=0)
    storage_cost_per_quintal_per_day: float = Field(0.5, ge=0)
    spoilage_rate_per_day_percent: float = Field(0.2, ge=0, le=5)
    language: Language = Language.GUJLISH


class SellOption(BaseModel):
    action: DecisionAction
    mandi_name: Optional[str] = None
    mandi_distance_km: Optional[float] = None
    mandi_type: Optional[MandiType] = None
    expected_price_per_quintal: float
    transport_cost: float
    loading_unloading_cost: float
    storage_cost: float
    spoilage_loss_kg: float
    spoilage_loss_value: float
    total_costs: float
    net_realisation_per_quintal: float
    total_net_income: float
    days_to_execute: int
    risk_level: str = Field(..., pattern="^(low|medium|high)$")
    reasoning: str
    break_even_price: float


class SellDecisionResponse(BaseModel):
    request_id: str
    phone: str
    crop_type: CropType
    quantity_kg: float
    current_situation: Dict[str, Any]
    options: List[SellOption]
    recommended_action: SellOption
    price_sensitivity: List[Dict[str, Any]]
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str
    detailed_report_id: Optional[str] = None


class TransportOptimizationRequest(BaseModel):
    phone: str = Field(default="9876543210")
    origin: Location = Field(default_factory=lambda: Location(state="Gujarat"))
    destination: Location = Field(default_factory=lambda: Location(state="Maharashtra"))
    location: Optional[Location] = None  # fallback if frontend sends location
    crop_type: CropType = CropType.COTTON
    quantity_kg: float = Field(default=1000, gt=0, le=50000)
    transport_mode: TransportMode = TransportMode.TRUCK
    urgency: str = Field("normal", pattern="^(urgent|normal|flexible)$")
    language: Language = Language.GUJLISH


class TransportOption(BaseModel):
    transport_mode: TransportMode
    distance_km: float
    estimated_time_hours: float
    cost_per_km: float
    total_transport_cost: float
    loading_unloading_cost: float
    total_cost: float
    cost_per_quintal: float
    capacity_kg: float
    trips_required: int
    reliability: str = Field(..., pattern="^(high|medium|low)$")
    availability: str = Field(..., pattern="^(immediate|within_24h|within_48h)$")


class TransportOptimizationResponse(BaseModel):
    request_id: str
    phone: str
    origin: Location
    destination: Location
    options: List[TransportOption]
    recommended_option: TransportOption
    cost_savings_vs_default: float
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str


class StorageAdvisoryRequest(BaseModel):
    phone: str = Field(default="9876543210")
    location: Location = Field(default_factory=lambda: Location(state="Gujarat"))
    crop_type: CropType = CropType.COTTON
    quantity_kg: float = Field(default=1000, gt=0, le=50000)
    current_storage: StorageCondition = StorageCondition.SHED
    current_moisture_percent: float = Field(default=12.0, ge=5, le=30)
    target_storage_days: int = Field(default=30, ge=1, le=365)
    days_stored: int = Field(default=0, ge=0, le=365)
    current_mandi_price: Optional[float] = None
    language: Language = Language.GUJLISH


class StorageOption(BaseModel):
    storage_condition: StorageCondition
    setup_cost_inr: float
    monthly_cost_inr: float
    spoilage_rate_per_month_percent: float
    max_storage_months: int
    quality_retention: str = Field(..., pattern="^(excellent|good|fair|poor)$")
    pest_control_needed: bool
    ventilation_needed: bool
    total_cost_for_period: float
    expected_recovery_percent: float


class StorageAdvisoryResponse(BaseModel):
    request_id: str
    phone: str
    crop_type: CropType
    current_storage_assessment: Dict[str, Any]
    options: List[StorageOption]
    recommended_storage: StorageOption
    moisture_management: List[str]
    pest_management: List[str]
    monitoring_schedule: List[str]
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str
    detailed_report_id: Optional[str] = None


class SpoilagePredictionRequest(BaseModel):
    phone: str = Field(default="9876543210")
    location: Location = Field(default_factory=lambda: Location(state="Gujarat"))
    crop_type: CropType = CropType.COTTON
    quantity_kg: float = Field(default=1000, gt=0, le=50000)
    storage_condition: StorageCondition = StorageCondition.SHED
    current_moisture_percent: float = Field(default=12.0, ge=5, le=30)
    temperature_celsius: Optional[float] = Field(None, ge=0, le=50)
    humidity_percent: Optional[float] = Field(None, ge=0, le=100)
    days_stored: int = Field(0, ge=0, le=365)
    language: Language = Language.GUJLISH


class SpoilagePredictionPoint(BaseModel):
    day: int
    remaining_quality_percent: float
    spoilage_loss_kg: float
    marketable_kg: float
    value_loss_inr: float
    risk_level: str = Field(..., pattern="^(low|medium|high|critical)$")


class SpoilagePredictionResponse(BaseModel):
    request_id: str
    phone: str
    crop_type: CropType
    initial_quality: str
    predictions: List[SpoilagePredictionPoint]
    critical_threshold_day: int
    recommended_action_day: int
    total_value_at_risk: float
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str
    detailed_report_id: Optional[str] = None


class PriceAlertSetupRequest(BaseModel):
    phone: str = Field(default="9876543210")
    location: Location = Field(default_factory=lambda: Location(state="Gujarat"))
    crop_type: CropType = CropType.COTTON
    mandi_name: Optional[str] = None
    alert_type: Optional[Any] = AlertType.PRICE_THRESHOLD
    threshold_price: float = Field(default=5000, gt=0)
    threshold_direction: str = Field("above")
    notification_channel: str = Field("sms")
    frequency: str = Field("instant")
    language: Language = Language.GUJLISH

    @root_validator(pre=True)
    def handle_alert_type_string(cls, values):
        if isinstance(values, dict):
            at = values.get('alert_type')
            if at in ['above', 'below']:
                values['threshold_direction'] = at
                values['alert_type'] = AlertType.PRICE_THRESHOLD
        return values


class PriceAlertSetupResponse(BaseModel):
    request_id: str
    phone: str
    alert_id: str
    status: str = Field("active", pattern="^(active|paused|completed)$")
    crop_type: CropType
    mandi_name: Optional[str] = None
    alert_type: AlertType
    threshold_price: float
    threshold_direction: str
    current_price: float
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str


class PriceAlertTriggerRequest(BaseModel):
    phone: str = Field(default="9876543210")
    alert_id: str = "ALT-001"
    current_price: float = Field(default=5000)
    language: Language = Language.GUJLISH


class PriceAlertTriggerResponse(BaseModel):
    request_id: str
    phone: str
    alert_id: str
    triggered: bool
    current_price: float
    threshold_price: float
    message: str
    recommended_action: str
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str


class MarketIntelligenceRequest(BaseModel):
    phone: str = Field(default="9876543210")
    location: Location = Field(default_factory=lambda: Location(state="Gujarat"))
    crop_type: CropType = CropType.COTTON
    horizon_days: int = Field(14, ge=1, le=60)
    language: Language = Language.GUJLISH


class MarketIntelligenceResponse(BaseModel):
    request_id: str
    phone: str
    crop_type: CropType
    current_market_summary: Dict[str, Any]
    price_forecast: List[Dict[str, Any]]
    arrivals_forecast: List[Dict[str, Any]]
    demand_supply_analysis: Dict[str, Any]
    trading_recommendations: List[str]
    risk_factors: List[str]
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str
    detailed_report_id: Optional[str] = None


class MandiListRequest(BaseModel):
    phone: str = Field(default="9876543210")
    location: Location = Field(default_factory=lambda: Location(state="Gujarat"))
    radius_km: int = Field(50, ge=5, le=200)
    crop_type: Optional[CropType] = None
    mandi_type: Optional[MandiType] = None
    language: Language = Language.GUJLISH


class MandiInfo(BaseModel):
    mandi_name: str
    mandi_type: MandiType
    district: str
    state: str
    distance_km: float
    contact_number: Optional[str] = None
    email: Optional[str] = None
    operating_hours: Optional[str] = None
    facilities: List[str] = []
    crops_traded: List[CropType] = []
    e_nam_enabled: bool = False


class MandiListResponse(BaseModel):
    request_id: str
    phone: str
    location: Location
    mandis: List[MandiInfo]
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str