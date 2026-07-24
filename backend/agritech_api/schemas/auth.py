from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class OTPRequest(BaseModel):
    phone: str = Field(..., description="10-digit mobile number")
    purpose: str = Field("login", description="Purpose: login / register")


class OTPResponse(BaseModel):
    success: bool = True
    message: str = "OTP sent successfully"
    otp_code: str = Field("123456", description="Demo OTP code for testing")
    expires_in_seconds: int = 300


class OTPVerifyRequest(BaseModel):
    phone: str = Field(..., description="10-digit mobile number")
    otp_code: str = Field(..., description="6-digit OTP code")


class PINLoginRequest(BaseModel):
    phone: str = Field(..., description="10-digit mobile number")
    pin: str = Field(..., description="4-digit security PIN")


class UserProfile(BaseModel):
    phone: str
    name: str = "Farmer"
    state: str = "Gujarat"
    district: str = "Anand"
    language: str = "English"
    land_holding_acres: float = 2.5
    soil_type: str = "black_cotton"
    primary_crops: List[str] = ["cotton", "wheat", "groundnut"]
    role: str = "farmer"
    created_at: Optional[str] = None


class FarmerRegisterRequest(BaseModel):
    phone: str = Field(..., description="10-digit mobile number")
    name: str = Field(..., description="Farmer full name")
    state: str = Field("Gujarat", description="State name")
    district: str = Field("Anand", description="District name")
    language: str = Field("English", description="Preferred language")
    land_holding_acres: float = Field(2.5, description="Land holding in acres")
    soil_type: str = Field("black_cotton", description="Primary soil type")
    primary_crops: List[str] = Field(default_factory=lambda: ["cotton", "wheat"], description="Primary crops cultivated")
    pin: Optional[str] = Field("1234", description="Optional 4-digit security PIN")


class AuthTokenResponse(BaseModel):
    success: bool = True
    access_token: str
    token_type: str = "bearer"
    user: UserProfile
    message: str = "Authentication successful"
