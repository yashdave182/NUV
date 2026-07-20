from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional, Dict
from datetime import datetime, date, timedelta
import uuid

from agritech_api.schemas import (
    FarmInputRequest, FarmAdvisoryResponse, AdvisoryItem,
    DiseaseDetectionRequest, DiseaseDetectionResponse,
    CropCalendarRequest, CropCalendarResponse,
    SoilHealthCardRequest, SoilHealthCardResponse,
    VarietyRecommendationRequest, VarietyRecommendationResponse,
    IrrigationSchedulingRequest, IrrigationSchedulingResponse,
    FertilizerRecommendationRequest, FertilizerRecommendationResponse,
    PestDiseaseIdentificationRequest, PestDiseaseIdentificationResponse,
    WeatherAdvisoryRequest, WeatherAdvisoryResponse,
    IntercroppingAdviceRequest, IntercroppingAdviceResponse,
    CropInsuranceRequest, CropInsuranceResponse,
)
from agritech_api.services.agriculture_service import (
    get_crop_data, get_growth_stage, get_days_after_sowing,
    calculate_et0, calculate_crop_water_need,
    get_irrigation_advisory, get_fertilizer_advisory,
    get_pest_disease_advisory, get_weather_based_advice,
    get_next_scheduled_activities, generate_sms_summary,
    get_real_weather_data, get_satellite_data, get_soil_data,
    get_ml_yield_prediction,
)
from agritech_api.services.weather_service import (
    generate_weather_forecast, generate_weather_advisories, get_overall_risk,
    calculate_et0 as weather_et0, get_crop_coefficient, calculate_etc,
    assess_heat_stress, assess_cold_stress,
)
from ..schemas.common import Language
from agritech_api.schemas import GrowthStage

router = APIRouter(prefix="/agriculture", tags=["Agriculture Advisory"])


def build_advisory_item(adv_dict: Dict) -> AdvisoryItem:
    return AdvisoryItem(
        category=adv_dict.get("category", "general"),
        priority=adv_dict.get("priority", "medium"),
        title=adv_dict.get("title", ""),
        description=adv_dict.get("description", ""),
        rationale=adv_dict.get("rationale", ""),
        confidence=adv_dict.get("confidence", "Medium"),
        action_items=adv_dict.get("action_items", []),
        timeline_days=adv_dict.get("timeline_days", 7),
        estimated_cost_inr=adv_dict.get("estimated_cost_inr"),
        materials_needed=adv_dict.get("materials_needed", []),
        precautions=adv_dict.get("precautions", []),
        weather_dependent=adv_dict.get("weather_dependent", False),
        pest_disease_name=adv_dict.get("pest_disease_name"),
        threshold_reached=adv_dict.get("threshold_reached"),
    )


@router.post("/advisory", response_model=FarmAdvisoryResponse)
async def get_farm_advisory(request: FarmInputRequest, background_tasks: BackgroundTasks):
    try:
        request_id = str(uuid.uuid4())[:8]
        days_after_sowing = await get_days_after_sowing(request.sowing_date)
        growth_stage = await get_growth_stage(request.crop_type, days_after_sowing)
        
        weather_forecast = request.weather_forecast or await get_real_weather_data(request.location, 7)
        
        et0 = 0
        if request.temperature_celsius and request.humidity_percent:
            et0 = await calculate_et0(
                request.temperature_celsius + 3,
                request.temperature_celsius - 3,
                request.humidity_percent,
                request.wind_speed_kmph or 10
            )
        
        soil_data = await get_soil_data(request.location)
        
        irrigation_adv = await get_irrigation_advisory(
            request.crop_type, growth_stage, request.soil_type, request.irrigation_source,
            None, request.rainfall_mm or 0, et0, days_after_sowing,
            request.location, request.area_hectares,
        ) if et0 > 0 else None
        
        fertilizer_adv = await get_fertilizer_advisory(
            request.crop_type, growth_stage, request.area_hectares, soil_data
        )
        
        pest_disease_advs = await get_pest_disease_advisory(
            request.crop_type, growth_stage, request.pest_disease_observed, weather_forecast
        )
        
        weather_advice = get_weather_based_advice(weather_forecast)
        weather_advisories = generate_weather_advisories(weather_forecast, request.crop_type, growth_stage)
        
        all_advisories = []
        if irrigation_adv:
            all_advisories.append(irrigation_adv)
        all_advisories.append(fertilizer_adv)
        all_advisories.extend(pest_disease_advs)
        
        for w_adv in weather_advisories:
            all_advisories.append({
                "category": w_adv["category"],
                "priority": w_adv["priority"],
                "title": f"Weather: {w_adv['advisory'][:50]}",
                "description": w_adv["advisory"],
                "rationale": "Based on weather forecast",
                "confidence": "Medium",
                "action_items": ["Follow advisory"],
                "timeline_days": 1,
                "weather_dependent": True,
            })
        
        for w_adv in weather_advice:
            all_advisories.append({
                "category": "general",
                "priority": "low",
                "title": "Weather Note",
                "description": w_adv,
                "rationale": "Weather forecast based advice",
                "confidence": "Medium",
                "action_items": ["Monitor conditions"],
                "timeline_days": 1,
                "weather_dependent": True,
            })
        
        next_activities = get_next_scheduled_activities(request.crop_type, growth_stage, days_after_sowing)
        
        crop_data = await get_crop_data(request.crop_type)
        pest_risk = [
            {"pest": p, "risk": "medium", "stage": growth_stage.value}
            for p in crop_data["major_pests"][:3]
        ]
        pest_risk.extend([
            {"disease": d, "risk": "medium", "stage": growth_stage.value}
            for d in crop_data["major_diseases"][:2]
        ])
        
        sms = generate_sms_summary(all_advisories, request.language.value)
        
        advisory_items = [build_advisory_item(a) for a in all_advisories]
        
        yield_pred = await get_ml_yield_prediction(
            request.crop_type, request.area_hectares, request.soil_type or SoilType.ALLUVIAL,
            request.sowing_date, request.location, soil_data,
            [{"temp_max_c": w.get("temp_max_c", 30), "temp_min_c": w.get("temp_min_c", 20),
              "humidity_percent": w.get("humidity_percent", 60), "rainfall_mm": w.get("rainfall_mm", 0),
              "wind_speed_kmph": w.get("wind_speed_kmph", 10)} for w in weather_forecast],
            [{"ndvi": s.get("ndvi", 0.6), "soil_moisture_percent": s.get("soil_moisture_percent", 50),
              "crop_health_score": s.get("crop_health_score", 70)} for s in await get_satellite_data(
                  request.location, request.crop_type, request.area_hectares, request.sowing_date
              )],
            {"irrigation_count": 5, "fertilizer_n": 100, "fertilizer_p": 50, "fertilizer_k": 40,
             "pest_pressure": 0.1, "disease_pressure": 0.1},
        )
        
        return FarmAdvisoryResponse(
            request_id=request_id,
            phone=request.phone,
            crop_type=request.crop_type,
            growth_stage=growth_stage,
            days_after_sowing=days_after_sowing,
            advisories=advisory_items,
            weather_forecast=weather_forecast,
            soil_moisture_status="Adequate" if request.rainfall_mm and request.rainfall_mm > 10 else "Monitor",
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
            detailed_report_id=f"rpt_{request_id}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/irrigation", response_model=IrrigationSchedulingResponse)
async def get_irrigation_schedule(request: IrrigationSchedulingRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        days_after_sowing = await get_days_after_sowing(request.sowing_date)
        growth_stage = await get_growth_stage(request.crop_type, days_after_sowing)
        
        weather_forecast = request.weather_forecast or await get_real_weather_data(request.location, 7)
        et0_values = []
        for w in weather_forecast:
            et0 = await calculate_et0(
                w.get("temp_max_c", 30), w.get("temp_min_c", 20),
                w.get("humidity_percent", 60), w.get("wind_speed_kmph", 10)
            )
            et0_values.append(et0)
        
        avg_et0 = sum(et0_values) / len(et0_values) if et0_values else 5.0
        
        from agritech_api.schemas import GrowthStage
        last_irrigation_days = None
        if request.last_irrigation_date:
            last_irrigation_days = (date.today() - request.last_irrigation_date).days
        
        irrigation_adv = await get_irrigation_advisory(
            request.crop_type, growth_stage, request.soil_type, request.irrigation_source,
            last_irrigation_days, 0, avg_et0, days_after_sowing,
            request.location, request.area_hectares, request.irrigation_method,
        )
        
        schedule = []
        interval = irrigation_adv["interval_days"]
        for i in range(7):
            d = date.today() + timedelta(days=i * interval)
            schedule.append({
                "date": d.isoformat(),
                "depth_mm": irrigation_adv["depth_mm"],
                "volume_m3": irrigation_adv["volume_m3_per_ha"],
                "duration_hours": round(irrigation_adv["volume_m3_per_ha"] * request.area_hectares / 50, 1),
                "stage": growth_stage.value,
                "criticality": "critical" if growth_stage in [GrowthStage.FLOWERING, GrowthStage.FRUITING] else "optimal",
                "water_saving_tip": irrigation_adv["water_saving_tips"][i % len(irrigation_adv["water_saving_tips"])],
            })
        
        water_saving = [
            "Adopt drip/sprinkler irrigation",
            "Mulching to reduce evaporation",
            "Irrigate early morning/evening",
            "Laser land leveling",
            "Alternate wetting and drying for rice",
        ]
        
        sms = f"Irrigation: {irrigation_adv['etc_mm_day']:.1f} mm/day needed. Irrigate every {interval} days. {water_saving[0]}."
        
        return IrrigationSchedulingResponse(
            request_id=request_id,
            phone=request.phone,
            crop_type=request.crop_type,
            current_stage=growth_stage,
            eto_mm_per_day=round(avg_et0, 1),
            etc_mm_per_day=irrigation_adv["etc_mm_day"],
            soil_moisture_status="Monitor",
            irrigation_schedule=schedule,
            total_water_requirement_mm=round(irrigation_adv["etc_mm_day"] * await get_crop_data(request.crop_type)["duration_days"], 1),
            water_saving_recommendations=water_saving,
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
            detailed_report_id=f"rpt_irr_{request_id}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fertilizer", response_model=FertilizerRecommendationResponse)
async def get_fertilizer_recommendation(request: FertilizerRecommendationRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        days_after_sowing = await get_days_after_sowing(request.sowing_date)
        growth_stage = await get_growth_stage(request.crop_type, days_after_sowing)
        
        soil_test = None
        if request.available_n_kg_per_ha is not None:
            soil_test = {
                "available_n": request.available_n_kg_per_ha,
                "available_p": request.available_p_kg_per_ha,
                "available_k": request.available_k_kg_per_ha,
                "zn_ppm": request.available_zn_ppm,
                "fe_ppm": request.available_fe_ppm,
            }
        else:
            soil_data = await get_soil_data(request.location)
            soil_test = soil_data
        
        fertilizer_adv = await get_fertilizer_advisory(
            request.crop_type, growth_stage, request.area_hectares, soil_test
        )
        
        organic_alts = [
            {"name": "Vermicompost", "dose_tonnes_ha": 5, "nutrients": "N-P-K + micros"},
            {"name": "FYM", "dose_tonnes_ha": 10, "nutrients": "N-P-K + organic matter"},
            {"name": "Neem cake", "dose_kg_ha": 500, "nutrients": "N + pest repellent"},
            {"name": "Biofertilizers", "dose_kg_ha": 5, "nutrients": "N-fixing bacteria"},
        ]
        
        soil_advice = [
            "Test soil every 2 years",
            "Maintain pH 6.5-7.5",
            "Incorporate crop residues",
            "Green manuring before main crop",
        ]
        
        sms = f"Fertilizer: {fertilizer_adv['details']['recommended_npk']} kg/ha NPK. Apply {fertilizer_adv['action_items'][0] if fertilizer_adv['action_items'] else 'as per split'}. Cost: ₹{fertilizer_adv['details']['total_cost_inr']:.0f}/ha"
        
        return FertilizerRecommendationResponse(
            request_id=request_id,
            phone=request.phone,
            crop_type=request.crop_type,
            nutrient_recommendation=fertilizer_adv["details"]["recommended_npk"],
            fertilizer_schedule=fertilizer_adv["details"]["fertilizers"],
            total_fertilizer_cost_inr=fertilizer_adv["details"]["total_cost_inr"],
            organic_alternatives=organic_alts,
            soil_health_advice=soil_advice,
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
            detailed_report_id=f"rpt_fert_{request_id}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pest-disease", response_model=PestDiseaseIdentificationResponse)
async def identify_pest_disease(request: PestDiseaseIdentificationRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        matches = await get_pest_disease_advisory(
            request.crop_type, request.growth_stage, request.symptoms, request.recent_weather
        )
        
        pest_matches = []
        for m in matches:
            pest_matches.append({
                "pest_disease_name": m.get("pest_disease_name", "Unknown"),
                "scientific_name": None,
                "category": "pest" if "pest" in m.get("category", "") else "disease",
                "match_confidence": m.get("confidence", "Medium"),
                "key_symptoms_matched": request.symptoms[:3],
                "severity": m.get("severity", "moderate"),
                "economic_threshold": "5-10% damage",
                "spread_risk": "medium",
            })
        
        most_likely = pest_matches[0] if pest_matches else {
            "pest_disease_name": "Not identified",
            "scientific_name": None,
            "category": "unknown",
            "match_confidence": "Low",
            "key_symptoms_matched": [],
            "severity": "low",
            "economic_threshold": None,
            "spread_risk": "low",
        }
        
        immediate = [
            "Scout entire field for damage extent",
            "Collect samples for lab confirmation",
            "Avoid blanket spraying",
        ]
        
        treatments = [
            {"method": "Neem oil 5%", "dose": "3 ml/L", "target": "Broad spectrum"},
            {"method": "Bio-pesticide", "dose": "As per label", "target": "Specific pest"},
        ]
        
        preventive = [
            "Crop rotation", "Resistant varieties", "Balanced nutrition", "Field sanitation",
        ]
        
        monitoring = [
            "Weekly field scouting",
            "Pheromone trap monitoring",
            "Weather-based disease forecasting",
        ]
        
        sms = f"Pest/Disease: {most_likely['pest_disease_name']} risk {most_likely['severity']}. {immediate[0]}. Confidence: {most_likely['match_confidence']}"
        
        return PestDiseaseIdentificationResponse(
            request_id=request_id,
            phone=request.phone,
            crop_type=request.crop_type,
            matches=pest_matches,
            most_likely=most_likely,
            immediate_actions=immediate,
            recommended_treatments=treatments,
            preventive_measures=preventive,
            monitoring_schedule=monitoring,
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
            detailed_report_id=f"rpt_pest_{request_id}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calendar", response_model=CropCalendarResponse)
async def get_crop_calendar(request: CropCalendarRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        crop_data = await get_crop_data(request.crop_type)
        
        calendar = []
        for week in range(1, crop_data["duration_days"] // 7 + 2):
            stage = await get_growth_stage(request.crop_type, week * 7)
            activities = []
            
            if stage == GrowthStage.GERMINATION:
                activities = ["Gap filling", "First weeding", "Starter fertilizer"]
            elif stage == GrowthStage.VEGETATIVE:
                activities = ["Top dressing N", "Weeding", "Earthing up", "Pest monitoring"]
            elif stage == GrowthStage.FLOWERING:
                activities = ["Potash application", "Pollination support", "Disease monitoring"]
            elif stage == GrowthStage.FRUITING:
                activities = ["Fruit/pod monitoring", "Harvest preparation", "Pest control"]
            elif stage == GrowthStage.MATURITY:
                activities = ["Harvest planning", "Drying preparation", "Storage arrangement"]
            
            calendar.append({
                "week_after_sowing": week,
                "growth_stage": stage.value,
                "activity": ", ".join(activities),
                "category": "general",
                "description": f"Week {week} activities for {stage.value} stage",
                "inputs_needed": ["Fertilizer", "Pesticides"] if stage in [GrowthStage.VEGETATIVE, GrowthStage.FLOWERING] else [],
                "estimated_cost_inr": 2000 if stage in [GrowthStage.VEGETATIVE, GrowthStage.FLOWERING] else 1000,
                "weather_dependency": stage in [GrowthStage.FLOWERING, GrowthStage.FRUITING],
            })
        
        milestones = [
            {"milestone": "Sowing", "day": 0, "critical": True},
            {"milestone": "Emergence", "day": 10, "critical": True},
            {"milestone": "First weeding", "day": 20, "critical": False},
            {"milestone": "Flowering", "day": crop_data["stages"].get(GrowthStage.FLOWERING, (45, 60))[0], "critical": True},
            {"milestone": "Harvest", "day": crop_data["duration_days"], "critical": True},
        ]
        
        total_cost = sum(c.get("estimated_cost_inr", 0) for c in calendar)
        
        sms = f"Crop calendar: {crop_data['duration_days']} days. Key: Flowering day {milestones[3]['day']}, Harvest day {crop_data['duration_days']}."
        
        return CropCalendarResponse(
            request_id=request_id,
            phone=request.phone,
            crop_type=request.crop_type,
            season=request.season,
            sowing_window={"early": "Jun 15", "optimal": "Jul 1", "late": "Jul 15"},
            harvest_window={"early": "Oct 15", "optimal": "Nov 1", "late": "Nov 15"},
            calendar=calendar,
            key_milestones=milestones,
            total_estimated_cost_inr=total_cost,
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
            detailed_report_id=f"rpt_cal_{request_id}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/soil-health", response_model=SoilHealthCardResponse)
async def get_soil_health_card(request: SoilHealthCardRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        soil_data = await get_soil_data(request.location, request.survey_number)
        
        parameters = [
            {"parameter": "pH", "value": soil_data["ph"], "unit": "", "status": "optimal" if 6.5 <= soil_data["ph"] <= 7.5 else "medium", "recommendation": "Suitable for most crops"},
            {"parameter": "EC", "value": soil_data["ec_ds_m"], "unit": "dS/m", "status": "optimal" if soil_data["ec_ds_m"] < 1 else "medium", "recommendation": "No salinity issue"},
            {"parameter": "Organic Carbon", "value": soil_data["organic_carbon_percent"], "unit": "%", "status": "medium", "recommendation": "Add FYM/green manure"},
            {"parameter": "Available N", "value": soil_data["available_n_kg_ha"], "unit": "kg/ha", "status": "medium", "recommendation": "Apply recommended N dose"},
            {"parameter": "Available P", "value": soil_data["available_p_kg_ha"], "unit": "kg/ha", "status": "medium", "recommendation": "Apply P as per soil test"},
            {"parameter": "Available K", "value": soil_data["available_k_kg_ha"], "unit": "kg/ha", "status": "medium", "recommendation": "Apply K as per soil test"},
            {"parameter": "Sulphur", "value": soil_data["sulphur_ppm"], "unit": "ppm", "status": "medium", "recommendation": "Apply gypsum/elemental S if deficient"},
            {"parameter": "Zinc", "value": soil_data["zinc_ppm"], "unit": "ppm", "status": "medium" if soil_data["zinc_ppm"] > 0.6 else "low", "recommendation": "Apply ZnSO4 if <0.6 ppm"},
            {"parameter": "Boron", "value": soil_data["boron_ppm"], "unit": "ppm", "status": "low", "recommendation": "Apply borax for sensitive crops"},
        ]
        
        crop_suit = [
            {"crop": "Cotton", "suitability": "High"},
            {"crop": "Groundnut", "suitability": "High"},
            {"crop": "Wheat", "suitability": "Medium"},
            {"crop": "Cumin", "suitability": "High"},
        ]
        
        amendments = [
            {"amendment": "FYM 10 t/ha", "purpose": "Improve OC", "cost_inr_ha": 5000},
            {"amendment": "Gypsum 500 kg/ha", "purpose": "S supply", "cost_inr_ha": 1500},
            {"amendment": "ZnSO4 25 kg/ha", "purpose": "Zn correction", "cost_inr_ha": 1125},
        ]
        
        sms = f"Soil: pH {soil_data['ph']}, EC {soil_data['ec_ds_m']}, OC {soil_data['organic_carbon_percent']}%. N-P-K medium. Add FYM, gypsum, ZnSO4. Suitable for cotton, groundnut, cumin."
        
        return SoilHealthCardResponse(
            request_id=request_id,
            phone=request.phone,
            location=request.location,
            survey_number=request.survey_number,
            parameters=parameters,
            ph=soil_data["ph"],
            ec_ds_m=soil_data["ec_ds_m"],
            organic_carbon_percent=soil_data["organic_carbon_percent"],
            nitrogen_kg_ha=soil_data["available_n_kg_ha"],
            phosphorus_kg_ha=soil_data["available_p_kg_ha"],
            potassium_kg_ha=soil_data["available_k_kg_ha"],
            sulphur_ppm=soil_data["sulphur_ppm"],
            zinc_ppm=soil_data["zinc_ppm"],
            boron_ppm=soil_data["boron_ppm"],
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
            detailed_report_id=f"rpt_soil_{request_id}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/variety-recommendation", response_model=VarietyRecommendationResponse)
async def recommend_variety(request: VarietyRecommendationRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        varieties = {
            CropType.COTTON: [
                {"name": "G. Cot Hy 10", "yield": 2.8, "duration": 180, "traits": ["High yield", "Fusarium resistant"]},
                {"name": "BGII Hybrids", "yield": 3.0, "duration": 185, "traits": ["Bt cotton", "Bollworm resistant"]},
            ],
            CropType.GROUNDNUT: [
                {"name": "GG 20", "yield": 2.5, "duration": 115, "traits": ["High yield", "Tikka resistant"]},
                {"name": "GG 34", "yield": 2.3, "duration": 110, "traits": ["Early", "Drought tolerant"]},
            ],
            CropType.WHEAT: [
                {"name": "GW 451", "yield": 5.2, "duration": 125, "traits": ["Heat tolerant", "Rust resistant"]},
                {"name": "HD 3086", "yield": 5.5, "duration": 130, "traits": ["High yield", "Good chapati quality"]},
            ],
            CropType.CUMIN: [
                {"name": "GC 4", "yield": 0.7, "duration": 120, "traits": ["Wilt resistant", "High oil"]},
                {"name": "RZ 19", "yield": 0.65, "duration": 115, "traits": ["Early", "Blight tolerant"]},
            ],
        }
        
        crop_vars = varieties.get(request.crop_type, varieties[CropType.COTTON])
        
        recommended = []
        for v in crop_vars:
            recommended.append({
                "variety_name": v["name"],
                "release_year": 2020,
                "duration_days": v["duration"],
                "yield_potential_tonnes_per_ha": v["yield"],
                "special_traits": v["traits"],
                "disease_resistance": v["traits"],
                "pest_resistance": [],
                "quality_parameters": {"oil": "high" if request.crop_type in [CropType.GROUNDNUT, CropType.CUMIN] else "normal"},
                "suitable_regions": ["Gujarat", "Rajasthan", "Madhya Pradesh"],
                "seed_availability": "easy",
                "seed_cost_inr_per_kg": 500 if request.crop_type == CropType.COTTON else 200,
            })
        
        comparison = [
            {"variety": v["variety_name"], "yield": v["yield_potential_tonnes_per_ha"], "duration": v["duration_days"], "cost": v["seed_cost_inr_per_kg"]}
            for v in recommended
        ]
        
        guide = [
            "Match variety to your sowing window",
            "Check disease resistance for your area",
            "Ensure seed availability before season",
            "Consider market preference",
        ]
        
        sms = f"Varieties: {', '.join([v['variety_name'] for v in recommended])}. Yield: {recommended[0]['yield_potential_tonnes_per_ha']} t/ha. Duration: {recommended[0]['duration_days']} days."
        
        return VarietyRecommendationResponse(
            request_id=request_id,
            phone=request.phone,
            crop_type=request.crop_type,
            season=request.season,
            recommended_varieties=recommended,
            comparison_table=comparison,
            selection_guide=guide,
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
            detailed_report_id=f"rpt_var_{request_id}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/intercropping", response_model=IntercroppingAdviceResponse)
async def get_intercropping_advice(request: IntercroppingAdviceRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        options = {
            CropType.COTTON: [
                {"intercrop": "Green gram", "ratio": "1:1", "benefit": "N fixation, extra income"},
                {"intercrop": "Black gram", "ratio": "1:1", "benefit": "N fixation, weed suppression"},
                {"intercrop": "Soybean", "ratio": "1:2", "benefit": "High protein, soil health"},
            ],
            CropType.GROUNDNUT: [
                {"intercrop": "Castor", "ratio": "4:1", "benefit": "Different root zones, pest barrier"},
                {"intercrop": "Pigeon pea", "ratio": "6:1", "benefit": "Perennial, N fixation"},
            ],
            CropType.MAIZE: [
                {"intercrop": "Soybean", "ratio": "2:2", "benefit": "Classic combo, N fixation"},
                {"intercrop": "Cowpea", "ratio": "2:1", "benefit": "Fodder + grain"},
            ],
        }
        
        crop_options = options.get(request.main_crop, options[CropType.COTTON])
        
        result_options = []
        for o in crop_options:
            result_options.append({
                "intercrop": o["intercrop"],
                "row_ratio": o["ratio"],
                "spatial_arrangement": f"Additive series {o['ratio']}",
                "benefits": [o["benefit"], "Risk diversification", "Better resource use"],
                "additional_yield": {o["intercrop"]: 0.8},
                "additional_cost_inr": 3000,
                "management_complexity": "medium",
                "compatibility_score": 8.5,
            })
        
        best = result_options[0] if result_options else {}
        
        implementation = [
            "Sow intercrop same day or within 5 days",
            "Adjust fertilizer for both crops",
            "Monitor for competition",
            "Harvest intercrop first if earlier",
        ]
        
        risks = ["Competition for water/nutrients", "Harvest interference", "Pest/disease sharing"]
        
        sms = f"Intercrop: {best.get('intercrop', 'Green gram')} in {best.get('row_ratio', '1:1')} with cotton. Extra yield 0.8 t/ha. Cost: ₹3000/ha."
        
        return IntercroppingAdviceResponse(
            request_id=request_id,
            phone=request.phone,
            main_crop=request.main_crop,
            options=result_options,
            best_option=best,
            implementation_guide=implementation,
            risk_factors=risks,
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
            detailed_report_id=f"rpt_inter_{request_id}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crop-insurance", response_model=CropInsuranceResponse)
async def get_crop_insurance(request: CropInsuranceRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        options = [
            {
                "scheme_name": "PMFBY",
                "premium_rate_percent": 2.0 if request.season.value == "kharif" else 1.5,
                "farmer_share_percent": 2.0 if request.season.value == "kharif" else 1.5,
                "sum_insured_per_ha": request.sum_insured_per_ha or 50000,
                "coverage": ["Yield loss", "Prevented sowing", "Post-harvest loss", "Localized calamity"],
                "exclusions": ["War", "Nuclear risk", "Malicious damage", "Negligence"],
                "claim_process": ["Intimation within 72 hrs", "Joint inspection", "Claim settlement in 30 days"],
                "cut_off_date": date(2026, 7, 31) if request.season.value == "kharif" else date(2026, 12, 31),
                "implementing_agency": "Empanelled insurance company",
            },
            {
                "scheme_name": "RWBCIS",
                "premium_rate_percent": 3.0,
                "farmer_share_percent": 3.0,
                "sum_insured_per_ha": request.sum_insured_per_ha or 50000,
                "coverage": ["Weather indices", "Rainfall deficit/excess", "Temperature extremes", "Humidity"],
                "exclusions": ["Non-weather risks"],
                "claim_process": ["Automatic trigger", "No inspection needed", "Fast payout"],
                "cut_off_date": date(2026, 7, 31) if request.season.value == "kharif" else date(2026, 12, 31),
                "implementing_agency": "Empanelled insurance company",
            },
        ]
        
        recommended = options[0]
        premium = recommended["sum_insured_per_ha"] * request.area_hectares * recommended["farmer_share_percent"] / 100
        
        sms = f"PMFBY: Premium {recommended['farmer_share_percent']}% = ₹{premium:.0f} for {request.area_hectares} ha. Cut-off: {recommended['cut_off_date']}. Cover: yield loss, prevented sowing."
        
        return CropInsuranceResponse(
            request_id=request_id,
            phone=request.phone,
            crop_type=request.crop_type,
            season=request.season,
            options=options,
            recommended_option=recommended,
            premium_estimate_inr=round(premium),
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
            detailed_report_id=f"rpt_ins_{request_id}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/weather-advisory", response_model=WeatherAdvisoryResponse)
async def get_weather_advisory(request: WeatherAdvisoryRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        forecast = await get_real_weather_data(request.location, request.forecast_days)
        advisories = generate_weather_advisories(forecast, request.crop_type, request.growth_stage)
        risk = get_overall_risk(advisories)
        
        sms = f"Weather: {forecast[0]['condition']}, {forecast[0]['temp_max_c']:.0f}°C/{forecast[0]['temp_min_c']:.0f}°C. {advisories[0]['advisory'][:80] if advisories else 'No alerts'}. Risk: {risk}"
        
        return WeatherAdvisoryResponse(
            request_id=request_id,
            phone=request.phone,
            location=request.location,
            forecast=forecast,
            advisories=advisories,
            overall_risk=risk,
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))