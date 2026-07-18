from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from .common import Language, Location


class SchemeCategory(str, Enum):
    AGRICULTURE = "agriculture"
    LIVESTOCK = "livestock"
    HEALTH = "health"
    WOMEN = "women"
    EDUCATION = "education"
    HOUSING = "housing"
    EMPLOYMENT = "employment"
    SOCIAL_SECURITY = "social_security"
    DISASTER_RELIEF = "disaster_relief"


class BeneficiaryType(str, Enum):
    FARMER = "farmer"
    LANDLESS_LABOURER = "landless_labourer"
    WOMEN = "women"
    CHILD = "child"
    SENIOR_CITIZEN = "senior_citizen"
    DISABLED = "disabled"
    SC_ST = "sc_st"
    MINORITY = "minority"
    GENERAL = "general"


class SchemeQueryRequest(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    location: Location
    category: Optional[SchemeCategory] = None
    beneficiary_type: Optional[BeneficiaryType] = None
    keywords: Optional[List[str]] = None
    language: Language = Language.GUJLISH
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[str] = Field(None, pattern="^(male|female)$")
    annual_income: Optional[float] = Field(None, ge=0)
    land_holding_hectares: Optional[float] = Field(None, ge=0)
    caste_category: Optional[str] = Field(None, pattern="^(SC|ST|OBC|General|Minority)$")


class SchemeSummary(BaseModel):
    scheme_id: str
    name: str
    category: SchemeCategory
    implementing_agency: str
    level: str = Field(..., pattern="^(Central|State|District|Block)$")
    benefit_summary: str
    eligibility_summary: str


class SchemeQueryResponse(BaseModel):
    request_id: str
    phone: str
    matched_schemes: List[SchemeSummary]
    total_count: int
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str
    detailed_report_id: Optional[str] = None


class SchemeDetailRequest(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    scheme_id: str
    language: Language = Language.GUJLISH


class DocumentRequirement(BaseModel):
    document_name: str
    description: str
    mandatory: bool = True
    alternatives: List[str] = []


class ApplicationStep(BaseModel):
    step_number: int
    title: str
    description: str
    channel: str = Field(..., pattern="^(online|offline|both)$")
    authority: str
    estimated_days: int
    documents_needed: List[str]


class SchemeDetailResponse(BaseModel):
    request_id: str
    phone: str
    scheme_id: str
    name: str
    category: SchemeCategory
    description: str
    implementing_agency: str
    level: str
    target_beneficiaries: List[BeneficiaryType]
    eligibility_criteria: List[str]
    benefits: List[Dict[str, Any]]
    documents_required: List[DocumentRequirement]
    application_process: List[ApplicationStep]
    official_website: Optional[str] = None
    helpline: Optional[str] = None
    contact_person: Optional[str] = None
    last_updated: date
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str
    detailed_report_id: Optional[str] = None


class ApplicationTrackerRequest(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    application_id: str
    language: Language = Language.GUJLISH


class ApplicationStatus(BaseModel):
    application_id: str
    scheme_name: str
    status: str = Field(..., pattern="^(submitted|under_review|approved|rejected|disbursed|pending_documents)$")
    current_stage: str
    submitted_date: date
    last_updated: date
    expected_completion: Optional[date] = None
    remarks: Optional[str] = None
    documents_pending: List[str] = []


class ApplicationTrackerResponse(BaseModel):
    request_id: str
    phone: str
    application: ApplicationStatus
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str


class EligibilityCheckRequest(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    location: Location
    scheme_id: str
    profile: Dict[str, Any]
    language: Language = Language.GUJLISH


class EligibilityResult(BaseModel):
    scheme_id: str
    scheme_name: str
    is_eligible: bool
    eligibility_score: float = Field(..., ge=0, le=100)
    met_criteria: List[str]
    unmet_criteria: List[str]
    missing_documents: List[str]
    estimated_benefit: Optional[str] = None
    next_steps: List[str]


class EligibilityCheckResponse(BaseModel):
    request_id: str
    phone: str
    result: EligibilityResult
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str