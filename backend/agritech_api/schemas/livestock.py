from enum import Enum
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from .common import (
    Language, Location, AnimalType, BreedType, HealthStatus,
    VaccinationStatus, LactationStage, HousingType, BaseRequest, BaseResponse
)


class LivestockProfileRequest(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    location: Location
    animal_type: AnimalType
    breed: Optional[BreedType] = None
    tag_number: Optional[str] = None
    age_months: int = Field(..., ge=0, le=300)
    weight_kg: Optional[float] = Field(None, ge=0, le=1000)
    body_condition_score: Optional[float] = Field(None, ge=1, le=5)
    lactation_stage: Optional[LactationStage] = None
    last_calving_date: Optional[date] = None
    pregnancy_status: Optional[bool] = None
    pregnancy_month: Optional[int] = Field(None, ge=1, le=9)
    vaccination_status: VaccinationStatus = VaccinationStatus.UNKNOWN
    deworming_date: Optional[date] = None
    housing_type: Optional[HousingType] = None
    feed_type: Optional[str] = None
    milk_yield_litres: Optional[float] = Field(None, ge=0, le=50)
    fat_percent: Optional[float] = Field(None, ge=0, le=10)
    snf_percent: Optional[float] = Field(None, ge=0, le=12)
    language: Language = Language.GUJLISH


class LivestockProfileResponse(BaseResponse):
    request_id: str
    phone: str
    animal_type: AnimalType
    profile_summary: Dict[str, Any]
    health_assessment: str
    recommendations: List[str]
    upcoming_vaccinations: List[Dict[str, Any]]
    upcoming_deworming: Optional[Dict[str, Any]] = None
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str


class VaccinationScheduleRequest(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    location: Location
    animal_type: AnimalType
    breed: Optional[BreedType] = None
    age_months: int = Field(..., ge=0, le=300)
    last_vaccination_date: Optional[date] = None
    last_vaccine_name: Optional[str] = None
    pregnancy_status: Optional[bool] = None
    pregnancy_month: Optional[int] = Field(None, ge=1, le=9)
    language: Language = Language.GUJLISH


class VaccineDose(BaseModel):
    vaccine_name: str
    disease_prevented: str
    dose_number: int
    recommended_age_months: int
    recommended_date: Optional[date] = None
    status: str = Field("pending", pattern="^(due|completed|overdue|skipped|pending)$")
    route: str
    dose_ml: Optional[str] = None
    booster_interval_months: Optional[int] = None
    notes: Optional[str] = None
    government_scheme: Optional[str] = None


class VaccinationScheduleResponse(BaseResponse):
    request_id: str
    phone: str
    animal_type: AnimalType
    schedule: List[VaccineDose]
    completed_count: int
    due_count: int
    overdue_count: int
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str


class HealthDiagnosisRequest(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    location: Location
    animal_type: AnimalType
    breed: Optional[BreedType] = None
    age_months: int = Field(..., ge=0, le=300)
    symptoms: List[str] = Field(..., min_items=1)
    symptom_duration_days: int = Field(..., ge=1, le=365)
    temperature_celsius: Optional[float] = Field(None, ge=35, le=45)
    appetite: Optional[str] = Field(None, pattern="^(normal|reduced|absent)$")
    milk_yield_change: Optional[str] = Field(None, pattern="^(normal|decreased|stopped)$")
    faeces_consistency: Optional[str] = Field(None, pattern="^(normal|loose|hard|bloody)$")
    respiration: Optional[str] = Field(None, pattern="^(normal|rapid|laboured)$")
    behaviour: Optional[str] = Field(None, pattern="^(normal|dull|restless|aggressive)$")
    skin_lesions: Optional[str] = None
    discharge: Optional[str] = None
    lameness: Optional[bool] = None
    recent_vaccination: Optional[bool] = None
    recent_deworming: Optional[bool] = None
    herd_size: Optional[int] = Field(None, ge=1, le=500)
    similar_cases_in_herd: Optional[int] = Field(None, ge=0, le=500)
    language: Language = Language.GUJLISH


class DifferentialDiagnosis(BaseModel):
    disease_name: str
    probability: float = Field(..., ge=0, le=1)
    matching_symptoms: List[str]
    key_differentiating_features: List[str]
    urgency: str = Field(..., pattern="^(low|medium|high|emergency)$")


class HealthDiagnosisResponse(BaseResponse):
    request_id: str
    phone: str
    animal_type: AnimalType
    differential_diagnoses: List[DifferentialDiagnosis]
    most_likely: DifferentialDiagnosis
    immediate_actions: List[str]
    recommended_tests: List[str]
    treatment_suggestions: List[str]
    withdrawal_periods: Dict[str, int]
    preventive_measures: List[str]
    requires_vet_visit: bool
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str


class DewormingScheduleRequest(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    location: Location
    animal_type: AnimalType
    age_months: int = Field(..., ge=0, le=300)
    weight_kg: Optional[float] = Field(None, ge=0, le=1000)
    last_deworming_date: Optional[date] = None
    last_dewormer_name: Optional[str] = None
    lactation_stage: Optional[LactationStage] = None
    pregnancy_month: Optional[int] = Field(None, ge=1, le=9)
    faecal_egg_count: Optional[int] = Field(None, ge=0)
    language: Language = Language.GUJLISH


class DewormerOption(BaseModel):
    dewormer_name: str
    active_ingredient: str
    dose_per_kg: str
    route: str
    withdrawal_milk_days: int
    withdrawal_meat_days: int
    safe_in_pregnancy: bool
    safe_in_lactation: bool
    target_parasites: List[str]
    cost_per_dose_inr: Optional[float] = None


class DewormingScheduleResponse(BaseResponse):
    request_id: str
    phone: str
    animal_type: AnimalType
    recommended_dewormers: List[DewormerOption]
    schedule: List[Dict[str, Any]]
    faecal_egg_count_interpretation: Optional[str] = None
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str


class FeedFormulationRequest(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    location: Location
    animal_type: AnimalType
    breed: Optional[BreedType] = None
    age_months: int = Field(..., ge=0, le=300)
    weight_kg: float = Field(..., ge=0, le=1000)
    lactation_stage: Optional[LactationStage] = None
    milk_yield_litres: Optional[float] = Field(None, ge=0, le=50)
    fat_percent: Optional[float] = Field(None, ge=0, le=10)
    pregnancy_month: Optional[int] = Field(None, ge=1, le=9)
    available_ingredients: List[str] = Field(default_factory=list)
    budget_per_kg_inr: Optional[float] = Field(None, ge=0)
    language: Language = Language.GUJLISH


class FeedIngredient(BaseModel):
    ingredient: str
    quantity_kg_per_day: float
    cost_per_kg_inr: float
    dry_matter_percent: float
    crude_protein_percent: float
    tdn_percent: float
    calcium_percent: Optional[float] = None
    phosphorus_percent: Optional[float] = None


class FeedFormulation(BaseModel):
    ingredients: List[FeedIngredient]
    total_dry_matter_kg: float
    total_crude_protein_kg: float
    total_tdn_kg: float
    total_cost_per_day_inr: float
    cost_per_litre_milk_inr: Optional[float] = None
    meets_requirements: bool
    deficiencies: List[str] = []


class FeedFormulationResponse(BaseResponse):
    request_id: str
    phone: str
    animal_type: AnimalType
    nutritional_requirements: Dict[str, float]
    formulations: List[FeedFormulation]
    recommended_formulation: FeedFormulation
    locally_available_substitutes: Dict[str, List[str]]
    feeding_schedule: List[str]
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str


class BreedingAdviceRequest(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    location: Location
    animal_type: AnimalType
    breed: Optional[BreedType] = None
    age_months: int = Field(..., ge=0, le=300)
    weight_kg: float = Field(..., ge=0, le=1000)
    body_condition_score: Optional[float] = Field(None, ge=1, le=5)
    lactation_number: Optional[int] = Field(None, ge=0, le=10)
    last_calving_date: Optional[date] = None
    heat_signs_observed: Optional[List[str]] = None
    ai_history: Optional[List[Dict[str, Any]]] = None
    bull_availability: Optional[bool] = None
    language: Language = Language.GUJLISH


class BreedingAdviceResponse(BaseResponse):
    request_id: str
    phone: str
    animal_type: AnimalType
    heat_detection_guide: List[str]
    optimal_breeding_window: Dict[str, Any]
    ai_vs_natural_service: Dict[str, Any]
    recommended_bull_breeds: List[str]
    pregnancy_diagnosis_timeline: List[str]
    dry_period_management: List[str]
    calving_preparation: List[str]
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str


class MilkQualityRequest(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    location: Location
    animal_type: AnimalType
    milk_sample_data: Dict[str, float]
    fat_percent: float = Field(..., ge=0, le=15)
    snf_percent: float = Field(..., ge=0, le=15)
    density: Optional[float] = Field(None, ge=1.0, le=1.05)
    ph: Optional[float] = Field(None, ge=6.0, le=7.0)
    temperature_celsius: Optional[float] = Field(None, ge=0, le=40)
    somatic_cell_count: Optional[int] = Field(None, ge=0)
    bacterial_count: Optional[int] = Field(None, ge=0)
    antibiotic_residue: Optional[bool] = None
    language: Language = Language.GUJLISH


class MilkQualityResponse(BaseResponse):
    request_id: str
    phone: str
    animal_type: AnimalType
    quality_grade: str = Field(..., pattern="^(Grade-A|Grade-B|Grade-C|Rejected)$")
    parameters: Dict[str, Any]
    compliance_status: Dict[str, str]
    issues_identified: List[str]
    corrective_actions: List[str]
    pricing_impact: Dict[str, float]
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str


class DiseaseOutbreakAlertRequest(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    location: Location
    animal_type: Optional[AnimalType] = None
    radius_km: int = Field(25, ge=5, le=100)
    language: Language = Language.GUJLISH


class DiseaseAlert(BaseModel):
    disease_name: str
    affected_villages: List[str]
    cases_reported: int
    deaths_reported: int
    outbreak_date: date
    risk_level: str = Field(..., pattern="^(low|medium|high|critical)$")
    symptoms_to_watch: List[str]
    preventive_measures: List[str]
    vaccination_recommended: bool
    vaccination_details: Optional[str] = None
    helpline_number: Optional[str] = None


class DiseaseOutbreakAlertResponse(BaseResponse):
    request_id: str
    phone: str
    location: Location
    active_alerts: List[DiseaseAlert]
    overall_risk: str = Field(..., pattern="^(low|medium|high)$")
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str


class LivestockSchemeRequest(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    location: Location
    animal_type: Optional[AnimalType] = None
    farmer_category: Optional[str] = Field(None, pattern="^(small|marginal|landless|women|sc_st|general)$")
    language: Language = Language.GUJLISH


class LivestockScheme(BaseModel):
    scheme_name: str
    sponsoring_agency: str
    description: str
    eligibility: List[str]
    benefits: List[str]
    subsidy_amount: Optional[str] = None
    application_process: List[str]
    documents_required: List[str]
    contact_info: Optional[str] = None
    deadline: Optional[date] = None
    website: Optional[str] = None


class LivestockSchemeResponse(BaseResponse):
    request_id: str
    phone: str
    location: Location
    schemes: List[LivestockScheme]
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str