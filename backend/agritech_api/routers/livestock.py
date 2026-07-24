from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, date
import uuid

from agritech_api.schemas import (
    LivestockProfileRequest, LivestockProfileResponse,
    VaccinationScheduleRequest, VaccinationScheduleResponse, VaccineDose,
    HealthDiagnosisRequest, HealthDiagnosisResponse, DifferentialDiagnosis,
    DewormingScheduleRequest, DewormingScheduleResponse, DewormerOption,
    FeedFormulationRequest, FeedFormulationResponse, FeedFormulation, FeedIngredient,
    BreedingAdviceRequest, BreedingAdviceResponse,
    MilkQualityRequest, MilkQualityResponse,
    DiseaseOutbreakAlertRequest, DiseaseOutbreakAlertResponse, DiseaseAlert,
    LivestockSchemeRequest, LivestockSchemeResponse, LivestockScheme,
    AnimalType, BreedType, VaccinationStatus, LactationStage, HousingType,
    Language, Location,
)
from agritech_api.services.livestock_service import (
    get_vaccination_schedule as service_get_vaccination_schedule,
    get_deworming_schedule as service_get_deworming_schedule,
    formulate_feed as service_formulate_feed,
    diagnose_health as service_diagnose_health,
    get_breeding_advice as service_get_breeding_advice,
    assess_milk_quality as service_assess_milk_quality,
    get_disease_alerts as service_get_disease_alerts,
    get_livestock_schemes as service_get_livestock_schemes,
)
from agritech_api.schemas.common import Language, ConfidenceLevel

router = APIRouter(prefix="/livestock", tags=["Livestock Advisory"])


@router.post("/profile", response_model=LivestockProfileResponse)
async def get_livestock_profile(request: LivestockProfileRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        schedule = service_get_vaccination_schedule(
            request.animal_type, request.age_months,
            request.last_vaccination_date, request.last_vaccine_name,
            request.pregnancy_month,
        )
        
        upcoming = [v for v in schedule if v.status in ["due", "overdue"]]
        
        deworming = service_get_deworming_schedule(
            request.animal_type, request.age_months, request.weight_kg or 300,
            request.deworming_date, request.lactation_stage, request.pregnancy_month,
        )
        
        sms = f"{request.animal_type.value.title()} profile: {request.age_months}mo, {request.weight_kg or '?'}kg. Vaccines due: {len(upcoming)}. Deworming: {deworming['schedule'][0]['action'] if deworming['schedule'] else 'Current'}."
        
        return LivestockProfileResponse(
            request_id=request_id,
            phone=request.phone,
            animal_type=request.animal_type,
            profile_summary={
                "age_months": request.age_months,
                "weight_kg": request.weight_kg,
                "bcs": request.body_condition_score,
                "lactation": request.lactation_stage.value if request.lactation_stage else None,
                "pregnancy_month": request.pregnancy_month,
            },
            health_assessment="Good" if request.body_condition_score and request.body_condition_score >= 3 else "Needs improvement",
            recommendations=[
                "Maintain balanced nutrition",
                "Follow vaccination schedule",
                "Regular deworming",
                "Clean water ad libitum",
            ],
            upcoming_vaccinations=[{
                "vaccine": v.vaccine_name,
                "due_date": v.recommended_date.isoformat() if v.recommended_date else None,
                "status": v.status,
            } for v in upcoming[:5]],
            upcoming_deworming=deworming["schedule"][0] if deworming["schedule"] else None,
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vaccination-schedule", response_model=VaccinationScheduleResponse)
async def get_vaccination_schedule_endpoint(request: VaccinationScheduleRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        schedule = service_get_vaccination_schedule(
            request.animal_type, request.age_months,
            request.last_vaccination_date, request.last_vaccine_name,
            request.pregnancy_month,
        )
        
        completed = len([v for v in schedule if v.status == "completed"])
        due = len([v for v in schedule if v.status == "due"])
        overdue = len([v for v in schedule if v.status == "overdue"])
        
        sms = f"Vaccination schedule for {request.animal_type.value}: {completed} done, {due} due, {overdue} overdue. Next: {[v.vaccine_name for v in schedule if v.status in ['due','overdue']][:2]}."
        
        return VaccinationScheduleResponse(
            request_id=request_id,
            phone=request.phone,
            animal_type=request.animal_type,
            schedule=schedule,
            completed_count=completed,
            due_count=due,
            overdue_count=overdue,
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/health-diagnosis", response_model=HealthDiagnosisResponse)
async def diagnose_health(request: HealthDiagnosisRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        diagnosis = service_diagnose_health(
            request.animal_type, request.breed, request.age_months,
            request.symptoms, request.symptom_duration_days,
            request.temperature_celsius, request.appetite, request.milk_yield_change,
            request.faeces_consistency, request.respiration, request.behaviour,
            request.skin_lesions, request.discharge, request.lameness,
            request.recent_vaccination, request.recent_deworming,
            request.herd_size, request.similar_cases_in_herd,
        )
        
        differentials = []
        for d in diagnosis["differential_diagnoses"]:
            differentials.append(DifferentialDiagnosis(
                disease_name=d["disease_name"],
                probability=d["probability"],
                matching_symptoms=d["matching_symptoms"],
                key_differentiating_features=d["key_differentiating_features"],
                urgency=d["urgency"],
            ))
        
        most_likely = DifferentialDiagnosis(**diagnosis["most_likely"])
        
        sms = f"⚠️ {diagnosis['most_likely']['disease_name']} ({diagnosis['most_likely']['probability']*100:.0f}%). Urgency: {diagnosis['most_likely']['urgency']}. {diagnosis['immediate_actions'][0]}. Vet needed: {diagnosis['requires_vet_visit']}."
        
        return HealthDiagnosisResponse(
            request_id=request_id,
            phone=request.phone,
            animal_type=request.animal_type,
            differential_diagnoses=differentials,
            most_likely=most_likely,
            immediate_actions=diagnosis["immediate_actions"],
            recommended_tests=diagnosis["recommended_tests"],
            treatment_suggestions=diagnosis["treatment_suggestions"],
            withdrawal_periods=diagnosis["withdrawal_periods"],
            preventive_measures=diagnosis["preventive_measures"],
            requires_vet_visit=diagnosis["requires_vet_visit"],
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deworming", response_model=DewormingScheduleResponse)
async def get_deworming_schedule(request: DewormingScheduleRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        deworming = service_get_deworming_schedule(
            request.animal_type, request.age_months, request.weight_kg or 300,
            request.last_deworming_date, request.lactation_stage,
            request.pregnancy_month, request.faecal_egg_count,
        )
        
        sms = f"Deworming: {deworming['schedule'][0]['action'] if deworming['schedule'] else 'Current'}. {deworming['faecal_egg_count_interpretation'] or 'No FEC data'}. Recommended: {[d.dewormer_name for d in deworming['recommended_dewormers'][:2]]}."
        
        return DewormingScheduleResponse(
            request_id=request_id,
            phone=request.phone,
            animal_type=request.animal_type,
            recommended_dewormers=deworming["recommended_dewormers"],
            schedule=deworming["schedule"],
            faecal_egg_count_interpretation=deworming["faecal_egg_count_interpretation"],
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feed-formulation", response_model=FeedFormulationResponse)
async def get_feed_formulation(request: FeedFormulationRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        formulation = service_formulate_feed(
            request.animal_type, request.weight_kg or 450, request.lactation_stage,
            request.milk_yield_litres, request.pregnancy_month,
            request.available_ingredients or [], request.budget_per_kg_inr,
        )
        
        rec = formulation["recommended_formulation"]
        sms = f"Feed for {request.animal_type.value} {request.weight_kg}kg: {len(rec.ingredients)} ingredients. Cost: ₹{rec.total_cost_per_day_inr:.0f}/day ({rec.cost_per_litre_milk_inr or 'N/A'}/L). Meets needs: {rec.meets_requirements}."
        
        return FeedFormulationResponse(
            request_id=request_id,
            phone=request.phone,
            animal_type=request.animal_type,
            nutritional_requirements=formulation["nutritional_requirements"],
            formulations=formulation["formulations"],
            recommended_formulation=formulation["recommended_formulation"],
            locally_available_substitutes=formulation["locally_available_substitutes"],
            feeding_schedule=formulation["feeding_schedule"],
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/breeding-advice", response_model=BreedingAdviceResponse)
async def get_breeding_advice(request: BreedingAdviceRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        advice = service_get_breeding_advice(
            request.animal_type, request.age_months, request.weight_kg or 450,
            request.body_condition_score, request.lactation_number,
            request.last_calving_date, request.heat_signs_observed, request.ai_history,
        )
        
        sms = f"Breeding: {advice['optimal_breeding_window']}. Heat signs: {len(advice['heat_detection_guide'])}. AI recommended: {advice['ai_vs_natural_service']['recommendation']}. PD at 28-35 days."
        
        return BreedingAdviceResponse(
            request_id=request_id,
            phone=request.phone,
            animal_type=request.animal_type,
            heat_detection_guide=advice["heat_detection_guide"],
            optimal_breeding_window=advice["optimal_breeding_window"],
            ai_vs_natural_service=advice["ai_vs_natural_service"],
            recommended_bull_breeds=advice["recommended_bull_breeds"],
            pregnancy_diagnosis_timeline=advice["pregnancy_diagnosis_timeline"],
            dry_period_management=advice["dry_period_management"],
            calving_preparation=advice["calving_preparation"],
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/milk-quality", response_model=MilkQualityResponse)
async def assess_milk_quality(request: MilkQualityRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        quality = service_assess_milk_quality(
            request.fat_percent, request.snf_percent, request.density,
            request.ph, request.temperature_celsius, request.somatic_cell_count,
            request.bacterial_count, request.antibiotic_residue,
        )
        
        sms = f"Milk quality: {quality['quality_grade']}. Fat: {request.fat_percent}%, SNF: {request.snf_percent}%. Issues: {len(quality['issues_identified'])}. {quality['corrective_actions'][0] if quality['corrective_actions'] else 'Compliant'}."
        
        return MilkQualityResponse(
            request_id=request_id,
            phone=request.phone,
            animal_type=request.animal_type,
            quality_grade=quality["quality_grade"],
            parameters=quality["parameters"],
            compliance_status=quality["compliance_status"],
            issues_identified=quality["issues_identified"],
            corrective_actions=quality["corrective_actions"],
            pricing_impact=quality["pricing_impact"],
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disease-alerts", response_model=DiseaseOutbreakAlertResponse)
async def get_disease_alerts(request: DiseaseOutbreakAlertRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        alerts = service_get_disease_alerts(request.location, request.animal_type, request.radius_km)
        
        overall_risk = "high" if any(a["risk_level"] == "critical" for a in alerts) else "medium" if alerts else "low"
        
        sms = f"Disease alerts ({len(alerts)}): {', '.join([a['disease_name'] for a in alerts[:3]])}. Risk: {overall_risk}. {alerts[0]['preventive_measures'][0] if alerts else 'No alerts'}."
        
        return DiseaseOutbreakAlertResponse(
            request_id=request_id,
            phone=request.phone,
            location=request.location,
            active_alerts=[DiseaseAlert(**a) for a in alerts],
            overall_risk=overall_risk,
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schemes", response_model=LivestockSchemeResponse)
async def get_livestock_schemes(request: LivestockSchemeRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        schemes = service_get_livestock_schemes(request.location, request.animal_type, request.farmer_category)
        
        sms = f"Livestock schemes ({len(schemes)}): {', '.join([s['scheme_name'][:15] for s in schemes[:3]])}. Subsidy: {schemes[0].get('subsidy_amount', 'Contact vet officer')}."
        
        return LivestockSchemeResponse(
            request_id=request_id,
            phone=request.phone,
            location=request.location,
            schemes=[LivestockScheme(**s) for s in schemes],
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))