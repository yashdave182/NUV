from enum import Enum
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from .common import Language, Location


class HealthCategory(str, Enum):
    MATERNAL = "maternal"
    CHILD = "child"
    GENERAL = "general"
    VACCINATION = "vaccination"
    NUTRITION = "nutrition"
    SANITATION = "sanitation"
    EMERGENCY = "emergency"


class AgeGroup(str, Enum):
    INFANT = "infant"  # 0-1 year
    TODDLER = "toddler"  # 1-3 years
    CHILD = "child"  # 3-12 years
    ADOLESCENT = "adolescent"  # 12-18 years
    ADULT = "adult"  # 18-60 years
    SENIOR = "senior"  # 60+ years


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class SymptomInput(BaseModel):
    symptom: str
    duration_days: int = Field(..., ge=1, le=90)
    severity: str = Field(..., pattern="^(mild|moderate|severe)$")
    body_part: Optional[str] = None


class VitalSigns(BaseModel):
    temperature_c: Optional[float] = Field(None, ge=30, le=45)
    heart_rate_bpm: Optional[int] = Field(None, ge=30, le=200)
    respiratory_rate: Optional[int] = Field(None, ge=5, le=60)
    blood_pressure: Optional[str] = None
    oxygen_saturation: Optional[int] = Field(None, ge=50, le=100)
    weight_kg: Optional[float] = Field(None, ge=0.5, le=200)
    height_cm: Optional[float] = Field(None, ge=30, le=250)


class PatientProfile(BaseModel):
    age_years: int = Field(..., ge=0, le=120)
    gender: Gender
    age_group: AgeGroup
    pregnant: Optional[bool] = None
    chronic_conditions: List[str] = []
    current_medications: List[str] = []
    vaccination_status: Optional[Dict[str, bool]] = None
    last_antenatal_visit: Optional[date] = None


class HealthAdvisoryRequest(BaseModel):
    phone: str = Field(default="9876543210")
    location: Location = Field(default_factory=lambda: Location(state="Gujarat"))
    # Simple flat fields from frontend
    symptoms: Optional[List[Any]] = None  # can be list of strings or SymptomInput objects
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[str] = None
    # Full patient profile (optional, used if age/gender not provided directly)
    patient: Optional[Any] = None
    vital_signs: Optional[VitalSigns] = None
    category: HealthCategory = HealthCategory.GENERAL
    language: Language = Language.GUJLISH
    is_emergency: bool = False

    def get_age(self) -> int:
        if self.age is not None:
            return self.age
        if self.patient and hasattr(self.patient, 'age_years'):
            return self.patient.age_years
        if isinstance(self.patient, dict):
            return self.patient.get('age_years', 35)
        return 35

    def get_gender(self) -> str:
        if self.gender:
            return self.gender
        if self.patient and hasattr(self.patient, 'gender'):
            return str(self.patient.gender.value if hasattr(self.patient.gender, 'value') else self.patient.gender)
        if isinstance(self.patient, dict):
            return self.patient.get('gender', 'male')
        return 'male'

    def get_symptoms_list(self) -> List[str]:
        if not self.symptoms:
            return ['fever', 'fatigue']
        result = []
        for s in self.symptoms:
            if isinstance(s, str):
                result.append(s)
            elif isinstance(s, dict):
                result.append(s.get('symptom', str(s)))
            else:
                result.append(str(s))
        return result


class AdvisoryItem(BaseModel):
    category: str
    title: str
    description: str
    confidence: str = Field(..., pattern="^(High|Medium|Low)$")
    rationale: str
    action_items: List[str]
    timeline_hours: int = Field(..., ge=1, le=168)
    priority: int = Field(..., ge=1, le=3)
    warning_signs: List[str] = []


class HealthAdvisoryResponse(BaseModel):
    request_id: str
    phone: str
    patient_profile: Dict[str, Any]
    advisories: List[AdvisoryItem]
    red_flags: List[str] = []
    referral_needed: bool = False
    nearest_facilities: List[Dict[str, str]] = []
    vaccination_reminders: List[Dict[str, Any]] = []
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str
    detailed_report_id: Optional[str] = None

    @validator('sms_summary')
    def validate_sms_length(cls, v):
        if len(v) > 155:
            raise ValueError('SMS summary must be <= 155 characters')
        return v


class VaccinationScheduleRequest(BaseModel):
    phone: str = Field(default="9876543210")
    location: Location = Field(default_factory=lambda: Location(state="Gujarat"))
    child_dob: Optional[date] = None
    language: Language = Language.GUJLISH


class VaccineInfo(BaseModel):
    vaccine_name: str
    recommended_age: str
    dose_number: int
    disease_prevented: str
    is_due: bool
    due_date: Optional[date] = None
    nearest_center: Optional[str] = None


class VaccinationScheduleResponse(BaseModel):
    request_id: str
    phone: str
    child_age_months: int
    schedule: List[VaccineInfo]
    upcoming: List[VaccineInfo]
    missed: List[VaccineInfo]
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str


class HealthCampRequest(BaseModel):
    location: Location
    radius_km: int = Field(10, ge=1, le=50)
    category: Optional[HealthCategory] = None
    language: Language = Language.GUJLISH


class HealthCampResponse(BaseModel):
    request_id: str
    camps: List[Dict[str, Any]]
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str


class EmergencyTriageRequest(BaseModel):
    phone: str = Field(default="9876543210")
    location: Location = Field(default_factory=lambda: Location(state="Gujarat"))
    symptoms: Optional[List[Any]] = None  # list of strings or SymptomInput objects
    vital_signs: Optional[VitalSigns] = None
    patient_age: int = Field(default=35, ge=0, le=120)
    patient_gender: Optional[str] = None
    # Flat fields from frontend
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[str] = None
    language: Language = Language.GUJLISH

    def get_symptoms_list(self) -> List[str]:
        if not self.symptoms:
            return ['chest pain']
        return [s if isinstance(s, str) else s.get('symptom', str(s)) if isinstance(s, dict) else str(s) for s in self.symptoms]


class TriageLevel(str, Enum):
    RED = "RED"  # Immediate emergency
    YELLOW = "YELLOW"  # Urgent - within 1 hour
    GREEN = "GREEN"  # Non-urgent - within 24 hours
    BLUE = "BLUE"  # Minor - self care


class EmergencyTriageResponse(BaseModel):
    request_id: str
    phone: str
    triage_level: TriageLevel
    immediate_actions: List[str]
    warning_signs: List[str]
    ambulance_needed: bool
    nearest_emergency: List[Dict[str, str]]
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str