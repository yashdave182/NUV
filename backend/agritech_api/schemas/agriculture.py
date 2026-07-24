from enum import Enum
from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from .common import Language, Location, CropType, SoilType, IrrigationSource, AdvisoryCategory, AdvisoryPriority, ConfidenceLevel


class Season(str, Enum):
    KHARIF = "kharif"
    RABI = "rabi"
    ZAID = "zaid"
    PERENNIAL = "perennial"


class GrowthStage(str, Enum):
    GERMINATION = "germination"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    MATURITY = "maturity"
    HARVEST = "harvest"


class PestSeverity(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"


class FertilizerType(str, Enum):
    UREA = "urea"
    DAP = "dap"
    MOP = "mop"
    SSP = "ssp"
    NPK = "npk"
    ZINC_SULPHATE = "zinc_sulphate"
    FERROUS_SULPHATE = "ferrous_sulphate"
    ORGANIC = "organic"
    BIOFERTILIZER = "biofertilizer"


class CropAdvisoryRequest(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    location: Location
    crop_type: CropType
    variety: Optional[str] = None
    season: Season
    sowing_date: date
    area_hectares: float = Field(..., gt=0, le=1000)
    soil_type: Optional[SoilType] = None
    irrigation_source: Optional[IrrigationSource] = None
    growth_stage: Optional[GrowthStage] = None
    last_fertilizer_application: Optional[Dict[str, Any]] = None
    last_irrigation_date: Optional[date] = None
    weather_forecast: Optional[List[Dict[str, Any]]] = None
    pest_disease_observed: Optional[List[str]] = None
    language: Language = Language.GUJLISH


class AdvisoryItem(BaseModel):
    category: AdvisoryCategory
    priority: AdvisoryPriority
    title: str
    description: str
    confidence: ConfidenceLevel
    action_items: List[str]
    timeline_days: int = Field(..., ge=1, le=30)
    estimated_cost_inr: Optional[float] = None
    materials_needed: List[str] = []
    precautions: List[str] = []


class CropAdvisoryResponse(BaseModel):
    request_id: str
    phone: str
    crop_type: CropType
    growth_stage: GrowthStage
    days_after_sowing: int
    advisories: List[AdvisoryItem]
    weather_based_advice: List[str]
    pest_disease_risk: List[Dict[str, Any]]
    next_scheduled_activities: List[Dict[str, Any]]
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str
    detailed_report_id: Optional[str] = None


class FertilizerRecommendationRequest(BaseModel):
    phone: str = Field(default="9876543210")
    location: Location = Field(default_factory=lambda: Location(state="Gujarat"))
    crop_type: CropType = CropType.COTTON
    variety: Optional[str] = None
    season: Optional[Season] = Season.KHARIF
    sowing_date: Optional[date] = Field(default_factory=date.today)
    area_hectares: float = Field(default=2.5, gt=0, le=1000)
    soil_test_data: Optional[Dict[str, float]] = None
    # Extra convenience fields sent from frontend
    soil_type: Optional[SoilType] = None
    growth_stage: Optional[str] = None
    target_yield_tonnes_per_ha: Optional[float] = Field(None, gt=0, le=20)
    previous_crop: Optional[CropType] = None
    organic_matter_percent: Optional[float] = Field(None, ge=0, le=10)
    ph: Optional[float] = Field(None, ge=4, le=9)
    ec_ds_m: Optional[float] = Field(None, ge=0)
    available_n_kg_per_ha: Optional[float] = None
    available_p_kg_per_ha: Optional[float] = None
    available_k_kg_per_ha: Optional[float] = None
    available_zn_ppm: Optional[float] = None
    available_fe_ppm: Optional[float] = None
    language: Language = Language.GUJLISH


class FertilizerDose(BaseModel):
    fertilizer: str
    dose_kg_per_ha: float
    dose_kg_total: float
    application_stage: str
    application_method: str
    cost_per_kg_inr: Optional[float] = None
    total_cost_inr: Optional[float] = None
    nutrient_supplied: Dict[str, float]


class FertilizerRecommendationResponse(BaseModel):
    request_id: str
    phone: str
    crop_type: CropType
    nutrient_recommendation: Dict[str, float]
    fertilizer_schedule: List[FertilizerDose]
    total_fertilizer_cost_inr: float
    organic_alternatives: List[Dict[str, Any]]
    soil_health_advice: List[str]
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str
    detailed_report_id: Optional[str] = None


class PestDiseaseIdentificationRequest(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    location: Location
    crop_type: CropType
    growth_stage: Optional[GrowthStage] = None
    symptoms: Optional[List[str]] = None
    affected_area_percent: Optional[float] = Field(None, ge=0, le=100)
    symptom_photos: Optional[List[str]] = None
    recent_weather: Optional[List[Dict[str, Any]]] = None
    pesticide_history: Optional[List[Dict[str, Any]]] = None
    variety: Optional[str] = None
    language: Language = Language.GUJLISH


class PestDiseaseMatch(BaseModel):
    pest_disease_name: str
    scientific_name: Optional[str] = None
    category: str = Field(..., pattern="^(pest|disease|nutrient_deficiency|physiological)$")
    match_confidence: ConfidenceLevel
    key_symptoms_matched: List[str]
    severity: PestSeverity
    economic_threshold: Optional[str] = None
    spread_risk: str = Field(..., pattern="^(low|medium|high)$")


class PestDiseaseIdentificationResponse(BaseModel):
    request_id: str
    phone: str
    crop_type: CropType
    matches: List[PestDiseaseMatch]
    most_likely: PestDiseaseMatch
    immediate_actions: List[str]
    recommended_treatments: List[Dict[str, Any]]
    preventive_measures: List[str]
    monitoring_schedule: List[str]
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str
    detailed_report_id: Optional[str] = None


class IrrigationSchedulingRequest(BaseModel):
    phone: str = Field(default="9876543210")
    location: Location = Field(default_factory=lambda: Location(state="Gujarat"))
    crop_type: CropType = CropType.COTTON
    variety: Optional[str] = None
    season: Optional[Season] = Season.KHARIF
    sowing_date: Optional[date] = Field(default_factory=date.today)
    area_hectares: float = Field(default=2.5, gt=0, le=1000)
    soil_type: Optional[SoilType] = SoilType.BLACK_COTTON
    irrigation_source: Optional[IrrigationSource] = IrrigationSource.BOREWELL
    irrigation_method: Optional[str] = Field("drip", pattern="^(flood|drip|sprinkler|furrow)$")
    water_availability: Optional[str] = Field("adequate", pattern="^(adequate|limited|scarce)$")
    last_irrigation_date: Optional[date] = None
    last_irrigation_depth_mm: Optional[float] = None
    weather_forecast: Optional[List[Dict[str, Any]]] = None
    crop_coefficient: Optional[float] = None
    # Extra field from frontend
    growth_stage: Optional[str] = None
    language: Language = Language.GUJLISH


class IrrigationSchedule(BaseModel):
    date: date
    depth_mm: float
    volume_m3: float
    duration_hours: Optional[float] = None
    stage: GrowthStage
    criticality: str = Field(..., pattern="^(critical|optimal|supplementary)$")
    water_saving_tip: Optional[str] = None


class IrrigationSchedulingResponse(BaseModel):
    request_id: str
    phone: str
    crop_type: CropType
    current_stage: GrowthStage
    eto_mm_per_day: float
    etc_mm_per_day: float
    soil_moisture_status: str
    irrigation_schedule: List[IrrigationSchedule]
    total_water_requirement_mm: float
    water_saving_recommendations: List[str]
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str
    detailed_report_id: Optional[str] = None


class CropCalendarRequest(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    location: Location
    crop_type: CropType
    variety: Optional[str] = None
    season: Optional[Season] = Season.KHARIF
    language: Language = Language.GUJLISH


class CalendarActivity(BaseModel):
    week_after_sowing: int
    growth_stage: GrowthStage
    activity: str
    category: AdvisoryCategory
    description: str
    inputs_needed: List[str] = []
    estimated_cost_inr: Optional[float] = None
    weather_dependency: bool = False


class CropCalendarResponse(BaseModel):
    request_id: str
    phone: str
    crop_type: CropType
    season: Optional[Season] = Season.KHARIF
    sowing_window: Dict[str, str]
    harvest_window: Dict[str, str]
    calendar: List[CalendarActivity]
    key_milestones: List[Dict[str, Any]]
    total_estimated_cost_inr: float
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str
    detailed_report_id: Optional[str] = None


class WeatherAdvisoryRequest(BaseModel):
    phone: str = Field(default="9876543210")
    location: Location = Field(default_factory=lambda: Location(state="Gujarat"))
    crop_type: Optional[CropType] = None
    growth_stage: Optional[GrowthStage] = None
    forecast_days: int = Field(7, ge=1, le=14)
    language: Language = Language.GUJLISH


class WeatherForecastDay(BaseModel):
    date: date
    max_temp_c: Optional[float] = Field(None, alias="temp_max_c")
    temp_max_c: Optional[float] = None
    min_temp_c: Optional[float] = Field(None, alias="temp_min_c")
    temp_min_c: Optional[float] = None
    rainfall_mm: float = 0.0
    humidity_percent: float = 50.0
    wind_speed_kmph: float = 10.0
    cloud_cover_percent: float = 0.0
    condition: str = "Sunny"

    @root_validator(pre=True)
    def align_temp_fields(cls, values):
        if isinstance(values, dict):
            if 'temp_max_c' in values and 'max_temp_c' not in values:
                values['max_temp_c'] = values['temp_max_c']
            elif 'max_temp_c' in values and 'temp_max_c' not in values:
                values['temp_max_c'] = values['max_temp_c']
            if 'temp_min_c' in values and 'min_temp_c' not in values:
                values['min_temp_c'] = values['temp_min_c']
            elif 'min_temp_c' in values and 'temp_min_c' not in values:
                values['temp_min_c'] = values['min_temp_c']
        return values


class WeatherAdvisory(BaseModel):
    date: date
    advisory: str
    category: AdvisoryCategory
    priority: AdvisoryPriority
    action_required: bool


class WeatherAdvisoryResponse(BaseModel):
    request_id: str
    phone: str
    location: Location
    forecast: List[WeatherForecastDay]
    advisories: List[WeatherAdvisory]
    overall_risk: str = Field(..., pattern="^(low|medium|high)$")
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str


class SoilHealthCardRequest(BaseModel):
    phone: str = Field(default="9876543210")
    location: Location = Field(default_factory=lambda: Location(state="Gujarat"))
    survey_number: Optional[str] = None
    language: Language = Language.GUJLISH
    # Optional soil parameter overrides from frontend
    soil_type: Optional[SoilType] = None
    soil_parameters: Optional[Dict[str, Any]] = None


class SoilParameter(BaseModel):
    parameter: str
    value: float
    unit: str
    status: str = Field(..., pattern="^(low|medium|high|optimal)$")
    recommendation: str


class SoilHealthCardResponse(BaseModel):
    request_id: str
    phone: str
    location: Location
    survey_number: Optional[str] = None
    parameters: List[SoilParameter]
    soil_type: SoilType
    ph_status: str
    ec_status: str
    oc_status: str
    npk_status: Dict[str, str]
    micronutrient_status: Dict[str, str]
    overall_fertility: str = Field(..., pattern="^(poor|moderate|good|excellent)$")
    crop_suitability: List[Dict[str, Any]]
    amendment_recommendations: List[Dict[str, Any]]
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str
    detailed_report_id: Optional[str] = None


class VarietyRecommendationRequest(BaseModel):
    phone: str = Field(default="9876543210")
    location: Location = Field(default_factory=lambda: Location(state="Gujarat"))
    crop_type: CropType = CropType.COTTON
    season: Optional[Season] = Season.KHARIF
    soil_type: Optional[SoilType] = None
    irrigation_source: Optional[IrrigationSource] = None
    farmer_preference: Optional[str] = Field(None, pattern="^(yield|quality|disease_resistance|early_maturity|market_price)$")
    language: Language = Language.GUJLISH


class VarietyOption(BaseModel):
    variety_name: str
    release_year: int
    duration_days: int
    yield_potential_tonnes_per_ha: float
    special_traits: List[str]
    disease_resistance: List[str]
    pest_resistance: List[str]
    quality_parameters: Dict[str, Any]
    suitable_regions: List[str]
    seed_availability: str = Field(..., pattern="^(easy|moderate|difficult)$")
    seed_cost_inr_per_kg: Optional[float] = None


class VarietyRecommendationResponse(BaseModel):
    request_id: str
    phone: str
    crop_type: CropType
    season: Season
    recommended_varieties: List[VarietyOption]
    comparison_table: List[Dict[str, Any]]
    selection_guide: List[str]
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str
    detailed_report_id: Optional[str] = None


class IntercroppingAdviceRequest(BaseModel):
    phone: str = Field(default="9876543210")
    location: Location = Field(default_factory=lambda: Location(state="Gujarat"))
    main_crop: Optional[CropType] = None
    # Allow crop_type as alias for main_crop (sent by frontend GenericTab)
    crop_type: Optional[CropType] = None
    season: Optional[Season] = Season.KHARIF
    area_hectares: float = Field(default=2.5, gt=0, le=1000)
    irrigation_source: Optional[IrrigationSource] = None
    language: Language = Language.GUJLISH

    @root_validator(pre=True)
    def set_main_crop_from_crop_type(cls, values):
        if not values.get('main_crop') and values.get('crop_type'):
            values['main_crop'] = values['crop_type']
        if not values.get('main_crop'):
            values['main_crop'] = 'cotton'
        return values


class IntercroppingOption(BaseModel):
    intercrop: str
    row_ratio: str
    spatial_arrangement: str
    benefits: List[str]
    additional_yield: Dict[str, float]
    additional_cost_inr: float
    management_complexity: str = Field(..., pattern="^(low|medium|high)$")
    compatibility_score: float = Field(..., ge=0, le=10)


class IntercroppingAdviceResponse(BaseModel):
    request_id: str
    phone: str
    main_crop: CropType
    options: List[IntercroppingOption]
    best_option: IntercroppingOption
    implementation_guide: List[str]
    risk_factors: List[str]
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str
    detailed_report_id: Optional[str] = None


class CropInsuranceRequest(BaseModel):
    phone: str = Field(default="9876543210")
    location: Location = Field(default_factory=lambda: Location(state="Gujarat"))
    crop_type: CropType = CropType.COTTON
    area_hectares: float = Field(default=2.5, gt=0, le=1000)
    season: Optional[Season] = Season.KHARIF
    sum_insured_per_ha: Optional[float] = Field(None, gt=0)
    language: Language = Language.GUJLISH


class InsuranceOption(BaseModel):
    scheme_name: str
    premium_rate_percent: float
    farmer_share_percent: float
    sum_insured_per_ha: float
    coverage: List[str]
    exclusions: List[str]
    claim_process: List[str]
    cut_off_date: date
    implementing_agency: str


class CropInsuranceResponse(BaseModel):
    request_id: str
    phone: str
    crop_type: CropType
    season: Season
    options: List[InsuranceOption]
    recommended_option: InsuranceOption
    premium_estimate_inr: float
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str
    detailed_report_id: Optional[str] = None