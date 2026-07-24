from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional, Dict
import datetime

from agritech_api.schemas.auth import (
    OTPRequest, OTPResponse, OTPVerifyRequest, PINLoginRequest, UserProfile,
    FarmerRegisterRequest, AuthTokenResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication & Farmer Profiles"])

# In-memory user database for demo persistence
USERS_DB: Dict[str, UserProfile] = {
    "9099314955": UserProfile(
        phone="9099314955",
        name="Ramesh Patel",
        state="Gujarat",
        district="Anand",
        language="English",
        land_holding_acres=3.5,
        soil_type="black_cotton",
        primary_crops=["cotton", "wheat", "groundnut"],
        created_at="2026-01-10T10:00:00Z"
    ),
    "9876543210": UserProfile(
        phone="9876543210",
        name="Suresh Kumar",
        state="Gujarat",
        district="Rajkot",
        language="Gujarati",
        land_holding_acres=5.0,
        soil_type="alluvial",
        primary_crops=["groundnut", "cumin"],
        created_at="2026-02-14T11:30:00Z"
    )
}

# PIN Store for PIN-based login
PIN_STORE: Dict[str, str] = {
    "9099314955": "1234",
    "9876543210": "1234"
}

# OTP Store for validation
OTP_STORE: Dict[str, str] = {}


@router.post(
    "/otp/send",
    response_model=OTPResponse,
    summary="Send Mobile OTP",
    description="Generate and send a 6-digit OTP code to the farmer's mobile number (Default Demo OTP: 123456)."
)
async def send_otp(req: OTPRequest):
    phone = req.phone.strip()
    if not phone or len(phone) < 10:
        raise HTTPException(status_code=400, detail="Invalid 10-digit mobile number")

    demo_otp = "123456"
    OTP_STORE[phone] = demo_otp

    return OTPResponse(
        success=True,
        message=f"OTP sent successfully to +91 {phone}",
        otp_code=demo_otp,
        expires_in_seconds=300
    )


@router.post(
    "/otp/verify",
    response_model=AuthTokenResponse,
    summary="Verify OTP & Login",
    description="Verify 6-digit OTP code and retrieve access token & farmer profile."
)
async def verify_otp(req: OTPVerifyRequest):
    phone = req.phone.strip()
    code = req.otp_code.strip()

    expected = OTP_STORE.get(phone, "123456")
    if code != expected and code != "123456":
        raise HTTPException(status_code=400, detail="Invalid OTP code. Use demo code '123456'.")

    # Fetch existing user or create default profile for new number
    if phone in USERS_DB:
        user = USERS_DB[phone]
    else:
        user = UserProfile(
            phone=phone,
            name=f"Farmer ({phone[-4:]})",
            state="Gujarat",
            district="Anand",
            language="English",
            land_holding_acres=2.5,
            soil_type="black_cotton",
            primary_crops=["cotton", "wheat"],
            created_at=datetime.datetime.utcnow().isoformat()
        )
        USERS_DB[phone] = user

    token = f"agritech_token_{phone}_{int(datetime.datetime.utcnow().timestamp())}"

    return AuthTokenResponse(
        success=True,
        access_token=token,
        token_type="bearer",
        user=user,
        message="Login successful"
    )


@router.post(
    "/login/pin",
    response_model=AuthTokenResponse,
    summary="PIN / Password Login",
    description="Login using mobile number and 4-digit PIN."
)
async def login_with_pin(req: PINLoginRequest):
    phone = req.phone.strip()
    pin = req.pin.strip()

    if not phone or len(phone) < 10:
        raise HTTPException(status_code=400, detail="Invalid 10-digit mobile number")

    expected_pin = PIN_STORE.get(phone, "1234")
    if pin != expected_pin and pin != "1234":
        raise HTTPException(status_code=400, detail="Invalid PIN. Default demo PIN is '1234'.")

    if phone in USERS_DB:
        user = USERS_DB[phone]
    else:
        user = UserProfile(
            phone=phone,
            name=f"Farmer ({phone[-4:]})",
            state="Gujarat",
            district="Anand",
            language="English",
            land_holding_acres=2.5,
            soil_type="black_cotton",
            primary_crops=["cotton", "wheat"],
            created_at=datetime.datetime.utcnow().isoformat()
        )
        USERS_DB[phone] = user

    token = f"agritech_token_{phone}_{int(datetime.datetime.utcnow().timestamp())}"

    return AuthTokenResponse(
        success=True,
        access_token=token,
        token_type="bearer",
        user=user,
        message="PIN authentication successful"
    )


@router.post(
    "/register",
    response_model=AuthTokenResponse,
    summary="Register Farmer Profile",
    description="Register a new farmer profile with farm parameters and crops."
)
async def register_farmer(req: FarmerRegisterRequest):
    phone = req.phone.strip()
    if not phone or len(phone) < 10:
        raise HTTPException(status_code=400, detail="Invalid 10-digit mobile number")

    profile = UserProfile(
        phone=phone,
        name=req.name.strip(),
        state=req.state,
        district=req.district,
        language=req.language,
        land_holding_acres=req.land_holding_acres,
        soil_type=req.soil_type,
        primary_crops=req.primary_crops,
        created_at=datetime.datetime.utcnow().isoformat()
    )

    USERS_DB[phone] = profile
    if req.pin:
        PIN_STORE[phone] = req.pin.strip()

    token = f"agritech_token_{phone}_{int(datetime.datetime.utcnow().timestamp())}"

    return AuthTokenResponse(
        success=True,
        access_token=token,
        token_type="bearer",
        user=profile,
        message="Farmer account registered successfully"
    )


@router.get(
    "/me",
    response_model=UserProfile,
    summary="Get Active User Context",
    description="Retrieve farmer profile associated with X-Phone header or phone query param."
)
async def get_me(
    x_phone: Optional[str] = Header(None, alias="X-Phone"),
    phone: Optional[str] = Query(None)
):
    target_phone = phone or x_phone or "9099314955"
    if target_phone in USERS_DB:
        return USERS_DB[target_phone]

    return UserProfile(
        phone=target_phone,
        name="Guest Farmer",
        state="Gujarat",
        district="Anand",
        language="English"
    )
