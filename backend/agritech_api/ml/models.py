import os
import json
import pickle
import asyncio
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import random

from agritech_api.schemas import CropType, SoilType, GrowthStage, Location


@dataclass
class YieldPrediction:
    predicted_yield_tonnes_ha: float
    confidence_interval: Tuple[float, float]
    confidence_level: float
    key_factors: Dict[str, float]
    risk_factors: List[str]
    recommendation: str


@dataclass
class PriceForecast:
    crop: CropType
    forecast_date: date
    predicted_price: float
    lower_bound: float
    upper_bound: float
    trend: str
    confidence: float
    drivers: List[str]


@dataclass
class DiseaseRisk:
    crop: CropType
    disease: str
    risk_level: str
    probability: float
    days_to_peak: int
    recommended_action: str
    weather_trigger: Dict[str, Any]


class MLModelManager:
    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        self.yield_models: Dict[CropType, Any] = {}
        self.price_models: Dict[CropType, Any] = {}
        self.disease_models: Dict[str, Any] = {}
        self.irrigation_model = None
        self.fertilizer_model = None
        
        self._load_models()

    def _load_models(self):
        try:
            self._load_sklearn_models()
        except Exception as e:
            print(f"[MLModels] No pre-trained models found, using rule-based: {e}")
            self._init_rule_based()

    def _load_sklearn_models(self):
        import joblib
        
        for crop in CropType:
            yield_path = self.model_dir / f"yield_{crop.value}.joblib"
            if yield_path.exists():
                self.yield_models[crop] = joblib.load(yield_path)
            
            price_path = self.model_dir / f"price_{crop.value}.joblib"
            if price_path.exists():
                self.price_models[crop] = joblib.load(price_path)
        
        disease_path = self.model_dir / "disease_risk.joblib"
        if disease_path.exists():
            self.disease_models["general"] = joblib.load(disease_path)
        
        irrigation_path = self.model_dir / "irrigation_optimizer.joblib"
        if irrigation_path.exists():
            self.irrigation_model = joblib.load(irrigation_path)
        
        fertilizer_path = self.model_dir / "fertilizer_optimizer.joblib"
        if fertilizer_path.exists():
            self.fertilizer_model = joblib.load(fertilizer_path)

    def _init_rule_based(self):
        self.yield_models = {crop: RuleBasedYieldModel(crop) for crop in CropType}
        self.price_models = {crop: RuleBasedPriceModel(crop) for crop in CropType}
        self.disease_models["general"] = RuleBasedDiseaseModel()
        self.irrigation_model = RuleBasedIrrigationModel()
        self.fertilizer_model = RuleBasedFertilizerModel()


class RuleBasedYieldModel:
    def __init__(self, crop: CropType):
        self.crop = crop
        self.base_yields = {
            CropType.COTTON: 2.5,
            CropType.GROUNDNUT: 2.0,
            CropType.WHEAT: 4.5,
            CropType.BAJRA: 2.5,
            CropType.MAIZE: 5.5,
            CropType.CUMIN: 0.6,
            CropType.CASTOR: 1.8,
            CropType.SESAME: 0.8,
            CropType.TOBACCO: 2.0,
            CropType.GREEN_GRAM: 1.0,
            CropType.BLACK_GRAM: 0.9,
            CropType.PIGEON_PEA: 1.2,
            CropType.CHILLI: 2.5,
            CropType.ONION: 25.0,
            CropType.POTATO: 20.0,
            CropType.BANANA: 40.0,
            CropType.PAPAYA: 35.0,
            CropType.MANGO: 10.0,
        }
        
        self.crop_factors = {
            CropType.COTTON: {"temp_opt": (25, 35), "rain_opt": (600, 1000), "soil_pref": [SoilType.BLACK_COTTON, SoilType.ALLUVIAL]},
            CropType.GROUNDNUT: {"temp_opt": (25, 30), "rain_opt": (450, 750), "soil_pref": [SoilType.SANDY_LOAM, SoilType.RED_LOAM]},
            CropType.WHEAT: {"temp_opt": (15, 25), "rain_opt": (300, 500), "soil_pref": [SoilType.ALLUVIAL, SoilType.CLAY]},
            CropType.BAJRA: {"temp_opt": (25, 35), "rain_opt": (300, 500), "soil_pref": [SoilType.SANDY_LOAM, SoilType.RED_LOAM]},
            CropType.MAIZE: {"temp_opt": (20, 30), "rain_opt": (500, 800), "soil_pref": [SoilType.ALLUVIAL, SoilType.RED_LOAM]},
            CropType.CUMIN: {"temp_opt": (20, 30), "rain_opt": (250, 400), "soil_pref": [SoilType.SANDY_LOAM, SoilType.ALLUVIAL]},
            CropType.CASTOR: {"temp_opt": (25, 35), "rain_opt": (500, 750), "soil_pref": [SoilType.RED_LOAM, SoilType.SANDY_LOAM]},
        }

    def predict(
        self,
        area_hectares: float,
        soil_type: SoilType,
        sowing_date: date,
        temperature_avg: float,
        rainfall_total: float,
        humidity_avg: float,
        soil_n: float,
        soil_p: float,
        soil_k: float,
        soil_ph: float,
        irrigation_count: int,
        fertilizer_n: float,
        fertilizer_p: float,
        fertilizer_k: float,
        pest_pressure: float = 0.1,
        disease_pressure: float = 0.1,
        ndvi_avg: float = 0.6,
    ) -> YieldPrediction:
        base = self.base_yields.get(self.crop, 2.0)
        factors = self.crop_factors.get(self.crop, {})
        
        factor = 1.0
        key_factors = {}
        
        temp_opt = factors.get("temp_opt", (20, 35))
        if temp_opt[0] <= temperature_avg <= temp_opt[1]:
            temp_factor = 1.0
        else:
            deviation = min(abs(temperature_avg - temp_opt[0]), abs(temperature_avg - temp_opt[1]))
            temp_factor = max(0.5, 1.0 - deviation * 0.03)
        factor *= temp_factor
        key_factors["temperature"] = round(temp_factor, 2)
        
        rain_opt = factors.get("rain_opt", (400, 800))
        if rain_opt[0] <= rainfall_total <= rain_opt[1]:
            rain_factor = 1.0
        elif rainfall_total < rain_opt[0]:
            rain_factor = max(0.4, rainfall_total / rain_opt[0])
        else:
            rain_factor = max(0.6, 1.0 - (rainfall_total - rain_opt[1]) / rain_opt[1] * 0.3)
        factor *= rain_factor
        key_factors["rainfall"] = round(rain_factor, 2)
        
        soil_pref = factors.get("soil_pref", [])
        soil_factor = 1.1 if soil_type in soil_pref else 0.9
        factor *= soil_factor
        key_factors["soil_type"] = round(soil_factor, 2)
        
        n_factor = min(1.2, max(0.5, soil_n / 200 + fertilizer_n / 150))
        p_factor = min(1.2, max(0.5, soil_p / 25 + fertilizer_p / 50))
        k_factor = min(1.2, max(0.5, soil_k / 200 + fertilizer_k / 100))
        nutrient_factor = (n_factor + p_factor + k_factor) / 3
        factor *= nutrient_factor
        key_factors["nutrients"] = round(nutrient_factor, 2)
        
        ph_factor = 1.0
        if soil_ph < 5.5 or soil_ph > 8.5:
            ph_factor = 0.7
        elif soil_ph < 6.0 or soil_ph > 8.0:
            ph_factor = 0.85
        factor *= ph_factor
        key_factors["ph"] = round(ph_factor, 2)
        
        irrigation_factor = min(1.2, 0.7 + irrigation_count * 0.05)
        factor *= irrigation_factor
        key_factors["irrigation"] = round(irrigation_factor, 2)
        
        pest_factor = max(0.5, 1.0 - pest_pressure * 1.5)
        factor *= pest_factor
        key_factors["pest_pressure"] = round(pest_factor, 2)
        
        disease_factor = max(0.5, 1.0 - disease_pressure * 1.5)
        factor *= disease_factor
        key_factors["disease_pressure"] = round(disease_factor, 2)
        
        ndvi_factor = max(0.5, min(1.3, ndvi_avg / 0.6))
        factor *= ndvi_factor
        key_factors["ndvi"] = round(ndvi_factor, 2)
        
        predicted = base * factor * area_hectares
        
        uncertainty = 0.15
        uncertainty += pest_pressure * 0.1
        uncertainty += disease_pressure * 0.1
        uncertainty += abs(1 - temp_factor) * 0.1
        uncertainty += abs(1 - rain_factor) * 0.1
        uncertainty = min(0.4, uncertainty)
        
        lower = predicted * (1 - uncertainty)
        upper = predicted * (1 + uncertainty)
        
        risk_factors = []
        if temp_factor < 0.8:
            risk_factors.append(f"Temperature stress ({temperature_avg}°C)")
        if rain_factor < 0.8:
            risk_factors.append(f"Water stress ({rainfall_total}mm)")
        if pest_pressure > 0.3:
            risk_factors.append("High pest pressure")
        if disease_pressure > 0.3:
            risk_factors.append("High disease pressure")
        if soil_n < 150:
            risk_factors.append("Low soil nitrogen")
        if ndvi_avg < 0.4:
            risk_factors.append("Low crop vigor (NDVI)")
        
        if factor > 1.1:
            rec = "Excellent conditions - maintain management"
        elif factor > 0.9:
            rec = "Good conditions - optimize inputs"
        elif factor > 0.7:
            rec = "Moderate stress - increase monitoring and irrigation"
        else:
            rec = "High stress - immediate intervention needed"
        
        return YieldPrediction(
            predicted_yield_tonnes_ha=round(predicted / area_hectares, 2) if area_hectares > 0 else round(predicted, 2),
            confidence_interval=(round(lower / area_hectares, 2) if area_hectares > 0 else round(lower, 2), 
                               round(upper / area_hectares, 2) if area_hectares > 0 else round(upper, 2)),
            confidence_level=round(1 - uncertainty, 2),
            key_factors=key_factors,
            risk_factors=risk_factors,
            recommendation=rec,
        )


class RuleBasedPriceModel:
    def __init__(self, crop: CropType):
        self.crop = crop
        self.base_prices = {
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
        
        self.seasonal = {
            CropType.COTTON: {10: 1.1, 11: 1.15, 12: 1.1, 1: 1.05, 2: 1.0, 3: 0.95},
            CropType.GROUNDNUT: {3: 0.9, 4: 0.9, 5: 0.95, 6: 1.0, 7: 1.05, 8: 1.1, 9: 1.15, 10: 1.2},
            CropType.WHEAT: {3: 1.0, 4: 1.05, 5: 1.1, 6: 1.15, 7: 1.1},
            CropType.CUMIN: {1: 1.15, 2: 1.1, 3: 1.05, 4: 1.0, 5: 0.95},
        }

    def forecast(
        self,
        current_price: float,
        historical_prices: List[Dict],
        arrival_trend: List[float],
        weather_forecast: List[Dict],
        days_ahead: int = 14
    ) -> List[PriceForecast]:
        base = self.base_prices.get(self.crop, current_price)
        seasonal_factor = self.seasonal.get(self.crop, {}).get(date.today().month, 1.0)
        
        trend = 0
        if len(historical_prices) >= 7:
            recent = np.mean([p["price"] for p in historical_prices[-7:]])
            older = np.mean([p["price"] for p in historical_prices[-14:-7]]) if len(historical_prices) >= 14 else recent
            trend = (recent - older) / older
        
        arrival_factor = 1.0
        if arrival_trend:
            avg_arrival = np.mean(arrival_trend[-7:])
            if avg_arrival > np.mean(arrival_trend) * 1.2:
                arrival_factor = 0.95
            elif avg_arrival < np.mean(arrival_trend) * 0.8:
                arrival_factor = 1.05
        
        weather_factor = 1.0
        for w in weather_forecast[:7]:
            if w.get("rainfall_mm", 0) > 30:
                weather_factor *= 1.02
            if w.get("temp_max_c", 0) > 40:
                weather_factor *= 1.01
        
        results = []
        for i in range(1, days_ahead + 1):
            daily_trend = trend * 0.5 + np.random.normal(0, 0.01)
            daily_arrival = arrival_factor * (1 + np.random.normal(0, 0.02))
            daily_weather = weather_factor * (1 + np.random.normal(0, 0.01))
            
            predicted = current_price * (1 + daily_trend) * daily_arrival * daily_weather
            predicted = max(base * 0.7, min(base * 1.4, predicted))
            
            volatility = 0.03 + abs(daily_trend) * 0.5
            lower = predicted * (1 - volatility)
            upper = predicted * (1 + volatility)
            
            confidence = max(0.5, 0.9 - i * 0.02)
            
            if daily_trend > 0.01:
                trend_str = "rising"
            elif daily_trend < -0.01:
                trend_str = "falling"
            else:
                trend_str = "stable"
            
            drivers = []
            if abs(trend) > 0.02:
                drivers.append("Historical trend")
            if arrival_factor != 1.0:
                drivers.append("Arrival pressure")
            if weather_factor != 1.0:
                drivers.append("Weather impact")
            
            results.append(PriceForecast(
                crop=self.crop,
                forecast_date=date.today() + timedelta(days=i),
                predicted_price=round(predicted),
                lower_bound=round(lower),
                upper_bound=round(upper),
                trend=trend_str,
                confidence=round(confidence, 2),
                drivers=drivers,
            ))
        
        return results


class RuleBasedDiseaseModel:
    def __init__(self):
        self.disease_rules = {
            CropType.COTTON: {
                "boll_rot": {"humidity": 85, "rainfall": 10, "temp": (25, 35), "stage": [GrowthStage.FLOWERING, GrowthStage.FRUITING]},
                "leaf_curl": {"temp": (30, 40), "humidity": 60, "vector": "whitefly", "stage": [GrowthStage.VEGETATIVE, GrowthStage.FLOWERING]},
                "root_rot": {"soil_moisture": 80, "temp": (25, 30), "stage": [GrowthStage.GERMINATION, GrowthStage.VEGETATIVE]},
            },
            CropType.GROUNDNUT: {
                "tikka": {"humidity": 85, "rainfall": 5, "temp": (25, 32), "stage": [GrowthStage.FLOWERING, GrowthStage.FRUITING]},
                "rust": {"humidity": 80, "temp": (20, 28), "stage": [GrowthStage.VEGETATIVE, GrowthStage.FLOWERING]},
                "stem_rot": {"soil_moisture": 75, "temp": (25, 30), "stage": [GrowthStage.FRUITING]},
            },
            CropType.WHEAT: {
                "yellow_rust": {"temp": (10, 20), "humidity": 90, "stage": [GrowthStage.FLOWERING]},
                "brown_rust": {"temp": (15, 25), "humidity": 80, "stage": [GrowthStage.FLOWERING, GrowthStage.FRUITING]},
                "karnal_bunt": {"humidity": 80, "rainfall": 5, "stage": [GrowthStage.FLOWERING]},
            },
        }

    def assess_risk(
        self,
        crop: CropType,
        growth_stage: GrowthStage,
        weather_forecast: List[Dict],
        soil_moisture: float,
        ndvi: float,
        pest_counts: Dict[str, int]
    ) -> List[DiseaseRisk]:
        rules = self.disease_rules.get(crop, {})
        risks = []
        
        for disease, conditions in rules.items():
            prob = self._calculate_probability(conditions, growth_stage, weather_forecast, soil_moisture, pest_counts)
            
            if prob > 0.1:
                if prob > 0.7:
                    level = "critical"
                elif prob > 0.5:
                    level = "high"
                elif prob > 0.3:
                    level = "medium"
                else:
                    level = "low"
                
                days_to_peak = self._estimate_days_to_peak(prob, weather_forecast)
                action = self._get_action(disease, level, growth_stage)
                trigger = self._get_trigger(conditions, weather_forecast)
                
                risks.append(DiseaseRisk(
                    crop=crop,
                    disease=disease,
                    risk_level=level,
                    probability=round(prob, 2),
                    days_to_peak=days_to_peak,
                    recommended_action=action,
                    weather_trigger=trigger,
                ))
        
        risks.sort(key=lambda x: x.probability, reverse=True)
        return risks[:5]

    def _calculate_probability(
        self,
        conditions: Dict,
        stage: GrowthStage,
        forecast: List[Dict],
        soil_moist: float,
        pests: Dict[str, int]
    ) -> float:
        prob = 0.1
        
        if stage in conditions.get("stage", []):
            prob += 0.2
        
        for w in forecast[:7]:
            if "humidity" in conditions and w.get("humidity_percent", 0) >= conditions["humidity"]:
                prob += 0.15
            if "rainfall" in conditions and w.get("rainfall_mm", 0) >= conditions["rainfall"]:
                prob += 0.15
            if "temp" in conditions:
                tmin, tmax = conditions["temp"]
                if tmin <= w.get("temp_max_c", 0) <= tmax:
                    prob += 0.1
        
        if "soil_moisture" in conditions and soil_moist >= conditions["soil_moisture"]:
            prob += 0.2
        
        if "vector" in conditions and conditions["vector"] in pests and pests[conditions["vector"]] > 5:
            prob += 0.2
        
        return min(0.95, prob)

    def _estimate_days_to_peak(self, prob: float, forecast: List[Dict]) -> int:
        if prob > 0.7:
            return 3
        elif prob > 0.5:
            return 7
        else:
            return 14

    def _get_action(self, disease: str, level: str, stage: GrowthStage) -> str:
        actions = {
            "boll_rot": "Spray copper oxychloride 50% WP @ 2.5g/L + streptomycin 1g/L",
            "leaf_curl": "Control whitefly with neem oil 5% @ 3ml/L or imidacloprid",
            "root_rot": "Drench with carbendazim 50% WP @ 1g/L, improve drainage",
            "tikka": "Spray tebuconazole 25.9% EC @ 1ml/L or hexaconazole 5% SC @ 1ml/L",
            "rust": "Spray propiconazole 25% EC @ 1ml/L at first sign",
            "stem_rot": "Apply trichoderma @ 5kg/ha in soil, avoid waterlogging",
            "yellow_rust": "Spray triazole fungicide immediately, resistant varieties",
            "brown_rust": "Spray propiconazole 25% EC @ 1ml/L",
            "karnal_bunt": "Seed treatment with carbendazim, avoid late irrigation",
        }
        base = actions.get(disease, "Consult local KVK for specific recommendation")
        if level in ["critical", "high"]:
            return f"URGENT: {base}"
        return base

    def _get_trigger(self, conditions: Dict, forecast: List[Dict]) -> Dict[str, Any]:
        trigger = {}
        for w in forecast[:3]:
            if "humidity" in conditions and w.get("humidity_percent", 0) >= conditions["humidity"]:
                trigger["high_humidity"] = w.get("humidity_percent")
            if "rainfall" in conditions and w.get("rainfall_mm", 0) >= conditions["rainfall"]:
                trigger["rainfall"] = w.get("rainfall_mm")
            if "temp" in conditions:
                tmin, tmax = conditions["temp"]
                if tmin <= w.get("temp_max_c", 0) <= tmax:
                    trigger["temperature"] = w.get("temp_max_c")
        return trigger


class RuleBasedIrrigationModel:
    def optimize(
        self,
        crop: CropType,
        stage: GrowthStage,
        soil_type: SoilType,
        et0: float,
        rainfall_forecast: List[float],
        soil_moisture: float,
        field_capacity: float,
        wilting_point: float,
        root_depth_cm: int,
        irrigation_efficiency: float = 0.8
    ) -> Dict[str, Any]:
        kc = self._get_kc(crop, stage)
        etc = et0 * kc
        
        effective_rain = sum(rainfall_forecast[:3]) * 0.7
        net_need = max(0, etc * 3 - effective_rain)
        
        available = (soil_moisture - wilting_point) / (field_capacity - wilting_point) * 100
        
        if available > 70:
            schedule = "skip"
            interval = 5
        elif available > 50:
            schedule = "delay_2_days"
            interval = 4
        elif available > 30:
            schedule = "irrigate_normal"
            interval = 3
        else:
            schedule = "irrigate_urgent"
            interval = 2
        
        depth_mm = net_need / max(1, 3 - interval + 1)
        volume_m3 = depth_mm * 10
        
        return {
            "schedule": schedule,
            "interval_days": interval,
            "depth_mm": round(depth_mm, 1),
            "volume_m3_per_ha": round(volume_m3, 1),
            "etc_mm_day": round(etc, 1),
            "effective_rainfall_mm": round(effective_rain, 1),
            "soil_moisture_percent": round(available, 1),
            "kc": kc,
            "water_saving_tips": [
                "Use drip irrigation" if irrigation_efficiency < 0.9 else "Drip active",
                "Mulch to reduce evaporation",
                "Irrigate early morning (4-6 AM)",
                "Monitor soil moisture at 30cm depth",
            ],
        }

    def _get_kc(self, crop: CropType, stage: GrowthStage) -> float:
        kc_table = {
            CropType.COTTON: {GrowthStage.GERMINATION: 0.35, GrowthStage.VEGETATIVE: 0.75, GrowthStage.FLOWERING: 1.15, GrowthStage.FRUITING: 1.1, GrowthStage.MATURITY: 0.7},
            CropType.GROUNDNUT: {GrowthStage.GERMINATION: 0.4, GrowthStage.VEGETATIVE: 0.8, GrowthStage.FLOWERING: 1.05, GrowthStage.FRUITING: 1.0, GrowthStage.MATURITY: 0.65},
            CropType.WHEAT: {GrowthStage.GERMINATION: 0.3, GrowthStage.VEGETATIVE: 0.85, GrowthStage.FLOWERING: 1.15, GrowthStage.FRUITING: 1.05, GrowthStage.MATURITY: 0.7},
            CropType.BAJRA: {GrowthStage.GERMINATION: 0.3, GrowthStage.VEGETATIVE: 0.7, GrowthStage.FLOWERING: 1.0, GrowthStage.FRUITING: 0.95, GrowthStage.MATURITY: 0.6},
            CropType.MAIZE: {GrowthStage.GERMINATION: 0.3, GrowthStage.VEGETATIVE: 0.75, GrowthStage.FLOWERING: 1.2, GrowthStage.FRUITING: 1.1, GrowthStage.MATURITY: 0.8},
            CropType.CUMIN: {GrowthStage.GERMINATION: 0.3, GrowthStage.VEGETATIVE: 0.6, GrowthStage.FLOWERING: 0.9, GrowthStage.FRUITING: 0.85, GrowthStage.MATURITY: 0.5},
        }
        return kc_table.get(crop, {}).get(stage, 1.0)


class RuleBasedFertilizerModel:
    def optimize(
        self,
        crop: CropType,
        stage: GrowthStage,
        soil_test: Dict[str, float],
        target_yield: float,
        area_hectares: float
    ) -> Dict[str, Any]:
        requirements = {
            CropType.COTTON: {"N": 120, "P": 60, "K": 60},
            CropType.GROUNDNUT: {"N": 20, "P": 40, "K": 40},
            CropType.WHEAT: {"N": 120, "P": 60, "K": 40},
            CropType.BAJRA: {"N": 80, "P": 40, "K": 40},
            CropType.MAIZE: {"N": 150, "P": 75, "K": 60},
            CropType.CUMIN: {"N": 30, "P": 20, "K": 20},
            CropType.CASTOR: {"N": 80, "P": 40, "K": 40},
        }
        
        req = requirements.get(crop, {"N": 100, "P": 50, "K": 50})
        
        if soil_test:
            if soil_test.get("available_n", 0) > 280:
                req["N"] *= 0.8
            elif soil_test.get("available_n", 0) < 140:
                req["N"] *= 1.2
            
            if soil_test.get("available_p", 0) > 25:
                req["P"] *= 0.8
            elif soil_test.get("available_p", 0) < 10:
                req["P"] *= 1.3
            
            if soil_test.get("available_k", 0) > 250:
                req["K"] *= 0.8
            elif soil_test.get("available_k", 0) < 120:
                req["K"] *= 1.2
        
        stage_split = {
            GrowthStage.GERMINATION: {"N": 0.2, "P": 0.5, "K": 0.2},
            GrowthStage.VEGETATIVE: {"N": 0.4, "P": 0.3, "K": 0.3},
            GrowthStage.FLOWERING: {"N": 0.3, "P": 0.1, "K": 0.3},
            GrowthStage.FRUITING: {"N": 0.1, "P": 0.1, "K": 0.2},
            GrowthStage.MATURITY: {"N": 0, "P": 0, "K": 0},
        }
        
        split = stage_split.get(stage, {"N": 0.25, "P": 0.25, "K": 0.25})
        
        fertilizers = []
        
        n_dose = req["N"] * split["N"]
        if n_dose > 0:
            urea_kg = (n_dose / 0.46) * area_hectares
            fertilizers.append({
                "fertilizer": "Urea",
                "dose_kg_per_ha": round(n_dose / 0.46, 1),
                "dose_kg_total": round(urea_kg, 1),
                "cost_inr": round(urea_kg * 6, 0),
                "stage": stage.value,
            })
        
        p_dose = req["P"] * split["P"]
        if p_dose > 0:
            dap_kg = (p_dose / 0.18) * area_hectares
            fertilizers.append({
                "fertilizer": "DAP",
                "dose_kg_per_ha": round(p_dose / 0.18, 1),
                "dose_kg_total": round(dap_kg, 1),
                "cost_inr": round(dap_kg * 24, 0),
                "stage": stage.value,
            })
        
        k_dose = req["K"] * split["K"]
        if k_dose > 0:
            mop_kg = (k_dose / 0.60) * area_hectares
            fertilizers.append({
                "fertilizer": "MOP",
                "dose_kg_per_ha": round(k_dose / 0.60, 1),
                "dose_kg_total": round(mop_kg, 1),
                "cost_inr": round(mop_kg * 18, 0),
                "stage": stage.value,
            })
        
        total_cost = sum(f["cost_inr"] for f in fertilizers)
        
        return {
            "recommended_npk_kg_ha": {k: round(v, 1) for k, v in req.items()},
            "stage_dose_kg_ha": {k: round(req[k] * split[k], 1) for k in ["N", "P", "K"]},
            "fertilizers": fertilizers,
            "total_cost_inr": round(total_cost, 0),
            "organic_alternatives": [
                {"name": "Vermicompost", "dose_t_ha": 5, "cost_inr_ha": 5000},
                {"name": "FYM", "dose_t_ha": 10, "cost_inr_ha": 3000},
                {"name": "Neem Cake", "dose_kg_ha": 500, "cost_inr_ha": 11000},
            ],
        }


ml_models = MLModelManager()


def get_ml_models() -> MLModelManager:
    return ml_models