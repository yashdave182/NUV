from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime


class Language(str, Enum):
    ENGLISH = "English"
    HINDI = "Hindi"
    GUJARATI = "Gujarati"
    HINGLISH = "Hinglish"
    GUJLISH = "Gujlish"
    MARATHI = "Marathi"
    MARATHISH = "Marathish"
    TAMIL = "Tamil"
    TELUGU = "Telugu"
    KANNADA = "Kannada"
    PUNJABI = "Punjabi"
    BENGALI = "Bengali"
    ODIA = "Odia"
    URDU = "Urdu"


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class Location(BaseModel):
    pincode: Optional[str] = Field(None, pattern=r"^\d{6}$")
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    village: Optional[str] = None
    taluka: Optional[str] = None
    district: Optional[str] = None
    state: str = "Gujarat"
    country: str = "India"

    @classmethod
    def from_pincode(cls, pincode: str):
        return cls(pincode=pincode)

    @classmethod
    def from_coordinates(cls, lat: float, lon: float):
        return cls(latitude=lat, longitude=lon)


class CropType(str, Enum):
    COTTON = "cotton"
    GROUNDNUT = "groundnut"
    WHEAT = "wheat"
    BAJRA = "bajra"
    MAIZE = "maize"
    CUMIN = "cumin"
    CASTOR = "castor"
    TOBACCO = "tobacco"
    SESAME = "sesame"
    GREEN_GRAM = "green_gram"
    BLACK_GRAM = "black_gram"
    PIGEON_PEA = "pigeon_pea"
    CHILLI = "chilli"
    ONION = "onion"
    POTATO = "potato"
    BANANA = "banana"
    PAPAYA = "papaya"
    MANGO = "mango"


class SoilType(str, Enum):
    BLACK_COTTON = "black_cotton"
    ALLUVIAL = "alluvial"
    RED_LOAM = "red_loam"
    SANDY_LOAM = "sandy_loam"
    CLAY = "clay"
    SALINE = "saline"
    ALKALINE = "alkaline"


class IrrigationSource(str, Enum):
    CANAL = "canal"
    BOREWELL = "borewell"
    OPEN_WELL = "open_well"
    POND = "pond"
    RAINFED = "rainfed"
    DRIP = "drip"
    SPRINKLER = "sprinkler"


class IrrigationMethod(str, Enum):
    FLOOD = "flood"
    DRIP = "drip"
    SPRINKLER = "sprinkler"
    FURROW = "furrow"


class StorageCondition(str, Enum):
    OPEN = "open"
    SHED = "shed"
    WAREHOUSE = "warehouse"
    COLD_STORAGE = "cold_storage"
    HERMETIC = "hermetic"
    SILOS = "silos"


class TransportMode(str, Enum):
    TRUCK = "truck"
    TRACTOR_TROLLEY = "tractor_trolley"
    MINI_TRUCK = "mini_truck"
    RAILWAY = "railway"
    OWN_VEHICLE = "own_vehicle"


class AdvisoryCategory(str, Enum):
    IRRIGATION = "irrigation"
    FERTILIZER = "fertilizer"
    PEST_DISEASE = "pest_disease"
    WEED_MANAGEMENT = "weed_management"
    HARVEST = "harvest"
    GENERAL = "general"


class AdvisoryPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class GrowthStage(str, Enum):
    GERMINATION = "germination"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    MATURITY = "maturity"
    HARVEST = "harvest"


class ConfidenceLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class DecisionAction(str, Enum):
    SELL_IMMEDIATELY = "sell_immediately"
    STORE = "store"
    TRANSPORT_TO_MANDI = "transport_to_mandi"
    WAIT = "wait"


class PriceTrend(str, Enum):
    RISING = "rising"
    STABLE = "stable"
    FALLING = "falling"
    VOLATILE = "volatile"


class AlertType(str, Enum):
    PRICE_THRESHOLD = "price_threshold"
    PRICE_DROP = "price_drop"
    PRICE_SPIKE = "price_spike"
    SPOILAGE_RISK = "spoilage_risk"
    WEATHER_ALERT = "weather_alert"
    PEST_OUTBREAK = "pest_outbreak"


class MandiType(str, Enum):
    APMC = "apmc"
    PRIVATE = "private"
    E_NAM = "e_nam"
    FPO = "fpo"
    DIRECT = "direct"


class WeatherCondition(str, Enum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    LIGHT_RAIN = "light_rain"
    MODERATE_RAIN = "moderate_rain"
    HEAVY_RAIN = "heavy_rain"
    THUNDERSTORM = "thunderstorm"
    HOT = "hot"
    COLD = "cold"
    WINDY = "windy"
    FOG = "fog"


class ReportFormat(str, Enum):
    HTML = "html"
    JSON = "json"
    PDF = "pdf"


class AnimalType(str, Enum):
    COW = "cow"
    BUFFALO = "buffalo"
    GOAT = "goat"
    SHEEP = "sheep"


class BreedType(str, Enum):
    GIR = "Gir"
    SAHIWAL = "Sahiwal"
    HF_CROSS = "HF_Cross"
    MURRAH = "Murrah"
    JAFFRABADI = "Jaffrabadi"
    SURTI = "Surti"
    MEHSANA = "Mehsana"
    OTHER = "Other"


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    SICK = "sick"
    RECOVERING = "recovering"
    CRITICAL = "critical"


class VaccinationStatus(str, Enum):
    UP_TO_DATE = "up_to_date"
    DUE = "due"
    OVERDUE = "overdue"
    UNKNOWN = "unknown"


class LactationStage(str, Enum):
    EARLY = "early"
    MID = "mid"
    LATE = "late"
    DRY = "dry"
    HEIFER = "heifer"


class HousingType(str, Enum):
    OPEN = "open"
    SHED = "shed"
    STALL_FED = "stall_fed"
    PASTURE = "pasture"
    SEMI_INTENSIVE = "semi_intensive"


class BaseRequest(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    language: Language = Language.GUJLISH
    request_id: Optional[str] = None


class BaseResponse(BaseModel):
    request_id: str
    phone: str
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str


class SMSAlertConfig(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    alert_type: AlertType
    crop_type: Optional[CropType] = None
    mandi_name: Optional[str] = None
    price_threshold: Optional[float] = Field(None, ge=0)
    price_direction: Optional[str] = Field(None, pattern="^(above|below)$")
    language: Language = Language.GUJLISH
    is_active: bool = True
    frequency: str = Field("daily", pattern="^(daily|weekly|instant)$")


class AlertSimulationRequest(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    location: Location
    crop_type: CropType
    quantity_kg: float = Field(..., gt=0)
    storage_condition: StorageCondition
    current_price: float = Field(..., ge=0)
    price_threshold: float = Field(..., ge=0)
    alert_type: AlertType = AlertType.PRICE_THRESHOLD
    language: Language = Language.GUJLISH


class AlertSimulationResponse(BaseModel):
    request_id: str
    phone: str
    alert_type: AlertType
    trigger_price: float
    current_price: float
    projected_prices: List[Dict[str, Any]]
    days_to_trigger: Optional[int] = None
    spoilage_risk: str = Field(..., pattern="^(low|medium|high)$")
    recommended_action: DecisionAction
    language: Language
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sms_summary: str