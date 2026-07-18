from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, date
import uuid

from agritech_api.schemas import (
    HealthAdvisoryRequest, HealthAdvisoryResponse, AdvisoryItem,
    VaccinationScheduleRequest, VaccinationScheduleResponse, VaccineInfo,
    HealthCampRequest, HealthCampResponse,
    EmergencyTriageRequest, EmergencyTriageResponse, TriageLevel,
    Language, Location, Gender, AgeGroup, HealthCategory, VitalSigns, SymptomInput,
)
from agritech_api.services.health_service import (
    match_symptoms_to_conditions, check_red_flags, triage_level,
    generate_health_advisory, get_vaccination_schedule, find_health_camps,
    get_nearest_facilities, get_condition_advice,
)
from agritech_api.schemas.common import Language, ConfidenceLevel

router = APIRouter(prefix="/health", tags=["Health Advisory"])


@router.post("/advisory", response_model=HealthAdvisoryResponse)
async def get_health_advisory(request: HealthAdvisoryRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        symptoms_list = [s.symptom for s in request.symptoms]
        age_group = request.patient.age_group
        pregnant = request.patient.pregnant or False
        
        advisories_data = generate_health_advisory(
            symptoms_list, age_group, request.patient.gender, pregnant,
            request.vital_signs, request.language
        )
        
        advisories = []
        for adv in advisories_data:
            advisories.append(AdvisoryItem(
                category=adv["category"],
                title=adv["title"],
                description=adv["description"],
                confidence=adv["confidence"],
                rationale=adv["rationale"],
                action_items=adv["action_items"],
                timeline_hours=adv["timeline_hours"],
                priority=adv["priority"],
                warning_signs=adv.get("warning_signs", []),
            ))
        
        red_flags = check_red_flags(symptoms_list, age_group, pregnant)
        referral = len(red_flags) > 0 or request.is_emergency
        
        facilities = get_nearest_facilities(request.location, emergency=request.is_emergency)
        
        vaccination_reminders = []
        if age_group in [AgeGroup.INFANT, AgeGroup.TODDLER, AgeGroup.CHILD]:
            vac_schedule = get_vaccination_schedule(request.patient.age_years * 365 // 30 * 30)  # approximate
            for v in vac_schedule.get("upcoming", [])[:3]:
                vaccination_reminders.append({
                    "vaccine": v["vaccine_name"],
                    "due_date": v["due_date"],
                    "status": v["status"],
                })
        
        sms_parts = []
        if red_flags:
            sms_parts.append(f"⚠️ EMERGENCY: {', '.join(red_flags[:2])}. Go to hospital NOW!")
        if advisories:
            top = advisories[0]
            sms_parts.append(f"{top.title}: {top.action_items[0] if top.action_items else 'Consult doctor'}")
        if not sms_parts:
            sms_parts.append("No immediate concerns. Monitor symptoms. Consult doctor if worsens.")
        
        sms = " | ".join(sms_parts)[:155]
        
        return HealthAdvisoryResponse(
            request_id=request_id,
            phone=request.phone,
            patient_profile={
                "age": request.patient.age_years,
                "gender": request.patient.gender.value,
                "age_group": age_group.value,
                "pregnant": pregnant,
            },
            advisories=advisories,
            red_flags=red_flags,
            referral_needed=referral,
            nearest_facilities=facilities,
            vaccination_reminders=vaccination_reminders,
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
            detailed_report_id=f"rpt_hlth_{request_id}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vaccination-schedule", response_model=VaccinationScheduleResponse)
async def get_vaccination_schedule_endpoint(request: VaccinationScheduleRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        schedule_data = get_vaccination_schedule(request.child_dob)
        
        vaccines = []
        for v in schedule_data["schedule"]:
            vaccines.append(VaccineInfo(
                vaccine_name=v["vaccine_name"],
                recommended_age=v["recommended_age"],
                dose_number=v["dose_number"],
                disease_prevented=", ".join(v["diseases_prevented"]),
                is_due=v["is_due"],
                due_date=date.fromisoformat(v["due_date"]) if v["due_date"] else None,
                nearest_center="Nearest PHC/Sub-centre",
            ))
        
        upcoming = [v for v in vaccines if v.is_due and not v.due_date > date.today()]
        missed = [v for v in vaccines if v.due_date and v.due_date < date.today() and not v.is_due]
        
        sms = f"Vaccination for {schedule_data['child_age_months']:.1f}mo child: {len(upcoming)} due, {len(missed)} missed. Next: {upcoming[0].vaccine_name if upcoming else 'None due'}."
        
        return VaccinationScheduleResponse(
            request_id=request_id,
            phone=request.phone,
            child_age_months=int(schedule_data["child_age_months"]),
            schedule=vaccines,
            upcoming=upcoming[:5],
            missed=missed,
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/health-camps", response_model=HealthCampResponse)
async def get_health_camps(request: HealthCampRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        camps = find_health_camps(request.location, request.radius_km, request.category)
        
        sms = f"Found {len(camps)} health camps within {request.radius_km}km. Nearest: {camps[0]['name'] if camps else 'None'} ({camps[0]['distance_km']:.0f}km)."
        
        return HealthCampResponse(
            request_id=request_id,
            camps=camps,
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/emergency-triage", response_model=EmergencyTriageResponse)
async def emergency_triage(request: EmergencyTriageRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        symptoms_list = [s.symptom for s in request.symptoms]
        age_group = AgeGroup.CHILD if request.patient_age < 12 else (AgeGroup.SENIOR if request.patient_age > 60 else AgeGroup.ADULT)
        
        triage = triage_level(symptoms_list, request.vital_signs, age_group)
        
        red_flags = check_red_flags(symptoms_list, age_group)
        
        immediate = []
        warning = []
        
        if triage == TriageLevel.RED:
            immediate = [
                "CALL 108 AMBULANCE IMMEDIATELY",
                "Go to nearest emergency department",
                "Do not delay - life threatening",
            ]
            warning = red_flags
        elif triage == TriageLevel.YELLOW:
            immediate = [
                "Seek medical attention within 1 hour",
                "Go to CHC/District Hospital",
                "Monitor vital signs",
            ]
            warning = ["Worsening symptoms", "Breathing difficulty", "Chest pain"]
        elif triage == TriageLevel.GREEN:
            immediate = [
                "Visit PHC within 24 hours",
                "Monitor symptoms",
                "Take prescribed medicines",
            ]
            warning = ["No improvement in 2 days", "New symptoms"]
        else:
            immediate = ["Self care at home", "Rest and hydration", "OTC medicines if needed"]
            warning = ["Symptoms worsen", "Fever >3 days"]
        
        ambulance = triage in [TriageLevel.RED, TriageLevel.YELLOW]
        facilities = get_nearest_facilities(request.location, emergency=True)
        
        sms = f"TRIAGE: {triage.value}. {'🚨 EMERGENCY - CALL 108' if triage == TriageLevel.RED else '⚠️ URGENT - Visit hospital' if triage == TriageLevel.YELLOW else '📋 Visit PHC within 24h' if triage == TriageLevel.GREEN else '🏠 Self care'}. {' | '.join(immediate[:2])}"
        
        return EmergencyTriageResponse(
            request_id=request_id,
            phone=request.phone,
            triage_level=triage,
            immediate_actions=immediate,
            warning_signs=warning,
            ambulance_needed=ambulance,
            nearest_emergency=facilities,
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))