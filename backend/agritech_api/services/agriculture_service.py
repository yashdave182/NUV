import random
import math
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from ..schemas import (
    CropType, SoilType, IrrigationSource, WeatherCondition,
    AdvisoryCategory, AdvisoryPriority, ConfidenceLevel,
    GrowthStage, Season, FertilizerType, PestSeverity
)


CROP_DATA = {
    CropType.COTTON: {
        "duration_days": 180,
        "water_requirement_mm": 700,
        "n_kg_ha": 120,
        "p_kg_ha": 60,
        "k_kg_ha": 60,
        "stages": {
            GrowthStage.GERMINATION: (0, 15),
            GrowthStage.VEGETATIVE: (15, 60),
            GrowthStage.FLOWERING: (60, 120),
            GrowthStage.FRUITING: (120, 160),
            GrowthStage.MATURITY: (160, 180),
        },
        "major_pests": ["pink_bollworm", "whitefly", "aphid", "jassid"],
        "major_diseases": ["leaf_curl", "root_rot", "boll_rot"],
        "critical_stages": [GrowthStage.FLOWERING, GrowthStage.FRUITING],
    },
    CropType.GROUNDNUT: {
        "duration_days": 120,
        "water_requirement_mm": 500,
        "n_kg_ha": 20,
        "p_kg_ha": 40,
        "k_kg_ha": 40,
        "stages": {
            GrowthStage.GERMINATION: (0, 15),
            GrowthStage.VEGETATIVE: (15, 45),
            GrowthStage.FLOWERING: (45, 75),
            GrowthStage.FRUITING: (75, 105),
            GrowthStage.MATURITY: (105, 120),
        },
        "major_pests": ["leaf_miner", "spodoptera", "thrips", "aphid"],
        "major_diseases": ["tikka", "rust", "stem_rot", "bud_necrosis"],
        "critical_stages": [GrowthStage.FLOWERING, GrowthStage.FRUITING],
    },
    CropType.WHEAT: {
        "duration_days": 130,
        "water_requirement_mm": 450,
        "n_kg_ha": 120,
        "p_kg_ha": 60,
        "k_kg_ha": 40,
        "stages": {
            GrowthStage.GERMINATION: (0, 20),
            GrowthStage.VEGETATIVE: (20, 60),
            GrowthStage.FLOWERING: (60, 85),
            GrowthStage.FRUITING: (85, 110),
            GrowthStage.MATURITY: (110, 130),
        },
        "major_pests": ["aphid", "pink_borer", "termite"],
        "major_diseases": ["yellow_rust", "brown_rust", "loose_smut", "karnal_bunt"],
        "critical_stages": [GrowthStage.FLOWERING, GrowthStage.FRUITING],
    },
    CropType.BAJRA: {
        "duration_days": 90,
        "water_requirement_mm": 400,
        "n_kg_ha": 80,
        "p_kg_ha": 40,
        "k_kg_ha": 40,
        "stages": {
            GrowthStage.GERMINATION: (0, 15),
            GrowthStage.VEGETATIVE: (15, 40),
            GrowthStage.FLOWERING: (40, 60),
            GrowthStage.FRUITING: (60, 80),
            GrowthStage.MATURITY: (80, 90),
        },
        "major_pests": ["shoot_fly", "stem_borer", "earhead_worm"],
        "major_diseases": ["downy_mildew", "ergot", "smut"],
        "critical_stages": [GrowthStage.VEGETATIVE, GrowthStage.FLOWERING],
    },
    CropType.MAIZE: {
        "duration_days": 110,
        "water_requirement_mm": 550,
        "n_kg_ha": 150,
        "p_kg_ha": 75,
        "k_kg_ha": 60,
        "stages": {
            GrowthStage.GERMINATION: (0, 15),
            GrowthStage.VEGETATIVE: (15, 45),
            GrowthStage.FLOWERING: (45, 75),
            GrowthStage.FRUITING: (75, 95),
            GrowthStage.MATURITY: (95, 110),
        },
        "major_pests": ["stem_borer", "fall_armyworm", "cob_borer"],
        "major_diseases": ["maydis_leaf_blight", "tassel_blight", "stalk_rot"],
        "critical_stages": [GrowthStage.VEGETATIVE, GrowthStage.FLOWERING],
    },
    CropType.CUMIN: {
        "duration_days": 120,
        "water_requirement_mm": 300,
        "n_kg_ha": 30,
        "p_kg_ha": 20,
        "k_kg_ha": 20,
        "stages": {
            GrowthStage.GERMINATION: (0, 20),
            GrowthStage.VEGETATIVE: (20, 60),
            GrowthStage.FLOWERING: (60, 90),
            GrowthStage.FRUITING: (90, 110),
            GrowthStage.MATURITY: (110, 120),
        },
        "major_pests": ["aphid", "thrips"],
        "major_diseases": ["wilt", "blight", "powdery_mildew"],
        "critical_stages": [GrowthStage.FLOWERING, GrowthStage.FRUITING],
    },
    CropType.CASTOR: {
        "duration_days": 150,
        "water_requirement_mm": 500,
        "n_kg_ha": 80,
        "p_kg_ha": 40,
        "k_kg_ha": 40,
        "stages": {
            GrowthStage.GERMINATION: (0, 20),
            GrowthStage.VEGETATIVE: (20, 60),
            GrowthStage.FLOWERING: (60, 100),
            GrowthStage.FRUITING: (100, 130),
            GrowthStage.MATURITY: (130, 150),
        },
        "major_pests": ["semilooper", "spodoptera", "whitefly"],
        "major_diseases": ["wilt", "root_rot", "leaf_spot"],
        "critical_stages": [GrowthStage.FLOWERING, GrowthStage.FRUITING],
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


def get_crop_data(crop_type: CropType) -> Dict[str, Any]:
    return CROP_DATA.get(crop_type, CROP_DATA[CropType.COTTON])


def get_growth_stage(crop_type: CropType, days_after_sowing: int) -> GrowthStage:
    crop_data = get_crop_data(crop_type)
    stages = crop_data["stages"]
    for stage, (start, end) in stages.items():
        if start <= days_after_sowing < end:
            return stage
    return GrowthStage.MATURITY


def get_days_after_sowing(sowing_date: date) -> int:
    return (date.today() - sowing_date).days


def calculate_et0(temp_max: float, temp_min: float, humidity: float, wind_speed: float) -> float:
    """Simplified reference evapotranspiration calculation (Hargreaves method)"""
    t_mean = (temp_max + temp_min) / 2
    t_diff = temp_max - temp_min
    et0 = 0.0023 * (t_mean + 17.8) * math.sqrt(t_diff) * (100 - humidity) / 100
    return max(0, et0)


def calculate_crop_water_need(crop_type: CropType, growth_stage: GrowthStage, et0: float) -> float:
    crop_data = get_crop_data(crop_type)
    kc_values = {
        GrowthStage.GERMINATION: 0.4,
        GrowthStage.VEGETATIVE: 0.8,
        GrowthStage.FLOWERING: 1.1,
        GrowthStage.FRUITING: 1.05,
        GrowthStage.MATURITY: 0.7,
        GrowthStage.HARVEST: 0.3,
    }
    kc = kc_values.get(growth_stage, 1.0)
    return et0 * kc


def get_irrigation_advisory(
    crop_type: CropType,
    growth_stage: GrowthStage,
    soil_type: Optional[SoilType],
    irrigation_source: Optional[IrrigationSource],
    last_irrigation_days_ago: Optional[int],
    rainfall_mm: float,
    et0: float,
    days_after_sowing: int
) -> Dict[str, Any]:
    crop_data = get_crop_data(crop_type)
    crop_et = calculate_crop_water_need(crop_type, growth_stage, et0)
    
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
    
    return {
        "category": AdvisoryCategory.IRRIGATION,
        "priority": priority.value,
        "title": f"Irrigation advisory for {crop_type.value} at {growth_stage.value}",
        "description": f"Crop water need: {crop_et:.1f} mm/day. Effective rainfall: {effective_rainfall:.1f} mm. Net irrigation needed: {net_irrigation_need:.1f} mm.",
        "confidence": ConfidenceLevel.HIGH.value if critical_stage else ConfidenceLevel.MEDIUM.value,
        "action_items": [
            f"Irrigate every {interval_days} days" if urgency != "monitor" else "Monitor soil moisture",
            f"Apply {net_irrigation_need:.0f} mm water per irrigation" if net_irrigation_need > 0 else "No irrigation needed if rain continues",
            "Check soil moisture at 15-30 cm depth before irrigation",
        ],
        "timeline_days": interval_days,
        "estimated_cost_inr": net_irrigation_need * 0.5 * 1000,
        "materials_needed": ["Irrigation water", "Flow meter"] if net_irrigation_need > 0 else [],
        "precautions": [
            "Avoid waterlogging",
            "Irrigate early morning or evening",
            "Ensure proper drainage",
        ],
        "weather_dependent": True,
        "details": {
            "crop_et_mm_day": round(crop_et, 1),
            "effective_rainfall_mm": round(effective_rainfall, 1),
            "net_need_mm": round(net_irrigation_need, 1),
            "soil_irr_factor": soil_irr_factor,
            "critical_stage": critical_stage,
            "urgency": urgency,
        }
    }


def get_fertilizer_advisory(
    crop_type: CropType,
    growth_stage: GrowthStage,
    area_hectares: float,
    soil_test: Optional[Dict[str, float]],
    previous_applications: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    crop_data = get_crop_data(crop_type)
    
    n_rec = crop_data["n_kg_ha"]
    p_rec = crop_data["p_kg_ha"]
    k_rec = crop_data["k_kg_ha"]
    
    if soil_test:
        if soil_test.get("available_n", 0) > 280:
            n_rec *= 0.8
        elif soil_test.get("available_n", 0) < 140:
            n_rec *= 1.2
        
        if soil_test.get("available_p", 0) > 25:
            p_rec *= 0.8
        elif soil_test.get("available_p", 0) < 10:
            p_rec *= 1.3
        
        if soil_test.get("available_k", 0) > 250:
            k_rec *= 0.8
        elif soil_test.get("available_k", 0) < 120:
            k_rec *= 1.2
        
        if soil_test.get("zn_ppm", 1) < 0.6:
            n_rec += 25
        if soil_test.get("fe_ppm", 1) < 4.5:
            n_rec += 20
    
    stage_split = {
        GrowthStage.GERMINATION: {"n": 0.2, "p": 0.5, "k": 0.2},
        GrowthStage.VEGETATIVE: {"n": 0.4, "p": 0.3, "k": 0.3},
        GrowthStage.FLOWERING: {"n": 0.3, "p": 0.1, "k": 0.3},
        GrowthStage.FRUITING: {"n": 0.1, "p": 0.1, "k": 0.2},
        GrowthStage.MATURITY: {"n": 0, "p": 0, "k": 0},
    }
    
    split = stage_split.get(growth_stage, {"n": 0.25, "p": 0.25, "k": 0.25})
    
    n_dose = n_rec * split["n"]
    p_dose = p_rec * split["p"]
    k_dose = k_rec * split["k"]
    
    fertilizers = []
    if n_dose > 0:
        urea_kg = (n_dose / 0.46) * area_hectares
        fertilizers.append({
            "fertilizer": FertilizerType.UREA.value,
            "dose_kg_per_ha": round(n_dose / 0.46, 1),
            "dose_kg_total": round(urea_kg, 1),
            "application_stage": growth_stage.value,
            "application_method": "Broadcast + incorporation" if growth_stage == GrowthStage.GERMINATION else "Top dressing",
            "cost_per_kg": 6.0,
            "total_cost": round(urea_kg * 6.0, 0),
            "nutrient_supplied": {"N": round(n_dose, 1)},
        })
    
    if p_dose > 0:
        dap_kg = (p_dose / 0.18) * area_hectares
        fertilizers.append({
            "fertilizer": FertilizerType.DAP.value,
            "dose_kg_per_ha": round(p_dose / 0.18, 1),
            "dose_kg_total": round(dap_kg, 1),
            "application_stage": growth_stage.value,
            "application_method": "Basal placement",
            "cost_per_kg": 24.0,
            "total_cost": round(dap_kg * 24.0, 0),
            "nutrient_supplied": {"P": round(p_dose, 1), "N": round(p_dose / 0.18 * 0.18, 1)},
        })
    
    if k_dose > 0:
        mop_kg = (k_dose / 0.60) * area_hectares
        fertilizers.append({
            "fertilizer": FertilizerType.MOP.value,
            "dose_kg_per_ha": round(k_dose / 0.60, 1),
            "dose_kg_total": round(mop_kg, 1),
            "application_stage": growth_stage.value,
            "application_method": "Broadcast",
            "cost_per_kg": 18.0,
            "total_cost": round(mop_kg * 18.0, 0),
            "nutrient_supplied": {"K": round(k_dose, 1)},
        })
    
    if soil_test and soil_test.get("zn_ppm", 1) < 0.6:
        zinc_kg = 25 * area_hectares
        fertilizers.append({
            "fertilizer": FertilizerType.ZINC_SULPHATE.value,
            "dose_kg_per_ha": 25,
            "dose_kg_total": round(zinc_kg, 1),
            "application_stage": "Basal",
            "application_method": "Soil application",
            "cost_per_kg": 45.0,
            "total_cost": round(zinc_kg * 45.0, 0),
            "nutrient_supplied": {"Zn": 25 * 0.33},
        })
    
    total_cost = sum(f["total_cost"] for f in fertilizers)
    
    return {
        "category": AdvisoryCategory.FERTILIZER,
        "priority": AdvisoryPriority.HIGH.value if n_dose + p_dose + k_dose > 10 else AdvisoryPriority.MEDIUM.value,
        "title": f"Fertilizer recommendation for {crop_type.value} at {growth_stage.value}",
        "description": f"Recommended N:P:K = {n_rec}:{p_rec}:{k_rec} kg/ha. Current stage split: N={n_dose:.1f}, P={p_dose:.1f}, K={k_dose:.1f} kg/ha",
        "confidence": ConfidenceLevel.HIGH.value if soil_test else ConfidenceLevel.MEDIUM.value,
        "action_items": [
            f"Apply {f['dose_kg_total']} kg {f['fertilizer']} per hectare" for f in fertilizers
        ],
        "timeline_days": 3,
        "estimated_cost_inr": total_cost,
        "materials_needed": [f['fertilizer'] for f in fertilizers],
        "precautions": [
            "Apply fertilizers in moist soil",
            "Avoid contact with seeds/seedlings",
            "Follow split application schedule",
            "Use soil test based recommendations",
        ],
        "weather_dependent": False,
        "details": {
            "recommended_npk": {"N": n_rec, "P": p_rec, "K": k_rec},
            "stage_dose": {"N": n_dose, "P": p_dose, "K": k_dose},
            "fertilizers": fertilizers,
            "total_cost_inr": total_cost,
        }
    }


def get_pest_disease_advisory(
    crop_type: CropType,
    growth_stage: GrowthStage,
    observed_pests: Optional[List[str]] = None,
    weather_forecast: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    crop_data = get_crop_data(crop_type)
    
    relevant_pests = crop_data["major_pests"]
    relevant_diseases = crop_data["major_diseases"]
    
    if observed_pests:
        relevant_pests = [p for p in relevant_pests if any(op in p.lower() for op in observed_pests)]
    
    risk_level = PestSeverity.LOW
    if growth_stage in crop_data.get("critical_stages", []):
        risk_level = PestSeverity.MODERATE
    if weather_forecast:
        high_humidity = any(w.get("humidity", 0) > 80 for w in weather_forecast)
        rain_forecast = any(w.get("rainfall", 0) > 10 for w in weather_forecast)
        if high_humidity and rain_forecast:
            risk_level = PestSeverity.HIGH
    
    advisories = []
    for pest in relevant_pests[:3]:
        advisories.append({
            "category": AdvisoryCategory.PEST_DISEASE.value,
            "priority": AdvisoryPriority.HIGH.value if risk_level in [PestSeverity.HIGH, PestSeverity.SEVERE] else AdvisoryPriority.MEDIUM.value,
            "title": f"{pest.replace('_', ' ').title()} monitoring for {crop_type.value}",
            "description": f"Risk level: {risk_level.value}. {pest.replace('_', ' ').title()} is a major pest in {crop_type.value} at {growth_stage.value} stage.",
            "confidence": ConfidenceLevel.MEDIUM.value,
            "action_items": [
                f"Scout field for {pest.replace('_', ' ')} symptoms",
                "Install pheromone traps if available",
                "Apply neem oil 5% @ 3 ml/L as preventive",
                "Consult local KVK for specific pesticide if threshold crossed",
            ],
            "timeline_days": 7,
            "estimated_cost_inr": 500,
            "materials_needed": ["Neem oil", "Pheromone traps", "Sticky traps"],
            "precautions": [
                "Follow pre-harvest interval",
                "Rotate insecticide groups",
                "Preserve natural enemies",
            ],
            "pest_disease_name": pest,
            "severity": risk_level.value,
            "threshold_reached": False,
            "details": {
                "pest": pest,
                "crop": crop_type.value,
                "stage": growth_stage.value,
                "risk_level": risk_level.value,
            }
        })
    
    for disease in relevant_diseases[:2]:
        advisories.append({
            "category": AdvisoryCategory.PEST_DISEASE.value,
            "priority": AdvisoryPriority.HIGH.value if risk_level in [PestSeverity.HIGH, PestSeverity.SEVERE] else AdvisoryPriority.MEDIUM.value,
            "title": f"{disease.replace('_', ' ').title()} prevention for {crop_type.value}",
            "description": f"Risk level: {risk_level.value}. {disease.replace('_', ' ').title()} can affect {crop_type.value} at {growth_stage.value} stage, especially in humid conditions.",
            "confidence": ConfidenceLevel.MEDIUM.value,
            "action_items": [
                f"Monitor for {disease.replace('_', ' ')} symptoms",
                "Ensure proper field drainage",
                "Apply copper oxychloride 50% WP @ 2.5 g/L as preventive",
                "Remove and destroy infected plant parts",
            ],
            "timeline_days": 7,
            "estimated_cost_inr": 300,
            "materials_needed": ["Copper oxychloride", "Sprayer"],
            "precautions": [
                "Spray in morning/evening",
                "Use sticker for better adhesion",
                "Follow label instructions",
            ],
            "pest_disease_name": disease,
            "severity": risk_level.value,
            "threshold_reached": False,
            "details": {
                "disease": disease,
                "crop": crop_type.value,
                "stage": growth_stage.value,
                "risk_level": risk_level.value,
            }
        })
    
    return advisories


def get_weather_based_advice(weather_forecast: List[Dict]) -> List[str]:
    advice = []
    for w in weather_forecast[:3]:
        day = w.get("date", "")
        rainfall = w.get("rainfall", 0)
        humidity = w.get("humidity", 0)
        temp_max = w.get("temp_max", 0)
        temp_min = w.get("temp_min", 0)
        
        if rainfall > 20:
            advice.append(f"{day}: Heavy rain ({rainfall}mm) expected - ensure drainage, delay spraying")
        elif rainfall > 5:
            advice.append(f"{day}: Light rain ({rainfall}mm) expected - good for soil moisture")
        else:
            advice.append(f"{day}: No significant rain - plan irrigation if needed")
        
        if humidity > 85:
            advice.append(f"{day}: High humidity ({humidity}%) - increase disease monitoring")
        
        if temp_max > 40:
            advice.append(f"{day}: High temp ({temp_max}°C) - increase irrigation frequency")
        elif temp_max < 15:
            advice.append(f"{day}: Low temp ({temp_max}°C) - protect sensitive crops")
    
    return advice


def get_next_scheduled_activities(crop_type: CropType, growth_stage: GrowthStage, days_after_sowing: int) -> List[Dict]:
    activities = []
    
    crop_data = get_crop_data(crop_type)
    current_stage_end = crop_data["stages"].get(growth_stage, (0, 0))[1]
    days_to_next_stage = current_stage_end - days_after_sowing
    
    if growth_stage == GrowthStage.GERMINATION:
        activities.append({
            "activity": "Gap filling and thinning",
            "days_from_now": 5,
            "description": "Fill gaps where seeds didn't germinate, thin excess plants"
        })
        activities.append({
            "activity": "First weeding",
            "days_from_now": 15,
            "description": "Remove weeds before they compete with crop"
        })
    elif growth_stage == GrowthStage.VEGETATIVE:
        activities.append({
            "activity": "Top dressing nitrogen",
            "days_from_now": 10,
            "description": "Apply 2nd split of nitrogen fertilizer"
        })
        activities.append({
            "activity": "Earthing up",
            "days_from_now": 20,
            "description": "Support plants and suppress weeds"
        })
    elif growth_stage == GrowthStage.FLOWERING:
        activities.append({
            "activity": "Pollination support",
            "days_from_now": 5,
            "description": "Ensure bee activity, avoid spraying during peak pollination"
        })
        activities.append({
            "activity": "Potash application",
            "days_from_now": 15,
            "description": "Apply potassium for fruit/grain development"
        })
    elif growth_stage == GrowthStage.FRUITING:
        activities.append({
            "activity": "Fruit/borer monitoring",
            "days_from_now": 3,
            "description": "Check for pest damage on developing produce"
        })
    
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
        if cat == "irrigation":
            parts.append("Irrigate")
        elif cat == "fertilizer":
            parts.append("Fertilizer")
        elif cat == "pest_disease":
            parts.append("Pest alert")
        else:
            parts.append(adv.get("title", "")[:15])
    
    if language in ["Gujlish", "Gujarati"]:
        return f"{', '.join(parts)}: {top[0].get('action_items', [''])[0][:60]}..."
    elif language in ["Hinglish", "Hindi"]:
        return f"{', '.join(parts)}: {top[0].get('action_items', [''])[0][:60]}..."
    else:
        return f"{', '.join(parts)}: {top[0].get('action_items', [''])[0][:60]}..."


def estimate_yield(crop_type: CropType, area_hectares: float, growth_stage: GrowthStage, 
                   management_score: float = 0.7) -> Dict[str, Any]:
    crop_data = get_crop_data(crop_type)
    
    base_yields = {
        CropType.COTTON: 2.5,
        CropType.GROUNDNUT: 2.0,
        CropType.WHEAT: 4.5,
        CropType.BAJRA: 2.5,
        CropType.MAIZE: 5.5,
        CropType.CUMIN: 0.6,
        CropType.CASTOR: 1.8,
    }
    
    base_yield = base_yields.get(crop_type, 2.0)
    estimated = base_yield * area_hectares * management_score
    
    return {
        "estimated_yield_tonnes": round(estimated, 2),
        "per_hectare_tonnes": round(base_yield * management_score, 2),
        "management_score": management_score,
        "days_to_harvest": max(0, crop_data["duration_days"] - (date.today() - date.today()).days),
    }