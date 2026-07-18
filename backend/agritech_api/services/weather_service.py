import random
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from ..schemas import (
    WeatherCondition, Language, Location, CropType, GrowthStage,
    AdvisoryCategory, AdvisoryPriority, ConfidenceLevel
)


WEATHER_CONDITIONS = [
    WeatherCondition.CLEAR,
    WeatherCondition.CLOUDY,
    WeatherCondition.LIGHT_RAIN,
    WeatherCondition.MODERATE_RAIN,
    WeatherCondition.HEAVY_RAIN,
    WeatherCondition.THUNDERSTORM,
    WeatherCondition.HOT,
    WeatherCondition.COLD,
    WeatherCondition.WINDY,
    WeatherCondition.FOG,
]

SEASONAL_WEATHER = {
    1: {"temp_range": (12, 28), "rainfall": 1, "humidity": 55},  # Jan
    2: {"temp_range": (15, 32), "rainfall": 1, "humidity": 50},  # Feb
    3: {"temp_range": (20, 37), "rainfall": 2, "humidity": 45},  # Mar
    4: {"temp_range": (25, 41), "rainfall": 3, "humidity": 50},  # Apr
    5: {"temp_range": (28, 42), "rainfall": 10, "humidity": 60},  # May
    6: {"temp_range": (28, 38), "rainfall": 150, "humidity": 75},  # Jun
    7: {"temp_range": (26, 33), "rainfall": 300, "humidity": 85},  # Jul
    8: {"temp_range": (25, 32), "rainfall": 250, "humidity": 85},  # Aug
    9: {"temp_range": (25, 34), "rainfall": 180, "humidity": 80},  # Sep
    10: {"temp_range": (22, 36), "rainfall": 40, "humidity": 65},  # Oct
    11: {"temp_range": (18, 33), "rainfall": 10, "humidity": 55},  # Nov
    12: {"temp_range": (14, 30), "rainfall": 2, "humidity": 50},  # Dec
}


def get_seasonal_weather(month: int) -> Dict[str, Any]:
    return SEASONAL_WEATHER.get(month, SEASONAL_WEATHER[1])


def generate_weather_forecast(location: Location, days: int = 7) -> List[Dict[str, Any]]:
    month = date.today().month
    seasonal = get_seasonal_weather(month)
    temp_min_base, temp_max_base = seasonal["temp_range"]
    base_humidity = seasonal["humidity"]
    base_rainfall = seasonal["rainfall"] / 30
    
    forecast = []
    for i in range(days):
        d = date.today() + timedelta(days=i)
        
        variation = random.uniform(-3, 3)
        temp_max = max(10, min(48, temp_max_base + variation))
        temp_min = max(5, min(temp_max - 2, temp_min_base + variation))
        humidity = max(20, min(100, base_humidity + random.uniform(-15, 15)))
        
        rain_prob = min(1.0, base_rainfall / 5 + random.uniform(-0.1, 0.1))
        if random.random() < rain_prob:
            rainfall = random.uniform(2, 50)
            if rainfall > 30:
                condition = WeatherCondition.HEAVY_RAIN
            elif rainfall > 10:
                condition = WeatherCondition.MODERATE_RAIN
            else:
                condition = WeatherCondition.LIGHT_RAIN
        else:
            rainfall = 0
            if humidity > 80:
                condition = WeatherCondition.CLOUDY
            elif temp_max > 40:
                condition = WeatherCondition.HOT
            elif temp_max < 15:
                condition = WeatherCondition.COLD
            else:
                condition = random.choice([WeatherCondition.CLEAR, WeatherCondition.CLOUDY])
        
        wind = random.uniform(5, 25)
        if wind > 20:
            condition = WeatherCondition.WINDY
        
        cloud = random.uniform(0, 100)
        
        forecast.append({
            "date": d.isoformat(),
            "condition": condition.value,
            "temp_max_c": round(temp_max, 1),
            "temp_min_c": round(temp_min, 1),
            "humidity_percent": round(humidity, 1),
            "rainfall_mm": round(rainfall, 1),
            "wind_speed_kmph": round(wind, 1),
            "cloud_cover_percent": round(cloud, 1),
        })
    
    return forecast


def generate_weather_advisories(
    forecast: List[Dict],
    crop_type: Optional[CropType] = None,
    growth_stage: Optional[GrowthStage] = None
) -> List[Dict[str, Any]]:
    
    advisories = []
    
    for w in forecast:
        day_advisories = []
        d = w["date"]
        rainfall = w["rainfall_mm"]
        humidity = w["humidity_percent"]
        temp_max = w["temp_max_c"]
        temp_min = w["temp_min_c"]
        wind = w["wind_speed_kmph"]
        condition = w["condition"]
        
        if rainfall > 30:
            day_advisories.append({
                "date": d,
                "advisory": f"Heavy rain ({rainfall:.0f}mm) expected. Ensure field drainage, delay fertilizer/pesticide application.",
                "category": AdvisoryCategory.IRRIGATION.value,
                "priority": AdvisoryPriority.HIGH.value,
                "action_required": True,
            })
        elif rainfall > 10:
            day_advisories.append({
                "date": d,
                "advisory": f"Moderate rain ({rainfall:.0f}mm) expected. Good for soil moisture. Avoid spraying.",
                "category": AdvisoryCategory.IRRIGATION.value,
                "priority": AdvisoryPriority.MEDIUM.value,
                "action_required": False,
            })
        elif rainfall > 2:
            day_advisories.append({
                "date": d,
                "advisory": f"Light rain ({rainfall:.0f}mm) possible. Monitor soil moisture.",
                "category": AdvisoryCategory.IRRIGATION.value,
                "priority": AdvisoryPriority.LOW.value,
                "action_required": False,
            })
        
        if humidity > 85:
            day_advisories.append({
                "date": d,
                "advisory": f"High humidity ({humidity:.0f}%) - Disease risk increased. Scout for fungal diseases.",
                "category": AdvisoryCategory.PEST_DISEASE.value,
                "priority": AdvisoryPriority.HIGH.value,
                "action_required": True,
            })
        
        if temp_max > 40:
            day_advisories.append({
                "date": d,
                "advisory": f"High temperature ({temp_max:.0f}°C) - Increase irrigation frequency, provide shade if possible.",
                "category": AdvisoryCategory.IRRIGATION.value,
                "priority": AdvisoryPriority.HIGH.value,
                "action_required": True,
            })
        elif temp_max < 15:
            day_advisories.append({
                "date": d,
                "advisory": f"Low temperature ({temp_max:.0f}°C) - Protect sensitive crops from cold stress.",
                "category": AdvisoryCategory.GENERAL.value,
                "priority": AdvisoryPriority.MEDIUM.value,
                "action_required": False,
            })
        
        if wind > 25:
            day_advisories.append({
                "date": d,
                "advisory": f"Strong winds ({wind:.0f} km/h) - Risk of lodging. Support tall crops.",
                "category": AdvisoryCategory.GENERAL.value,
                "priority": AdvisoryPriority.MEDIUM.value,
                "action_required": True,
            })
        
        if crop_type and growth_stage:
            crop_specific = get_crop_specific_advice(crop_type, growth_stage, w)
            day_advisories.extend(crop_specific)
        
        advisories.extend(day_advisories)
    
    return advisories


def get_crop_specific_advice(crop_type: CropType, growth_stage: GrowthStage, weather: Dict) -> List[Dict]:
    advice = []
    rainfall = weather["rainfall_mm"]
    humidity = weather["humidity_percent"]
    temp_max = weather["temp_max_c"]
    d = weather["date"]
    
    if crop_type == CropType.COTTON:
        if growth_stage == GrowthStage.FLOWERING and humidity > 80:
            advice.append({
                "date": d,
                "advisory": "Cotton flowering + high humidity = boll rot risk. Spray copper fungicide preventively.",
                "category": AdvisoryCategory.PEST_DISEASE.value,
                "priority": AdvisoryPriority.HIGH.value,
                "action_required": True,
            })
        if growth_stage == GrowthStage.FRUITING and temp_max > 38:
            advice.append({
                "date": d,
                "advisory": "Cotton boll development + heat = boll shedding. Light frequent irrigation needed.",
                "category": AdvisoryCategory.IRRIGATION.value,
                "priority": AdvisoryPriority.HIGH.value,
                "action_required": True,
            })
    
    elif crop_type == CropType.GROUNDNUT:
        if growth_stage == GrowthStage.FRUITING and humidity > 85:
            advice.append({
                "date": d,
                "advisory": "Groundnut pod filling + humidity = tikka/leaf spot risk. Apply preventive fungicide.",
                "category": AdvisoryCategory.PEST_DISEASE.value,
                "priority": AdvisoryPriority.HIGH.value,
                "action_required": True,
            })
    
    elif crop_type == CropType.WHEAT:
        if growth_stage == GrowthStage.FLOWERING and temp_max > 30:
            advice.append({
                "date": d,
                "advisory": "Wheat grain filling + high temp = yield loss. Irrigate if soil moisture low.",
                "category": AdvisoryCategory.IRRIGATION.value,
                "priority": AdvisoryPriority.HIGH.value,
                "action_required": True,
            })
        if growth_stage in [GrowthStage.FLOWERING, GrowthStage.FRUITING] and humidity > 80:
            advice.append({
                "date": d,
                "advisory": "Wheat heading + humidity = rust risk. Monitor for yellow/brown rust.",
                "category": AdvisoryCategory.PEST_DISEASE.value,
                "priority": AdvisoryPriority.MEDIUM.value,
                "action_required": False,
            })
    
    elif crop_type == CropType.CUMIN:
        if growth_stage == GrowthStage.FLOWERING and rainfall > 5:
            advice.append({
                "date": d,
                "advisory": "Cumin flowering + rain = blight/wilt risk. Ensure drainage, avoid irrigation.",
                "category": AdvisoryCategory.PEST_DISEASE.value,
                "priority": AdvisoryPriority.HIGH.value,
                "action_required": True,
            })
    
    return advice


def calculate_et0(
    temp_max: float,
    temp_min: float,
    humidity: float,
    wind_speed: float,
    solar_radiation: Optional[float] = None
) -> float:
    """FAO-56 Penman-Monteith simplified (Hargreaves for limited data)"""
    t_mean = (temp_max + temp_min) / 2
    t_diff = temp_max - temp_min
    et0 = 0.0023 * (t_mean + 17.8) * (t_diff ** 0.5) * (100 - humidity) / 100
    
    if solar_radiation:
        et0 = et0 * 0.7 + 0.408 * solar_radiation * 0.3
    
    if wind_speed > 5:
        et0 *= (1 + (wind_speed - 5) * 0.02)
    
    return max(0, round(et0, 2))


def get_crop_coefficient(crop_type: CropType, growth_stage: GrowthStage) -> float:
    kc_values = {
        CropType.COTTON: {
            GrowthStage.GERMINATION: 0.35,
            GrowthStage.VEGETATIVE: 0.75,
            GrowthStage.FLOWERING: 1.15,
            GrowthStage.FRUITING: 1.10,
            GrowthStage.MATURITY: 0.70,
            GrowthStage.HARVEST: 0.35,
        },
        CropType.GROUNDNUT: {
            GrowthStage.GERMINATION: 0.40,
            GrowthStage.VEGETATIVE: 0.80,
            GrowthStage.FLOWERING: 1.05,
            GrowthStage.FRUITING: 1.00,
            GrowthStage.MATURITY: 0.65,
            GrowthStage.HARVEST: 0.35,
        },
        CropType.WHEAT: {
            GrowthStage.GERMINATION: 0.30,
            GrowthStage.VEGETATIVE: 0.85,
            GrowthStage.FLOWERING: 1.15,
            GrowthStage.FRUITING: 1.05,
            GrowthStage.MATURITY: 0.70,
            GrowthStage.HARVEST: 0.25,
        },
        CropType.BAJRA: {
            GrowthStage.GERMINATION: 0.30,
            GrowthStage.VEGETATIVE: 0.70,
            GrowthStage.FLOWERING: 1.00,
            GrowthStage.FRUITING: 0.95,
            GrowthStage.MATURITY: 0.60,
            GrowthStage.HARVEST: 0.25,
        },
        CropType.MAIZE: {
            GrowthStage.GERMINATION: 0.30,
            GrowthStage.VEGETATIVE: 0.75,
            GrowthStage.FLOWERING: 1.20,
            GrowthStage.FRUITING: 1.10,
            GrowthStage.MATURITY: 0.80,
            GrowthStage.HARVEST: 0.35,
        },
    }
    
    return kc_values.get(crop_type, {}).get(growth_stage, 1.0)


def calculate_etc(et0: float, kc: float) -> float:
    return round(et0 * kc, 2)


def assess_heat_stress(temp_max: float, crop_type: CropType) -> Dict[str, Any]:
    thresholds = {
        CropType.COTTON: 38,
        CropType.GROUNDNUT: 35,
        CropType.WHEAT: 30,
        CropType.BAJRA: 40,
        CropType.MAIZE: 38,
        CropType.CUMIN: 35,
        CropType.CASTOR: 40,
    }
    
    threshold = thresholds.get(crop_type, 35)
    
    if temp_max > threshold + 5:
        level = "severe"
    elif temp_max > threshold:
        level = "moderate"
    elif temp_max > threshold - 3:
        level = "mild"
    else:
        level = "none"
    
    return {
        "crop": crop_type.value,
        "threshold_celsius": threshold,
        "current_temp_celsius": temp_max,
        "heat_stress_level": level,
        "impact": "Yield reduction likely" if level in ["moderate", "severe"] else "Minimal impact",
        "recommendations": [
            "Increase irrigation frequency",
            "Apply mulch to conserve soil moisture",
            "Consider antitranspirant spray",
            "Avoid fertilizer application during peak heat",
        ] if level != "none" else ["Monitor temperature trends"],
    }


def assess_cold_stress(temp_min: float, crop_type: CropType, growth_stage: GrowthStage) -> Dict[str, Any]:
    sensitive_stages = [GrowthStage.GERMINATION, GrowthStage.FLOWERING]
    thresholds = {
        CropType.COTTON: 12,
        CropType.GROUNDNUT: 10,
        CropType.WHEAT: 0,
        CropType.BAJRA: 10,
        CropType.MAIZE: 8,
        CropType.CUMIN: 5,
        CropType.CASTOR: 10,
    }
    
    threshold = thresholds.get(crop_type, 10)
    
    if growth_stage in sensitive_stages:
        threshold += 3
    
    if temp_min < threshold - 5:
        level = "severe"
    elif temp_min < threshold:
        level = "moderate"
    elif temp_min < threshold + 3:
        level = "mild"
    else:
        level = "none"
    
    return {
        "crop": crop_type.value,
        "stage": growth_stage.value,
        "threshold_celsius": threshold,
        "current_temp_celsius": temp_min,
        "cold_stress_level": level,
        "impact": "Growth retardation/frost damage possible" if level in ["moderate", "severe"] else "Minimal impact",
        "recommendations": [
            "Light irrigation before cold night",
            "Smoke/fogging for frost protection",
            "Avoid nitrogen application",
            "Cover nursery/seedlings",
        ] if level != "none" else ["Monitor temperature trends"],
    }


def get_overall_risk(advisories: List[Dict]) -> str:
    high_count = sum(1 for a in advisories if a.get("priority") == AdvisoryPriority.HIGH.value)
    medium_count = sum(1 for a in advisories if a.get("priority") == AdvisoryPriority.MEDIUM.value)
    
    if high_count >= 2:
        return "high"
    elif high_count >= 1 or medium_count >= 3:
        return "medium"
    else:
        return "low"