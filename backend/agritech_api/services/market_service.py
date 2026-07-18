import random
import math
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from ..schemas import (
    CropType, MandiType, PriceTrend, DecisionAction, StorageCondition, TransportMode
)


MANDI_DATA = {
    "Gujarat": {
        "Ahmedabad": {
            "mandis": [
                {"name": "Ahmedabad APMC", "type": MandiType.APMC, "crops": [CropType.COTTON, CropType.WHEAT, CropType.CUMIN, CropType.CASTOR]},
                {"name": "Ahmedabad E-NAM", "type": MandiType.E_NAM, "crops": [CropType.COTTON, CropType.WHEAT, CropType.MAIZE]},
            ]
        },
        "Rajkot": {
            "mandis": [
                {"name": "Rajkot APMC", "type": MandiType.APMC, "crops": [CropType.GROUNDNUT, CropType.COTTON, CropType.CUMIN]},
                {"name": "Rajkot FPO Market", "type": MandiType.FPO, "crops": [CropType.GROUNDNUT, CropType.SESAME]},
            ]
        },
        "Surat": {
            "mandis": [
                {"name": "Surat APMC", "type": MandiType.APMC, "crops": [CropType.COTTON, CropType.BAJRA, CropType.MAIZE]},
            ]
        },
        "Vadodara": {
            "mandis": [
                {"name": "Vadodara APMC", "type": MandiType.APMC, "crops": [CropType.COTTON, CropType.MAIZE, CropType.WHEAT]},
            ]
        },
        "Junagadh": {
            "mandis": [
                {"name": "Junagadh APMC", "type": MandiType.APMC, "crops": [CropType.GROUNDNUT, CropType.CUMIN, CropType.CASTOR]},
            ]
        },
        "Bhavnagar": {
            "mandis": [
                {"name": "Bhavnagar APMC", "type": MandiType.APMC, "crops": [CropType.COTTON, CropType.GROUNDNUT, CropType.SESAME]},
            ]
        },
    }
}

BASE_PRICES = {
    CropType.COTTON: 6500,
    CropType.GROUNDNUT: 5500,
    CropType.WHEAT: 2200,
    CropType.BAJRA: 2100,
    CropType.MAIZE: 2000,
    CropType.CUMIN: 18000,
    CropType.CASTOR: 5000,
    CropType.SESAME: 8500,
    CropType.TOBACCO: 12000,
    CropType.GREEN_GRAM: 7000,
    CropType.BLACK_GRAM: 6500,
    CropType.PIGEON_PEA: 6000,
    CropType.CHILLI: 15000,
    CropType.ONION: 1800,
    CropType.POTATO: 1200,
    CropType.BANANA: 1500,
    CropType.PAPAYA: 1000,
    CropType.MANGO: 3000,
}


SEASONAL_FACTORS = {
    CropType.COTTON: {1: 1.1, 2: 1.05, 3: 1.0, 4: 0.95, 5: 0.9, 6: 0.85, 7: 0.8, 8: 0.9, 9: 1.0, 10: 1.1, 11: 1.15, 12: 1.1},
    CropType.GROUNDNUT: {1: 1.0, 2: 0.95, 3: 0.9, 4: 0.9, 5: 0.95, 6: 1.0, 7: 1.05, 8: 1.1, 9: 1.15, 10: 1.2, 11: 1.1, 12: 1.05},
    CropType.WHEAT: {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.05, 5: 1.1, 6: 1.15, 7: 1.1, 8: 1.05, 9: 1.0, 10: 0.95, 11: 0.95, 12: 1.0},
    CropType.BAJRA: {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.05, 5: 1.1, 6: 1.1, 7: 1.05, 8: 1.0, 9: 1.0, 10: 1.1, 11: 1.15, 12: 1.1},
    CropType.MAIZE: {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.05, 6: 1.1, 7: 1.1, 8: 1.05, 9: 1.0, 10: 1.0, 11: 1.0, 12: 1.0},
    CropType.CUMIN: {1: 1.15, 2: 1.1, 3: 1.05, 4: 1.0, 5: 0.95, 6: 0.9, 7: 0.9, 8: 0.9, 9: 0.95, 10: 1.0, 11: 1.1, 12: 1.15},
    CropType.CASTOR: {1: 1.0, 2: 1.0, 3: 1.05, 4: 1.1, 5: 1.1, 6: 1.05, 7: 1.0, 8: 1.0, 9: 1.0, 10: 1.05, 11: 1.1, 12: 1.05},
}


def get_base_price(crop: CropType, month: Optional[int] = None) -> float:
    base = BASE_PRICES.get(crop, 2500)
    if month:
        factor = SEASONAL_FACTORS.get(crop, {}).get(month, 1.0)
        return base * factor
    return base


def get_mandis_for_crop(state: str, crop: CropType) -> List[Dict]:
    state_data = MANDI_DATA.get(state, MANDI_DATA["Gujarat"])
    mandis = []
    for district, data in state_data.items():
        for mandi in data["mandis"]:
            if crop in mandi["crops"]:
                mandis.append({
                    "name": mandi["name"],
                    "type": mandi["type"],
                    "district": district,
                    "state": state,
                })
    return mandis


def generate_mandi_prices(
    crop: CropType,
    location: str = "Gujarat",
    count: int = 5,
    date: Optional[date] = None
) -> List[Dict]:
    date = date or date.today()
    mandis = get_mandis_for_crop(location, crop)
    
    if not mandis:
        mandis = [
            {"name": f"{location} APMC", "type": MandiType.APMC, "district": location, "state": location},
            {"name": f"{location} E-NAM", "type": MandiType.E_NAM, "district": location, "state": location},
        ]
    
    prices = []
    base = get_base_price(crop, date.month)
    
    for i, mandi in enumerate(mandis[:count]):
        variation = random.uniform(0.92, 1.08)
        mandi_price = base * variation
        
        min_price = mandi_price * random.uniform(0.95, 0.98)
        max_price = mandi_price * random.uniform(1.02, 1.05)
        modal_price = mandi_price * random.uniform(0.98, 1.02)
        arrival = random.uniform(50, 2000)
        
        prices.append({
            "mandi_name": mandi["name"],
            "mandi_type": mandi["type"],
            "district": mandi["district"],
            "state": mandi["state"],
            "price_per_quintal": round(mandi_price),
            "min_price": round(min_price),
            "max_price": round(max_price),
            "modal_price": round(modal_price),
            "arrival_tonnes": round(arrival, 1),
            "date": date.isoformat(),
            "distance_km": round(random.uniform(5, 80), 1),
        })
    
    prices.sort(key=lambda x: x["price_per_quintal"], reverse=True)
    return prices


def get_price_trend(crop: CropType, days: int = 30) -> List[Dict]:
    trend = []
    base = get_base_price(crop)
    current = base * random.uniform(0.95, 1.05)
    
    for i in range(days):
        d = date.today() - timedelta(days=days-i)
        change = random.uniform(-0.02, 0.02)
        current = current * (1 + change)
        current = max(base * 0.8, min(base * 1.3, current))
        
        trend.append({
            "date": d.isoformat(),
            "price_per_quintal": round(current),
            "mandi_name": "Average",
            "arrival_tonnes": round(random.uniform(100, 1500), 1),
        })
    
    return trend


def determine_price_trend(history: List[Dict]) -> PriceTrend:
    if len(history) < 2:
        return PriceTrend.STABLE
    
    recent = history[-7:]
    older = history[-14:-7] if len(history) >= 14 else history[:-7]
    
    recent_avg = sum(p["price_per_quintal"] for p in recent) / len(recent)
    older_avg = sum(p["price_per_quintal"] for p in older) / len(older) if older else recent_avg
    
    change_pct = (recent_avg - older_avg) / older_avg * 100
    
    if change_pct > 3:
        return PriceTrend.RISING
    elif change_pct < -3:
        return PriceTrend.FALLING
    elif max(p["price_per_quintal"] for p in recent) / min(p["price_per_quintal"] for p in recent) > 1.05:
        return PriceTrend.VOLATILE
    else:
        return PriceTrend.STABLE


def calculate_spoilage_curve(
    crop: CropType,
    storage: StorageCondition,
    initial_moisture: float,
    temperature: float = 25,
    humidity: float = 60,
    days_stored: int = 0,
    horizon_days: int = 30
) -> List[Dict]:
    crop_factors = {
        CropType.COTTON: {"base_rate": 0.001, "moisture_sensitivity": 1.2},
        CropType.GROUNDNUT: {"base_rate": 0.003, "moisture_sensitivity": 1.5},
        CropType.WHEAT: {"base_rate": 0.001, "moisture_sensitivity": 1.0},
        CropType.BAJRA: {"base_rate": 0.001, "moisture_sensitivity": 1.0},
        CropType.MAIZE: {"base_rate": 0.002, "moisture_sensitivity": 1.3},
        CropType.CUMIN: {"base_rate": 0.001, "moisture_sensitivity": 1.1},
        CropType.CASTOR: {"base_rate": 0.001, "moisture_sensitivity": 1.0},
    }
    
    storage_factors = {
        StorageCondition.OPEN: 1.5,
        StorageCondition.SHED: 1.0,
        StorageCondition.WAREHOUSE: 0.7,
        StorageCondition.COLD_STORAGE: 0.2,
        StorageCondition.HERMETIC: 0.1,
        StorageCondition.SILOS: 0.3,
    }
    
    cf = crop_factors.get(crop, crop_factors[CropType.WHEAT])
    sf = storage_factors.get(storage, 1.0)
    
    moisture_factor = max(1.0, (initial_moisture - 10) / 4 * cf["moisture_sensitivity"])
    temp_factor = 1.0 + max(0, (temperature - 25)) * 0.03
    humidity_factor = 1.0 + max(0, (humidity - 65)) * 0.01
    
    daily_rate = cf["base_rate"] * sf * moisture_factor * temp_factor * humidity_factor
    
    points = []
    current_quality = 100.0
    base_price = get_base_price(crop)
    
    for day in range(days_stored, days_stored + horizon_days + 1):
        if day > days_stored:
            current_quality *= (1 - daily_rate)
        
        current_quality = max(0, current_quality)
        marketable_pct = current_quality
        loss_kg = (100 - current_quality) / 100 * 1000
        value_loss = loss_kg / 100 * base_price
        
        if current_quality > 90:
            risk = "low"
        elif current_quality > 70:
            risk = "medium"
        elif current_quality > 50:
            risk = "high"
        else:
            risk = "critical"
        
        points.append({
            "day": day,
            "remaining_quality_percent": round(current_quality, 1),
            "spoilage_loss_kg_per_tonne": round(loss_kg, 1),
            "marketable_kg_per_tonne": round(marketable_pct * 10, 1),
            "value_loss_inr_per_tonne": round(value_loss, 0),
            "risk_level": risk,
        })
    
    return points


def evaluate_sell_options(
    crop: CropType,
    quantity_kg: float,
    storage: StorageCondition,
    current_price: float,
    farmer_expected_price: Optional[float],
    days_stored: int,
    quality_grade: Optional[str],
    transport_mode: TransportMode,
    transport_cost_per_km: float,
    max_distance_km: float,
    location: str = "Gujarat"
) -> List[Dict]:
    
    mandis = get_mandis_for_crop(location, crop)
    if not mandis:
        mandis = [{"name": f"{location} APMC", "type": MandiType.APMC, "district": location, "state": location}]
    
    options = []
    
    spoilage_curve = calculate_spoilage_curve(crop, storage, 12, 25, 60, days_stored, 30)
    daily_spoilage_rate = (spoilage_curve[1]["spoilage_loss_kg_per_tonne"] - spoilage_curve[0]["spoilage_loss_kg_per_tonne"]) / 1000
    
    for mandi in mandis[:5]:
        distance = mandi.get("distance_km", random.uniform(10, 80))
        if distance > max_distance_km:
            continue
        
        mandi_prices = generate_mandi_prices(crop, location, 1)
        mandi_price = mandi_prices[0]["price_per_quintal"] if mandi_prices else current_price
        
        grade_factor = {"FAQ": 1.0, "Grade-A": 1.05, "Grade-B": 0.95, "Grade-C": 0.85}.get(quality_grade, 1.0)
        adjusted_price = mandi_price * grade_factor
        
        transport_cost = distance * transport_cost_per_km * (quantity_kg / 1000)
        handling_cost = quantity_kg / 100 * 10
        
        future_spoilage = daily_spoilage_rate * quantity_kg / 1000 * 7 * adjusted_price
        
        if farmer_expected_price and adjusted_price < farmer_expected_price * 0.95:
            action = DecisionAction.STORE
            days_to_execute = 0
            net_price = adjusted_price
            storage_cost = quantity_kg / 100 * 5 * 30
        elif adjusted_price >= current_price * 1.02:
            action = DecisionAction.TRANSPORT_TO_MANDI
            days_to_execute = 2
            net_price = adjusted_price
            storage_cost = 0
        else:
            action = DecisionAction.SELL_IMMEDIATELY
            days_to_execute = 0
            net_price = current_price
            storage_cost = 0
        
        total_cost = transport_cost + handling_cost + storage_cost + future_spoilage
        net_per_quintal = net_price - (total_cost / (quantity_kg / 100))
        total_net = net_per_quintal * (quantity_kg / 100)
        
        risk = "low"
        if daily_spoilage_rate > 0.002:
            risk = "high"
        elif daily_spoilage_rate > 0.001:
            risk = "medium"
        
        if action == DecisionAction.STORE and days_stored > 60:
            risk = "high"
        
        options.append({
            "action": action.value,
            "mandi_name": mandi["name"] if action == DecisionAction.TRANSPORT_TO_MANDI else None,
            "mandi_distance_km": round(distance, 1) if action == DecisionAction.TRANSPORT_TO_MANDI else None,
            "expected_price_per_quintal": round(adjusted_price),
            "transport_cost": round(transport_cost),
            "handling_cost": round(handling_cost),
            "storage_cost": round(storage_cost),
            "spoilage_loss_kg": round(daily_spoilage_rate * quantity_kg / 1000 * 7 * 1000),
            "net_realisation_per_quintal": round(net_per_quintal),
            "total_net_income": round(total_net),
            "days_to_execute": days_to_execute,
            "risk_level": risk,
            "reasoning": f"Mandi price: ₹{adjusted_price}/q. Transport: ₹{transport_cost:.0f}. Storage risk: {risk}. Recommended: {action.value.replace('_', ' ')}."
        })
    
    options.sort(key=lambda x: x["total_net_income"], reverse=True)
    return options


def calculate_transport_cost(
    distance_km: float,
    quantity_kg: float,
    mode: TransportMode,
    crop: Optional[CropType] = None
) -> Dict[str, Any]:
    
    mode_rates = {
        TransportMode.TRUCK: {"rate_per_km_per_tonne": 2.5, "fixed_cost": 1500, "capacity_tonnes": 10},
        TransportMode.TRACTOR_TROLLEY: {"rate_per_km_per_tonne": 1.8, "fixed_cost": 500, "capacity_tonnes": 3},
        TransportMode.MINI_TRUCK: {"rate_per_km_per_tonne": 3.0, "fixed_cost": 1000, "capacity_tonnes": 5},
        TransportMode.RAILWAY: {"rate_per_km_per_tonne": 1.2, "fixed_cost": 5000, "capacity_tonnes": 50},
        TransportMode.OWN_VEHICLE: {"rate_per_km_per_tonne": 1.5, "fixed_cost": 0, "capacity_tonnes": 2},
    }
    
    m = mode_rates.get(mode, mode_rates[TransportMode.TRUCK])
    tonnes = quantity_kg / 1000
    trips = math.ceil(tonnes / m["capacity_tonnes"])
    
    variable_cost = distance_km * m["rate_per_km_per_tonne"] * tonnes
    fixed_cost = m["fixed_cost"] * trips
    loading_unloading = tonnes * 50 * trips
    
    total = variable_cost + fixed_cost + loading_unloading
    per_quintal = total / (quantity_kg / 100)
    time_hours = distance_km / 40 * trips + 2 * trips
    
    return {
        "distance_km": distance_km,
        "transport_mode": mode.value,
        "quantity_tonnes": tonnes,
        "trips_required": trips,
        "cost_per_km_per_tonne": m["rate_per_km_per_tonne"],
        "variable_cost": round(variable_cost),
        "fixed_cost": round(fixed_cost),
        "loading_unloading_cost": round(loading_unloading),
        "total_cost": round(total),
        "cost_per_quintal": round(per_quintal),
        "estimated_time_hours": round(time_hours, 1),
    }


def forecast_prices(
    crop: CropType,
    horizon_days: int = 14,
    current_price: Optional[float] = None
) -> List[Dict]:
    
    base = current_price or get_base_price(crop)
    forecast = []
    
    trend = random.choice(["rising", "falling", "stable"])
    daily_change = {"rising": 0.005, "falling": -0.005, "stable": 0.0}[trend]
    volatility = 0.015
    
    for i in range(1, horizon_days + 1):
        d = date.today() + timedelta(days=i)
        change = daily_change + random.uniform(-volatility, volatility)
        base = base * (1 + change)
        base = max(get_base_price(crop) * 0.7, min(get_base_price(crop) * 1.4, base))
        
        lower = base * 0.95
        upper = base * 1.05
        
        forecast.append({
            "date": d.isoformat(),
            "predicted_price": round(base),
            "lower_bound": round(lower),
            "upper_bound": round(upper),
            "confidence": max(0.5, 0.9 - i * 0.02),
        })
    
    return forecast


def check_price_alert(
    alert_price: float,
    current_price: float,
    direction: str
) -> bool:
    if direction == "above":
        return current_price >= alert_price
    else:
        return current_price <= alert_price