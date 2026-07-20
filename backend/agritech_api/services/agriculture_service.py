import asyncio
import math
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta

from agritech_api.schemas import (
    CropType, SoilType, IrrigationSource, WeatherCondition,
    AdvisoryCategory, AdvisoryPriority, ConfidenceLevel,
    GrowthStage, Season, FertilizerType, PestSeverity, Location
)

from agritech_api.clients import (
    get_weather_client, get_satellite_client, get_soil_client
)
from agritech_api.ml_models import (
    get_model_manager,
    YieldPrediction, PriceForecast, DiseaseRisk
)


CROP_DATA = {
    CropType.COTTON: {
        "duration_days": 180, "water_requirement_mm": 700,
        "n_kg_ha": 120, "p_kg_ha": 60, "k_kg_ha": 60,
        "stages": {GrowthStage.GERMINATION: (0, 15), GrowthStage.VEGETATIVE: (15, 60),
                   GrowthStage.FLOWERING: (60, 120), GrowthStage.FRUITING: (120, 160),
                   GrowthStage.MATURITY: (160, 180)},
        "major_pests": ["pink_bollworm", "whitefly", "aphid", "jassid"],
        "major_diseases": ["boll_rot", "leaf_curl", "root_rot", "bacterial_blight"],
        "critical_stages": [GrowthStage.FLOWERING, GrowthStage.FRUITING],
        "base_yield_tonnes_ha": 2.5,
        "optimal_temp": (25, 35), "optimal_rainfall": (600, 1000),
    },
    CropType.GROUNDNUT: {
        "duration_days": 120, "water_requirement_mm": 500,
        "n_kg_ha": 20, "p_kg_ha": 40, "k_kg_ha": 40,
        "stages": {GrowthStage.GERMINATION: (0, 15), GrowthStage.VEGETATIVE: (15, 45),
                   GrowthStage.FLOWERING: (45, 75), GrowthStage.FRUITING: (75, 105),
                   GrowthStage.MATURITY: (105, 120)},
        "major_pests": ["leaf_miner", "spodoptera", "thrips", "aphid"],
        "major_diseases": ["tikka", "rust", "stem_rot", "bud_necrosis"],
        "critical_stages": [GrowthStage.FLOWERING, GrowthStage.FRUITING],
        "base_yield_tonnes_ha": 2.0,
        "optimal_temp": (25, 30), "optimal_rainfall": (450, 750),
    },
    CropType.WHEAT: {
        "duration_days": 130, "water_requirement_mm": 450,
        "n_kg_ha": 120, "p_kg_ha": 60, "k_kg_ha": 40,
        "stages": {GrowthStage.GERMINATION: (0, 20), GrowthStage.VEGETATIVE: (20, 60),
                   GrowthStage.FLOWERING: (60, 85), GrowthStage.FRUITING: (85, 110),
                   GrowthStage.MATURITY: (110, 130)},
        "major_pests": ["aphid", "pink_borer", "termite"],
        "major_diseases": ["yellow_rust", "brown_rust", "loose_smut", "karnal_bunt"],
        "critical_stages": [GrowthStage.FLOWERING, GrowthStage.FRUITING],
        "base_yield_tonnes_ha": 4.5,
        "optimal_temp": (15, 25), "optimal_rainfall": (300, 500),
    },
    CropType.BAJRA: {
        "duration_days": 90, "water_requirement_mm": 400,
        "n_kg_ha": 80, "p_kg_ha": 40, "k_kg_ha": 40,
        "stages": {GrowthStage.GERMINATION: (0, 15), GrowthStage.VEGETATIVE: (15, 40),
                   GrowthStage.FLOWERING: (40, 60), GrowthStage.FRUITING: (60, 80),
                   GrowthStage.MATURITY: (80, 90)},
        "major_pests": ["shoot_fly", "stem_borer", "earhead_worm"],
        "major_diseases": ["downy_mildew", "ergot", "smut"],
        "critical_stages": [GrowthStage.VEGETATIVE, GrowthStage.FLOWERING],
        "base_yield_tonnes_ha": 2.5,
        "optimal_temp": (25, 35), "optimal_rainfall": (300, 500),
    },
    CropType.MAIZE: {
        "duration_days": 110, "water_requirement_mm": 550,
        "n_kg_ha": 150, "p_kg_ha": 75, "k_kg_ha": 60,
        "stages": {GrowthStage.GERMINATION: (0, 15), GrowthStage.VEGETATIVE: (15, 45),
                   GrowthStage.FLOWERING: (45, 75), GrowthStage.FRUITING: (75, 95),
                   GrowthStage.MATURITY: (95, 110)},
        "major_pests": ["stem_borer", "fall_armyworm", "cob_borer"],
        "major_diseases": ["maydis_leaf_blight", "tassel_blight", "stalk_rot"],
        "critical_stages": [GrowthStage.VEGETATIVE, GrowthStage.FLOWERING],
        "base_yield_tonnes_ha": 5.5,
        "optimal_temp": (20, 30), "optimal_rainfall": (500, 800),
    },
    CropType.CUMIN: {
        "duration_days": 120, "water_requirement_mm": 300,
        "n_kg_ha": 30, "p_kg_ha": 20, "k_kg_ha": 20,
        "stages": {GrowthStage.GERMINATION: (0, 20), GrowthStage.VEGETATIVE: (20, 60),
                   GrowthStage.FLOWERING: (60, 90), GrowthStage.FRUITING: (90, 110),
                   GrowthStage.MATURITY: (110, 120)},
        "major_pests": ["aphid", "thrips"],
        "major_diseases": ["wilt", "blight", "powdery_mildew"],
        "critical_stages": [GrowthStage.FLOWERING, GrowthStage.FRUITING],
        "base_yield_tonnes_ha": 0.6,
        "optimal_temp": (20, 30), "optimal_rainfall": (250, 400),
    },
    CropType.CASTOR: {
        "duration_days": 150, "water_requirement_mm": 500,
        "n_kg_ha": 80, "p_kg_ha": 40, "k_kg_ha": 40,
        "stages": {GrowthStage.GERMINATION: (0, 20), GrowthStage.VEGETATIVE: (20, 60),
                   GrowthStage.FLOWERING: (60, 100), GrowthStage.FRUITING: (100, 130),
                   GrowthStage.MATURITY: (130, 150)},
        "major_pests": ["semilooper", "spodoptera", "whitefly"],
        "major_diseases": ["wilt", "root_rot", "leaf_spot"],
        "critical_stages": [GrowthStage.FLOWERING, GrowthStage.FRUITING],
        "base_yield_tonnes_ha": 1.8,
        "optimal_temp": (25, 35), "optimal_rainfall": (500, 750),
    },
    CropType.SESAME: {
        "duration_days": 90, "water_requirement_mm": 400,
        "n_kg_ha": 40, "p_kg_ha": 20, "k_kg_ha": 20,
        "stages": {GrowthStage.GERMINATION: (0, 15), GrowthStage.VEGETATIVE: (15, 35),
                   GrowthStage.FLOWERING: (35, 60), GrowthStage.FRUITING: (60, 80),
                   GrowthStage.MATURITY: (80, 90)},
        "major_pests": ["leaf_webber", "capsule_borer", "gall_fly"],
        "major_diseases": ["phyllody", "root_rot", "leaf_spot"],
        "critical_stages": [GrowthStage.FLOWERING, GrowthStage.FRUITING],
        "base_yield_tonnes_ha": 0.8,
        "optimal_temp": (25, 35), "optimal_rainfall": (500, 700),
    },
}


SOIL_IRRIGATION_FACTORS = {
    (SoilType.BLACK_COTTON, IrrigationSource.CANAL): 1.0,
    (SoilType.BLACK_COTTON, IrrigationSource.BOREWELL): 1.1,
    (SoilType.BLACK_COTTON, IrrigationSource.RAINFED): 0.6,
    (SoilType.ALLUVIAL, IrrigationSource.CANAL): 1.0,
    (SoilType.ALLUVIAL, IrrigationSource.BOREWELL): 1.0,
    (SoilType.ALLUVIAL, IrrigationSource.RAINFED): 0.7,
    (SoilType.RED_LOAM, IrrigationSource.CANAL): 0.9,
    (SoilType.RED_LOAM, IrrigationSource.BOREWELL): 1.0,
    (SoilType.RED_LOAM, IrrigationSource.RAINFED): 0.5,
    (SoilType.SANDY_LOAM, IrrigationSource.CANAL): 0.8,
    (SoilType.SANDY_LOAM, IrrigationSource.BOREWELL): 0.9,
    (SoilType.SANDY_LOAM, IrrigationSource.RAINFED): 0.4,
    (SoilType.CLAY, IrrigationSource.CANAL): 1.0,
    (SoilType.CLAY, IrrigationSource.BOREWELL): 1.0,
    (SoilType.CLAY, IrrigationSource.RAINFED): 0.6,
    (SoilType.SALINE, IrrigationSource.CANAL): 0.8,
    (SoilType.SALINE, IrrigationSource.BOREWELL): 0.9,
    (SoilType.SALINE, IrrigationSource.RAINFED): 0.3,
    (SoilType.ALKALINE, IrrigationSource.CANAL): 0.8,
    (SoilType.ALKALINE, IrrigationSource.BOREWELL): 0.9,
    (SoilType.ALKALINE, IrrigationSource.RAINFED): 0.3,
}


async def get_crop_data(crop_type: CropType) -> Dict[str, Any]:
    return CROP_DATA.get(crop_type, CROP_DATA[CropType.COTTON])


async def get_growth_stage(crop_type: CropType, days_after_sowing: int) -> GrowthStage:
    crop_data = await get_crop_data(crop_type)
    stages = crop_data["stages"]
    for stage, (start, end) in stages.items():
        if start <= days_after_sowing < end:
            return stage
    return GrowthStage.MATURITY


async def get_days_after_sowing(sowing_date: date) -> int:
    return (date.today() - sowing_date).days


async def calculate_et0(temp_max: float, temp_min: float, humidity: float, wind_speed: float) -> float:
    t_mean = (temp_max + temp_min) / 2
    t_diff = temp_max - temp_min
    et0 = 0.0023 * (t_mean + 17.8) * math.sqrt(t_diff) * (100 - humidity) / 100
    return max(0, et0)


async def calculate_crop_water_need(crop_type: CropType, growth_stage: GrowthStage, et0: float) -> float:
    crop_data = await get_crop_data(crop_type)
    kc_values = {
        GrowthStage.GERMINATION: 0.4, GrowthStage.VEGETATIVE: 0.8,
        GrowthStage.FLOWERING: 1.1, GrowthStage.FRUITING: 1.05,
        GrowthStage.MATURITY: 0.7, GrowthStage.HARVEST: 0.3,
    }
    kc = kc_values.get(growth_stage, 1.0)
    return et0 * kc


async def get_real_weather_data(location: Location, days: int = 7) -> List[Dict]:
    client = get_weather_client()
    return await client.get_forecast(location.latitude, location.longitude, days)


async def get_satellite_data(
    location: Location, crop_type: CropType, area_hectares: float, 
    sowing_date: date, days_back: int = 30
) -> List[Dict]:
    client = get_satellite_client()
    return await client.get_field_data(
        location.latitude, location.longitude, area_hectares,
        crop_type, sowing_date, days_back
    )


async def get_soil_data(
    location: Location, survey_number: Optional[str] = None
) -> Dict[str, Any]:
    client = get_soil_client()
    soil = await client.get_soil_health(
        location.latitude, location.longitude, survey_number,
        location.village, location.district, location.state
    )
    return {
        "ph": soil.ph, "ec_ds_m": soil.ec_ds_m,
        "organic_carbon_percent": soil.organic_carbon_percent,
        "available_n_kg_ha": soil.available_n_kg_ha,
        "available_p_kg_ha": soil.available_p_kg_ha,
        "available_k_kg_ha": soil.available_k_kg_ha,
        "sulphur_ppm": soil.sulphur_ppm,
        "zinc_ppm": soil.zinc_ppm,
        "boron_ppm": soil.boron_ppm,
        "iron_ppm": soil.iron_ppm,
        "manganese_ppm": soil.manganese_ppm,
        "copper_ppm": soil.copper_ppm,
        "soil_type": soil.soil_type,
    }


async def get_irrigation_advisory(
    crop_type: CropType,
    growth_stage: GrowthStage,
    soil_type: Optional[SoilType],
    irrigation_source: Optional[IrrigationSource],
    last_irrigation_days_ago: Optional[int],
    rainfall_mm: float,
    et0: float,
    days_after_sowing: int,
    location: Location,
    area_hectares: float,
    irrigation_method: str = "drip",
) -> Dict[str, Any]:
    crop_data = await get_crop_data(crop_type)
    crop_et = await calculate_crop_water_need(crop_type, growth_stage, et0)
    
    soil_irr_factor = 1.0
    if soil_type and irrigation_source:
        soil_irr_factor = SOIL_IRRIGATION_FACTORS.get((soil_type, irrigation_source), 1.0)
    
    effective_rainfall = rainfall_mm * 0.7
    net_irrigation_need = max(0, crop_et - effective_rainfall) * soil_irr_factor
    
    critical_stage = growth_stage in crop_data.get("critical_stages", [])
    
    if critical_stage:
        priority = AdvisoryPriority.HIGH
        interval_days = 3
    elif growth_stage in [GrowthStage.FLOWERING, GrowthStage.FRUITING]:
        priority = AdvisoryPriority.HIGH
        interval_days = 4
    elif growth_stage == GrowthStage.VEGETATIVE:
        priority = AdvisoryPriority.MEDIUM
        interval_days = 5
    else:
        priority = AdvisoryPriority.LOW
        interval_days = 7
    
    if last_irrigation_days_ago is not None and last_irrigation_days_ago < interval_days:
        urgency = "maintain_schedule"
    elif net_irrigation_need > 5:
        urgency = "irrigate_soon"
    else:
        urgency = "monitor"
    
    ml_manager = get_model_manager()
    
    soil_data = await get_soil_data(location)
    weather_data = await get_real_weather_data(location, 7)
    satellite_data = await get_satellite_data(location, crop_type, area_hectares, 
                                               date.today() - timedelta(days=days_after_sowing), 14)
    
    et0_forecast = []
    for w in weather_data[:7]:
        et0_day = await calculate_et0(
            w.get("temp_max_c", 30), w.get("temp_min_c", 20),
            w.get("humidity_percent", 60), w.get("wind_speed_kmph", 10)
        )
        et0_forecast.append(et0_day)
    
    irrigation_rec = await ml_manager.optimize_irrigation(
        crop=crop_type,
        growth_stage=growth_stage,
        soil_type=soil_type or SoilType.ALLUVIAL,
        soil_moisture=satellite_data[0].get("soil_moisture_percent", 50) if satellite_data else 50,
        weather_forecast=weather_data,
        et0_forecast=et0_forecast,
        area_hectares=area_hectares,
        irrigation_method=irrigation_method,
        water_cost_per_m3=2.0,
    )
    
    interval_days = irrigation_rec.get("interval_days", interval_days)
    depth_mm = irrigation_rec.get("depth_mm", net_irrigation_need)
    schedule = irrigation_rec.get("schedule", urgency)
    volume_m3 = irrigation_rec.get("volume_m3_per_ha", depth_mm * 10)
    
    return {
        "category": AdvisoryCategory.IRRIGATION,
        "priority": priority.value,
        "title": f"Irrigation advisory for {crop_type.value} at {growth_stage.value}",
        "description": f"Crop ET: {crop_et:.1f} mm/day. Effective rainfall: {effective_rainfall:.1f} mm. Net need: {net_irrigation_need:.1f} mm. ML schedule: {schedule}.",
        "confidence": ConfidenceLevel.HIGH.value if critical_stage else ConfidenceLevel.MEDIUM.value,
        "action_items": [
            f"ML recommended: Irrigate every {interval_days} days",
            f"Apply {depth_mm:.0f} mm ({volume_m3:.0f} m³/ha) per irrigation",
            "Check soil moisture at 30 cm depth before irrigation",
        ],
        "timeline_days": interval_days,
        "estimated_cost_inr": irrigation_rec.get("cost_estimate_inr", net_irrigation_need * 0.5 * 1000 * area_hectares),
        "materials_needed": ["Irrigation water", "Flow meter"] if net_irrigation_need > 0 else [],
        "precautions": [
            "Avoid waterlogging", "Irrigate early morning (4-6 AM)",
            "Ensure proper drainage", "Use mulch to reduce evaporation",
        ],
        "weather_dependent": True,
        "details": {
            **irrigation_rec,
            "crop_et_mm_day": round(crop_et, 1),
            "effective_rainfall_mm": round(effective_rainfall, 1),
            "net_need_mm": round(net_irrigation_need, 1),
            "soil_irr_factor": soil_irr_factor,
            "critical_stage": critical_stage,
            "ml_schedule": schedule,
            "ml_confidence": irrigation_rec.get("confidence", 0.8),
        }
    }


async def get_fertilizer_advisory(
    crop_type: CropType,
    growth_stage: GrowthStage,
    area_hectares: float,
    soil_test: Optional[Dict[str, float]],
    previous_applications: Optional[List[Dict]] = None,
    location: Optional[Location] = None,
) -> Dict[str, Any]:
    crop_data = await get_crop_data(crop_type)
    
    if soil_test is None and location:
        soil_test = await get_soil_data(location)
    
    ml_manager = get_model_manager()
    
    fertilizer_prices = {
        "Urea": 6.0, "DAP": 24.0, "MOP": 18.0,
        "Gypsum": 3.0, "Zinc_Sulphate": 45.0,
    }
    
    target_yield = crop_data.get("base_yield_tonnes_ha", 2.5) * 1.2
    
    ml_result = await ml_manager.optimize_fertilizer(
        crop=crop_type,
        growth_stage=growth_stage,
        soil_test=soil_test or {},
        target_yield=target_yield,
        area_hectares=area_hectares,
        fertilizer_prices=fertilizer_prices,
        previous_applications=previous_applications or [],
    )
    
    return {
        "category": AdvisoryCategory.FERTILIZER,
        "priority": AdvisoryPriority.HIGH.value if ml_result.get("total_cost_inr", 0) > 5000 else AdvisoryPriority.MEDIUM.value,
        "title": f"Fertilizer recommendation for {crop_type.value} at {growth_stage.value}",
        "description": f"ML-optimized NPK: {ml_result.get('recommended_npk_kg_ha', {})}. Stage dose: {ml_result.get('stage_dose_kg_ha', {})}. Cost: ₹{ml_result.get('total_cost_inr', 0):.0f}/ha",
        "confidence": ConfidenceLevel.HIGH.value if soil_test else ConfidenceLevel.MEDIUM.value,
        "action_items": [
            f"Apply {f['dose_kg_total']} kg {f['fertilizer']} per hectare" for f in ml_result.get("fertilizers", [])
        ],
        "timeline_days": 3,
        "estimated_cost_inr": ml_result.get("total_cost_inr", 0) * area_hectares,
        "materials_needed": [f['fertilizer'] for f in ml_result.get("fertilizers", [])],
        "precautions": [
            "Apply fertilizers in moist soil", "Avoid contact with seeds/seedlings",
            "Follow split application schedule", "Use soil test based recommendations",
            "Incorporate organic alternatives where possible",
        ],
        "weather_dependent": False,
        "details": ml_result,
    }


async def get_pest_disease_advisory(
    crop_type: CropType,
    growth_stage: GrowthStage,
    observed_pests: Optional[List[str]] = None,
    weather_forecast: Optional[List[Dict]] = None,
    location: Optional[Location] = None,
    area_hectares: float = 1.0,
    sowing_date: Optional[date] = None,
) -> List[Dict[str, Any]]:
    crop_data = await get_crop_data(crop_type)
    
    if weather_forecast is None and location:
        weather_forecast = await get_real_weather_data(location, 7)
    
    if weather_forecast is None:
        weather_forecast = []
    
    satellite_data = []
    pest_counts = {}
    if location and sowing_date:
        satellite_data = await get_satellite_data(
            location, crop_type, area_hectares, sowing_date, 14
        )
        pest_counts = {
            "whitefly": 3, "thrips": 5, "aphid": 8, "jassid": 2,
        }
    
    ml_manager = get_model_manager()
    disease_risks = await ml_manager.assess_disease_risk(
        crop=crop_type,
        growth_stage=growth_stage,
        weather_forecast=weather_forecast,
        satellite_data=satellite_data,
        field_history={},
        symptoms_observed=observed_pests or [],
    )
    
    advisories = []
    
    for risk in disease_risks:
        advisories.append({
            "category": AdvisoryCategory.PEST_DISEASE.value,
            "priority": {"critical": "high", "high": "high", "medium": "medium", "low": "low"}.get(risk.risk_level, "medium"),
            "title": f"{risk.disease.replace('_', ' ').title()} risk: {risk.risk_level.upper()}",
            "description": f"Probability: {risk.probability*100:.0f}%. Peak risk in {risk.days_to_peak} days. Weather trigger: {risk.weather_trigger}",
            "confidence": ConfidenceLevel.HIGH.value if risk.probability > 0.6 else ConfidenceLevel.MEDIUM.value,
            "action_items": [risk.recommended_action, "Monitor daily", "Consult KVK if symptoms appear"],
            "timeline_days": risk.days_to_peak,
            "estimated_cost_inr": 500,
            "materials_needed": ["Recommended pesticide/fungicide", "Sprayer", "PPE"],
            "precautions": [
                "Follow pre-harvest interval", "Rotate chemical groups",
                "Apply in morning/evening", "Use recommended dose only",
            ],
            "pest_disease_name": risk.disease,
            "severity": risk.risk_level,
            "threshold_reached": risk.probability > 0.5,
            "details": {
                "disease": risk.disease, "crop": crop_type.value,
                "stage": growth_stage.value, "probability": risk.probability,
                "days_to_peak": risk.days_to_peak,
                "weather_trigger": risk.weather_trigger,
            }
        })
    
    relevant_pests = crop_data["major_pests"]
    if observed_pests:
        relevant_pests = [p for p in relevant_pests if any(op in p.lower() for op in observed_pests)]
    
    for pest in relevant_pests[:2]:
        if any(a.get("pest_disease_name") == pest for a in advisories):
            continue
        advisories.append({
            "category": AdvisoryCategory.PEST_DISEASE.value,
            "priority": "medium",
            "title": f"{pest.replace('_', ' ').title()} monitoring for {crop_type.value}",
            "description": f"{pest.replace('_', ' ').title()} is a major pest in {crop_type.value} at {growth_stage.value} stage. Scout regularly.",
            "confidence": ConfidenceLevel.MEDIUM.value,
            "action_items": [
                f"Scout field for {pest.replace('_', ' ')} symptoms weekly",
                "Install pheromone traps if available",
                "Apply neem oil 5% @ 3 ml/L as preventive",
                "Consult local KVK for specific pesticide if threshold crossed",
            ],
            "timeline_days": 7,
            "estimated_cost_inr": 500,
            "materials_needed": ["Neem oil", "Pheromone traps", "Sticky traps"],
            "precautions": ["Follow pre-harvest interval", "Rotate insecticide groups", "Preserve natural enemies"],
            "pest_disease_name": pest,
            "severity": "moderate",
            "threshold_reached": False,
            "details": {"pest": pest, "crop": crop_type.value, "stage": growth_stage.value},
        })
    
    return advisories


async def get_weather_based_advice(weather_forecast: List[Dict]) -> List[str]:
    advice = []
    for w in weather_forecast[:3]:
        day = w.get("date", "")
        rainfall = w.get("rainfall_mm", 0)
        humidity = w.get("humidity_percent", 0)
        temp_max = w.get("temp_max_c", 0)
        temp_min = w.get("temp_min_c", 0)
        
        if rainfall > 20:
            advice.append(f"{day}: Heavy rain ({rainfall:.0f}mm) - ensure drainage, delay spraying")
        elif rainfall > 5:
            advice.append(f"{day}: Light rain ({rainfall:.0f}mm) - good for soil moisture")
        else:
            advice.append(f"{day}: No significant rain - plan irrigation if needed")
        
        if humidity > 85:
            advice.append(f"{day}: High humidity ({humidity:.0f}%) - increase disease monitoring")
        
        if temp_max > 40:
            advice.append(f"{day}: High temp ({temp_max:.0f}°C) - increase irrigation frequency")
        elif temp_max < 15:
            advice.append(f"{day}: Low temp ({temp_max:.0f}°C) - protect sensitive crops")
    
    return advice


async def get_next_scheduled_activities(
    crop_type: CropType, growth_stage: GrowthStage, days_after_sowing: int
) -> List[Dict]:
    crop_data = await get_crop_data(crop_type)
    activities = []
    current_stage_end = crop_data["stages"].get(growth_stage, (0, 0))[1]
    days_to_next_stage = current_stage_end - days_after_sowing
    
    if growth_stage == GrowthStage.GERMINATION:
        activities.append({"activity": "Gap filling and thinning", "days_from_now": 5, "description": "Fill gaps where seeds didn't germinate, thin excess plants"})
        activities.append({"activity": "First weeding", "days_from_now": 15, "description": "Remove weeds before they compete with crop"})
    elif growth_stage == GrowthStage.VEGETATIVE:
        activities.append({"activity": "Top dressing nitrogen", "days_from_now": 10, "description": "Apply 2nd split of nitrogen fertilizer"})
        activities.append({"activity": "Earthing up", "days_from_now": 20, "description": "Support plants and suppress weeds"})
    elif growth_stage == GrowthStage.FLOWERING:
        activities.append({"activity": "Pollination support", "days_from_now": 5, "description": "Ensure bee activity, avoid spraying during peak pollination"})
        activities.append({"activity": "Potash application", "days_from_now": 15, "description": "Apply potassium for fruit/grain development"})
    elif growth_stage == GrowthStage.FRUITING:
        activities.append({"activity": "Fruit/borer monitoring", "days_from_now": 3, "description": "Check for pest damage on developing produce"})
    
    if days_to_next_stage > 0 and days_to_next_stage <= 15:
        next_stage = None
        for stage, (start, end) in crop_data["stages"].items():
            if start == current_stage_end:
                next_stage = stage
                break
        if next_stage:
            activities.append({
                "activity": f"Prepare for {next_stage.value} stage",
                "days_from_now": days_to_next_stage,
                "description": f"Crop will enter {next_stage.value} in {days_to_next_stage} days"
            })
    
    return activities


def generate_sms_summary(advisories: List[Dict], language: str = "Gujlish") -> str:
    if not advisories:
        return "No advisories at this time. Check again tomorrow."
    
    priority_order = {"high": 0, "medium": 1, "low": 2}
    sorted_adv = sorted(advisories, key=lambda x: priority_order.get(x.get("priority", "low"), 3))
    top = sorted_adv[:2]
    
    parts = []
    for adv in top:
        cat = adv.get("category", "")
        if cat == "irrigation": parts.append("Irrigate")
        elif cat == "fertilizer": parts.append("Fertilizer")
        elif cat == "pest_disease": parts.append("Pest alert")
        else: parts.append(adv.get("title", "")[:15])
    
    action = top[0].get('action_items', [''])[0][:60] if top[0].get('action_items') else ""
    return f"{', '.join(parts)}: {action}..."


async def estimate_yield(
    crop_type: CropType, area_hectares: float, growth_stage: GrowthStage,
    management_score: float = 0.7, location: Optional[Location] = None,
    soil_test: Optional[Dict] = None, sowing_date: Optional[date] = None,
) -> Dict[str, Any]:
    crop_data = await get_crop_data(crop_type)
    
    ml_manager = get_model_manager()
    
    weather_history = []
    satellite_data = []
    if location:
        weather_history = await get_real_weather_data(location, 30)
        if sowing_date:
            satellite_data = await get_satellite_data(location, crop_type, area_hectares, sowing_date, 30)
    
    if soil_test is None and location:
        soil_test = await get_soil_data(location)
    
    pest_pressure = 0.1
    disease_pressure = 0.1
    if satellite_data:
        health_scores = [d.get("crop_health_score", 70) for d in satellite_data]
        if health_scores:
            avg_health = sum(health_scores) / len(health_scores)
            if avg_health < 50:
                pest_pressure = 0.3
                disease_pressure = 0.3
            elif avg_health < 70:
                pest_pressure = 0.15
                disease_pressure = 0.15
    
    ndvi_avg = 0.6
    if satellite_data:
        ndvi_vals = [d.get("ndvi", 0.6) for d in satellite_data]
        if ndvi_vals:
            ndvi_avg = sum(ndvi_vals) / len(ndvi_vals)
    
    temp_avg = 30
    rainfall_total = 200
    humidity_avg = 60
    if weather_history:
        temp_avg = sum(d.get("temp_max_c", 30) for d in weather_history) / len(weather_history)
        rainfall_total = sum(d.get("rainfall_mm", 0) for d in weather_history)
        humidity_avg = sum(d.get("humidity_percent", 60) for d in weather_history) / len(weather_history)
    
    yield_pred = await ml_manager.predict_yield(
        crop=crop_type,
        area_hectares=area_hectares,
        soil_type=soil_test.get("soil_type", SoilType.ALLUVIAL) if soil_test else SoilType.ALLUVIAL,
        sowing_date=sowing_date or date.today(),
        location=location,
        soil_data=soil_test or {},
        weather_history=weather_history,
        satellite_data=satellite_data,
        management={
            "irrigation_count": 5, "fertilizer_n": 100, "fertilizer_p": 50, "fertilizer_k": 40,
            "pest_pressure": pest_pressure, "disease_pressure": disease_pressure,
        }
    )
    
    return {
        "predicted_yield_tonnes_ha": yield_pred.get("predicted_yield_tonnes_ha", crop_data.get("base_yield_tonnes_ha", 2.0)),
        "total_yield_tonnes": round(yield_pred.get("predicted_yield_tonnes_ha", 2.0) * area_hectares, 2),
        "confidence_interval": yield_pred.get("confidence_interval", (1.5, 3.0)),
        "confidence_level": yield_pred.get("confidence_level", 0.75),
        "key_factors": yield_pred.get("key_factors", {}),
        "risk_factors": yield_pred.get("risk_factors", []),
        "recommendation": yield_pred.get("recommendation", "Maintain current practices"),
        "model_type": yield_pred.get("model_type", "rule_based"),
    }