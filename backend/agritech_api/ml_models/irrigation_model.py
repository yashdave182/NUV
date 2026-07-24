import numpy as np
from datetime import date
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
from pathlib import Path

from agritech_api.schemas import CropType, SoilType, GrowthStage, IrrigationSource, IrrigationMethod


@dataclass
class IrrigationRecommendation:
    schedule: str
    interval_days: int
    depth_mm: float
    volume_m3_per_ha: float
    etc_mm_day: float
    effective_rainfall_mm: float
    soil_moisture_percent: float
    kc: float
    water_saving_tips: List[str]
    cost_estimate_inr: float
    confidence: float


class RuleBasedIrrigationModel:
    def __init__(self):
        self.kc_table = {
            CropType.COTTON: {
                GrowthStage.GERMINATION: 0.35, GrowthStage.VEGETATIVE: 0.75,
                GrowthStage.FLOWERING: 1.15, GrowthStage.FRUITING: 1.10,
                GrowthStage.MATURITY: 0.70, GrowthStage.HARVEST: 0.35,
            },
            CropType.GROUNDNUT: {
                GrowthStage.GERMINATION: 0.40, GrowthStage.VEGETATIVE: 0.80,
                GrowthStage.FLOWERING: 1.05, GrowthStage.FRUITING: 1.00,
                GrowthStage.MATURITY: 0.65, GrowthStage.HARVEST: 0.35,
            },
            CropType.WHEAT: {
                GrowthStage.GERMINATION: 0.30, GrowthStage.VEGETATIVE: 0.85,
                GrowthStage.FLOWERING: 1.15, GrowthStage.FRUITING: 1.05,
                GrowthStage.MATURITY: 0.70, GrowthStage.HARVEST: 0.25,
            },
            CropType.BAJRA: {
                GrowthStage.GERMINATION: 0.30, GrowthStage.VEGETATIVE: 0.70,
                GrowthStage.FLOWERING: 1.00, GrowthStage.FRUITING: 0.95,
                GrowthStage.MATURITY: 0.60, GrowthStage.HARVEST: 0.25,
            },
            CropType.MAIZE: {
                GrowthStage.GERMINATION: 0.30, GrowthStage.VEGETATIVE: 0.75,
                GrowthStage.FLOWERING: 1.20, GrowthStage.FRUITING: 1.10,
                GrowthStage.MATURITY: 0.80, GrowthStage.HARVEST: 0.35,
            },
            CropType.CUMIN: {
                GrowthStage.GERMINATION: 0.30, GrowthStage.VEGETATIVE: 0.60,
                GrowthStage.FLOWERING: 0.90, GrowthStage.FRUITING: 0.85,
                GrowthStage.MATURITY: 0.50, GrowthStage.HARVEST: 0.30,
            },
            CropType.CASTOR: {
                GrowthStage.GERMINATION: 0.35, GrowthStage.VEGETATIVE: 0.70,
                GrowthStage.FLOWERING: 1.05, GrowthStage.FRUITING: 1.00,
                GrowthStage.MATURITY: 0.70, GrowthStage.HARVEST: 0.35,
            },
        }
        
        self.soil_factors = {
            (SoilType.SANDY_LOAM, IrrigationSource.RAINFED): 0.4,
            (SoilType.SANDY_LOAM, IrrigationSource.BOREWELL): 0.9,
            (SoilType.SANDY_LOAM, IrrigationSource.CANAL): 0.8,
            (SoilType.RED_LOAM, IrrigationSource.RAINFED): 0.5,
            (SoilType.RED_LOAM, IrrigationSource.BOREWELL): 1.0,
            (SoilType.RED_LOAM, IrrigationSource.CANAL): 0.9,
            (SoilType.ALLUVIAL, IrrigationSource.RAINFED): 0.7,
            (SoilType.ALLUVIAL, IrrigationSource.BOREWELL): 1.0,
            (SoilType.ALLUVIAL, IrrigationSource.CANAL): 1.0,
            (SoilType.BLACK_COTTON, IrrigationSource.RAINFED): 0.6,
            (SoilType.BLACK_COTTON, IrrigationSource.BOREWELL): 1.1,
            (SoilType.BLACK_COTTON, IrrigationSource.CANAL): 1.0,
            (SoilType.CLAY, IrrigationSource.RAINFED): 0.6,
            (SoilType.CLAY, IrrigationSource.BOREWELL): 1.0,
            (SoilType.CLAY, IrrigationSource.CANAL): 1.0,
        }
        
        self.efficiency = {
            IrrigationMethod.FLOOD: 0.6,
            IrrigationMethod.FURROW: 0.65,
            IrrigationMethod.SPRINKLER: 0.75,
            IrrigationMethod.DRIP: 0.9,
        }

    def _get_kc(self, crop: CropType, stage: GrowthStage) -> float:
        return self.kc_table.get(crop, {}).get(stage, 1.0)

    def optimize(
        self,
        crop: CropType,
        growth_stage: GrowthStage,
        soil_type: SoilType,
        soil_moisture: float,
        weather_forecast: List[Dict],
        et0_forecast: List[float],
        area_hectares: float,
        irrigation_method: str,
        water_cost_per_m3: float
    ) -> Dict[str, Any]:
        kc = self._get_kc(crop, growth_stage)
        avg_et0 = np.mean(et0_forecast[:3]) if et0_forecast else 5.0
        etc = avg_et0 * kc
        
        effective_rain = sum(w.get("rainfall_mm", 0) for w in weather_forecast[:3]) * 0.7
        
        field_capacity = {"SANDY_LOAM": 25, "RED_LOAM": 30, "ALLUVIAL": 35, "BLACK_COTTON": 40, "CLAY": 45}.get(soil_type.value, 30)
        wilting_point = {"SANDY_LOAM": 10, "RED_LOAM": 12, "ALLUVIAL": 15, "BLACK_COTTON": 20, "CLAY": 25}.get(soil_type.value, 15)
        
        available = (soil_moisture - wilting_point) / (field_capacity - wilting_point) * 100
        available = max(0, min(100, available))
        
        net_need_3d = max(0, etc * 3 - effective_rain)
        
        if available > 75:
            schedule = "skip"
            interval = 5
        elif available > 55:
            schedule = "delay_2_days"
            interval = 4
        elif available > 35:
            schedule = "irrigate_normal"
            interval = 3
        elif available > 20:
            schedule = "irrigate_soon"
            interval = 2
        else:
            schedule = "irrigate_urgent"
            interval = 1
        
        if growth_stage in [GrowthStage.FLOWERING, GrowthStage.FRUITING]:
            if interval > 3:
                interval = 3
                schedule = "irrigate_normal"
        
        depth_mm = net_need_3d / max(1, 4 - interval)
        volume_m3 = depth_mm * 10
        gross_irrigation = volume_m3 / self.efficiency.get(IrrigationMethod(irrigation_method), 0.75)
        
        cost = gross_irrigation * water_cost_per_m3 * area_hectares
        
        tips = [
            f"Use {irrigation_method} irrigation" if irrigation_method != "drip" else "Drip irrigation active - excellent efficiency",
            "Irrigate early morning (4-6 AM) to minimize evaporation",
            "Mulch to reduce soil evaporation by 30-50%",
            "Monitor soil moisture at 30 cm depth with probe/sensor",
            "Skip if rainfall > 15mm forecast in next 2 days",
        ]
        
        if available < 30:
            tips.insert(0, "URGENT: Soil moisture critical - irrigate immediately")
        
        return {
            "schedule": schedule,
            "interval_days": interval,
            "depth_mm": round(depth_mm, 1),
            "volume_m3_per_ha": round(gross_irrigation, 1),
            "etc_mm_day": round(etc, 1),
            "effective_rainfall_mm": round(effective_rain, 1),
            "soil_moisture_percent": round(available, 1),
            "kc": kc,
            "water_saving_tips": tips,
            "cost_estimate_inr": round(cost, 0),
            "confidence": 0.8,
        }


class IrrigationOptimizer:
    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.metrics = None

    def generate_training_data(self, n_samples: int = 15000) -> Tuple[np.ndarray, np.ndarray]:
        np.random.seed(42)
        rule_model = RuleBasedIrrigationModel()
        
        X = []
        y = []
        
        crops = list(CropType)
        soils = list(SoilType)
        stages = list(GrowthStage)
        sources = list(IrrigationSource)
        methods = list(IrrigationMethod)
        
        import random
        for _ in range(n_samples):
            crop = random.choice(crops)
            stage = random.choice(stages)
            soil = random.choice(soils)
            source = random.choice(sources)
            method = random.choice(methods)
            
            soil_moist = np.random.uniform(10, 90)
            
            weather = []
            et0 = []
            for i in range(7):
                tmax = np.random.uniform(20, 45)
                tmin = np.random.uniform(10, min(30, tmax - 0.1))
                hum = np.random.uniform(30, 95)
                wind = np.random.uniform(2, 25)
                rain = np.random.exponential(3)
                
                weather.append({
                    "temp_max_c": tmax,
                    "temp_min_c": tmin,
                    "humidity_percent": hum,
                    "rainfall_mm": rain,
                    "wind_speed_kmph": wind,
                })
                
                et = 0.0023 * (tmax + tmin + 17.8) * np.sqrt(tmax - tmin) * (100 - hum) / 100
                et0.append(max(0, et))
            
            area = np.random.uniform(0.5, 20)
            water_cost = np.random.uniform(0.5, 5)
            
            features = [
                list(CropType).index(crop),
                list(GrowthStage).index(stage),
                list(SoilType).index(soil),
                list(IrrigationSource).index(source),
                list(IrrigationMethod).index(method),
                soil_moist,
                area,
                water_cost,
                np.mean([w["temp_max_c"] for w in weather]),
                np.mean([w["humidity_percent"] for w in weather]),
                np.sum([w["rainfall_mm"] for w in weather]),
                np.mean([w["wind_speed_kmph"] for w in weather]),
                np.mean(et0),
                np.std(et0),
            ]
            
            result = rule_model.optimize(
                crop, stage, soil, soil_moist, weather, et0,
                area, method.value, water_cost
            )
            
            target = [
                result["interval_days"],
                result["depth_mm"],
                result["volume_m3_per_ha"],
                result["cost_estimate_inr"],
            ]
            
            X.append(features)
            y.append(target)
        
        self.feature_names = [
            "crop_encoded", "stage_encoded", "soil_encoded", "source_encoded",
            "method_encoded", "soil_moisture", "area_hectares", "water_cost",
            "avg_temp_max", "avg_humidity", "total_rainfall", "avg_wind",
            "avg_et0", "et0_std"
        ]
        
        return np.array(X), np.array(y)

    def train(self, X: np.ndarray = None, y: np.ndarray = None, n_samples: int = 15000):
        if X is None or y is None:
            X, y = self.generate_training_data(n_samples)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.models = {}
        targets = ["interval_days", "depth_mm", "volume_m3_per_ha", "cost_estimate_inr"]
        
        for i, target_name in enumerate(targets):
            model = GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=5,
                subsample=0.8,
                random_state=42
            )
            model.fit(X_train_scaled, y_train[:, i])
            
            score = model.score(X_test_scaled, y_test[:, i])
            self.models[target_name] = model
            print(f"[Irrigation] {target_name} R²: {score:.3f}")
        
        self.metrics = {
            "training_date": date.today().isoformat(),
            "n_samples": len(X),
            "target_scores": {t: m.score(X_test_scaled, y_test[:, i]) 
                             for i, (t, m) in enumerate(self.models.items())},
        }
        
        self.save()
        return self.metrics

    def predict(
        self,
        crop: CropType,
        stage: GrowthStage,
        soil: SoilType,
        source: IrrigationSource,
        method: IrrigationMethod,
        soil_moist: float,
        area: float,
        water_cost: float,
        weather: List[Dict],
        et0: List[float]
    ) -> Dict[str, Any]:
        if not self.models:
            self.load()
        
        if not self.models:
            rule = RuleBasedIrrigationModel()
            return rule.optimize(crop, stage, soil, soil_moist, weather, et0, area, method.value, water_cost)
        
        features = np.array([[
            list(CropType).index(crop),
            list(GrowthStage).index(stage),
            list(SoilType).index(soil),
            list(IrrigationSource).index(source),
            list(IrrigationMethod).index(method),
            soil_moist,
            area,
            water_cost,
            np.mean([w["temp_max_c"] for w in weather]),
            np.mean([w["humidity_percent"] for w in weather]),
            np.sum([w["rainfall_mm"] for w in weather]),
            np.mean([w["wind_speed_kmph"] for w in weather]),
            np.mean(et0),
            np.std(et0),
        ]])
        
        features_scaled = self.scaler.transform(features)
        
        predictions = {}
        for target_name, model in self.models.items():
            predictions[target_name] = model.predict(features_scaled)[0]
        
        kc = self._get_kc(crop, stage)
        avg_et0 = np.mean(et0)
        etc = avg_et0 * kc
        effective_rain = sum(w.get("rainfall_mm", 0) for w in weather[:3]) * 0.7
        
        return {
            "schedule": self._schedule_from_interval(predictions["interval_days"]),
            "interval_days": max(1, min(7, round(predictions["interval_days"]))),
            "depth_mm": max(0, round(predictions["depth_mm"], 1)),
            "volume_m3_per_ha": max(0, round(predictions["volume_m3_per_ha"], 1)),
            "etc_mm_day": round(etc, 1),
            "effective_rainfall_mm": round(effective_rain, 1),
            "kc": kc,
            "cost_estimate_inr": max(0, round(predictions["cost_estimate_inr"], 0)),
            "confidence": 0.85,
        }

    def _get_kc(self, crop: CropType, stage: GrowthStage) -> float:
        kc_table = {
            CropType.COTTON: {GrowthStage.GERMINATION: 0.35, GrowthStage.VEGETATIVE: 0.75, GrowthStage.FLOWERING: 1.15, GrowthStage.FRUITING: 1.10, GrowthStage.MATURITY: 0.70},
            CropType.GROUNDNUT: {GrowthStage.GERMINATION: 0.40, GrowthStage.VEGETATIVE: 0.80, GrowthStage.FLOWERING: 1.05, GrowthStage.FRUITING: 1.00, GrowthStage.MATURITY: 0.65},
            CropType.WHEAT: {GrowthStage.GERMINATION: 0.30, GrowthStage.VEGETATIVE: 0.85, GrowthStage.FLOWERING: 1.15, GrowthStage.FRUITING: 1.05, GrowthStage.MATURITY: 0.70},
            CropType.BAJRA: {GrowthStage.GERMINATION: 0.30, GrowthStage.VEGETATIVE: 0.70, GrowthStage.FLOWERING: 1.00, GrowthStage.FRUITING: 0.95, GrowthStage.MATURITY: 0.60},
            CropType.MAIZE: {GrowthStage.GERMINATION: 0.30, GrowthStage.VEGETATIVE: 0.75, GrowthStage.FLOWERING: 1.20, GrowthStage.FRUITING: 1.10, GrowthStage.MATURITY: 0.80},
            CropType.CUMIN: {GrowthStage.GERMINATION: 0.30, GrowthStage.VEGETATIVE: 0.60, GrowthStage.FLOWERING: 0.90, GrowthStage.FRUITING: 0.85, GrowthStage.MATURITY: 0.50},
            CropType.CASTOR: {GrowthStage.GERMINATION: 0.35, GrowthStage.VEGETATIVE: 0.70, GrowthStage.FLOWERING: 1.05, GrowthStage.FRUITING: 1.00, GrowthStage.MATURITY: 0.70},
        }
        return kc_table.get(crop, {}).get(stage, 1.0)

    def _schedule_from_interval(self, interval: float) -> str:
        if interval <= 1: return "irrigate_urgent"
        elif interval <= 2: return "irrigate_soon"
        elif interval <= 3: return "irrigate_normal"
        elif interval <= 4: return "delay_2_days"
        else: return "skip"

    def save(self):
        self.model_dir.mkdir(exist_ok=True)
        path = self.model_dir / "irrigation_optimizer.joblib"
        joblib.dump({
            "models": self.models,
            "scaler": self.scaler,
            "feature_names": self.feature_names,
            "metrics": self.metrics,
        }, path)

    def load(self):
        path = self.model_dir / "irrigation_optimizer.joblib"
        if path.exists():
            data = joblib.load(path)
            self.models = data["models"]
            self.scaler = data["scaler"]
            self.feature_names = data["feature_names"]
            self.metrics = data.get("metrics")
            return True
        return False


@dataclass
class FertilizerRecommendation:
    recommended_npk_kg_ha: Dict[str, float]
    stage_dose_kg_ha: Dict[str, float]
    fertilizers: List[Dict[str, Any]]
    total_cost_inr: float
    organic_alternatives: List[Dict[str, Any]]
    deficiency_risks: List[str]
    efficiency_score: float


class RuleBasedFertilizerModel:
    def __init__(self):
        self.requirements = {
            CropType.COTTON: {"N": 120, "P": 60, "K": 60, "S": 20, "Zn": 5},
            CropType.GROUNDNUT: {"N": 20, "P": 40, "K": 40, "S": 15, "Zn": 3},
            CropType.WHEAT: {"N": 120, "P": 60, "K": 40, "S": 20, "Zn": 5},
            CropType.BAJRA: {"N": 80, "P": 40, "K": 40, "S": 15, "Zn": 3},
            CropType.MAIZE: {"N": 150, "P": 75, "K": 60, "S": 20, "Zn": 5},
            CropType.CUMIN: {"N": 30, "P": 20, "K": 20, "S": 10, "Zn": 2},
            CropType.CASTOR: {"N": 80, "P": 40, "K": 40, "S": 15, "Zn": 3},
            CropType.SESAME: {"N": 40, "P": 20, "K": 20, "S": 15, "Zn": 2},
            CropType.TOBACCO: {"N": 100, "P": 50, "K": 80, "S": 15, "Zn": 2},
            CropType.CHILLI: {"N": 100, "P": 50, "K": 50, "S": 20, "Zn": 5},
            CropType.ONION: {"N": 100, "P": 50, "K": 50, "S": 25, "Zn": 5},
            CropType.POTATO: {"N": 150, "P": 80, "K": 150, "S": 20, "Zn": 3},
        }
        
        self.stage_split = {
            GrowthStage.GERMINATION: {"N": 0.20, "P": 0.50, "K": 0.20, "S": 0.30, "Zn": 0.50},
            GrowthStage.VEGETATIVE: {"N": 0.40, "P": 0.30, "K": 0.30, "S": 0.40, "Zn": 0.30},
            GrowthStage.FLOWERING: {"N": 0.30, "P": 0.10, "K": 0.30, "S": 0.20, "Zn": 0.10},
            GrowthStage.FRUITING: {"N": 0.10, "P": 0.10, "K": 0.20, "S": 0.10, "Zn": 0.10},
            GrowthStage.MATURITY: {"N": 0.00, "P": 0.00, "K": 0.00, "S": 0.00, "Zn": 0.00},
        }
        
        self.fertilizer_specs = {
            "Urea": {"N": 0.46, "cost_per_kg": 6.0},
            "DAP": {"N": 0.18, "P": 0.46, "cost_per_kg": 24.0},
            "MOP": {"K": 0.60, "cost_per_kg": 18.0},
            "SSP": {"P": 0.16, "S": 0.11, "cost_per_kg": 8.0},
            "Zinc_Sulphate": {"Zn": 0.33, "S": 0.17, "cost_per_kg": 45.0},
            "Gypsum": {"S": 0.17, "Ca": 0.22, "cost_per_kg": 3.0},
            "Ammonium_Sulphate": {"N": 0.21, "S": 0.24, "cost_per_kg": 15.0},
        }

    def optimize(
        self,
        crop: CropType,
        growth_stage: GrowthStage,
        soil_test: Dict[str, float],
        target_yield: float,
        area_hectares: float,
        fertilizer_prices: Dict[str, float],
        previous_applications: List[Dict]
    ) -> Dict[str, Any]:
        req = self.requirements.get(crop, {"N": 100, "P": 50, "K": 50, "S": 15, "Zn": 2})
        
        if target_yield:
            base_yield = {
                CropType.COTTON: 2.5, CropType.GROUNDNUT: 2.0, CropType.WHEAT: 4.5,
                CropType.BAJRA: 2.5, CropType.MAIZE: 5.5, CropType.CUMIN: 0.6,
                CropType.CASTOR: 1.8, CropType.SESAME: 0.8, CropType.CHILLI: 1.8,
                CropType.ONION: 25, CropType.POTATO: 20,
            }.get(crop, 2.0)
            
            yield_factor = target_yield / base_yield
            yield_factor = max(0.8, min(1.5, yield_factor))
            
            for k in req:
                req[k] = round(req[k] * yield_factor)
        
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
            
            if soil_test.get("zn_ppm", 1) < 0.6:
                req["Zn"] = max(req.get("Zn", 5), 25)
            if soil_test.get("fe_ppm", 1) < 4.5:
                req["Fe"] = req.get("Fe", 0) + 20
        
        split = self.stage_split.get(growth_stage, {"N": 0.25, "P": 0.25, "K": 0.25, "S": 0.25, "Zn": 0.25})
        
        fertilizers = []
        
        n_dose = req.get("N", 0) * split.get("N", 0)
        if n_dose > 0:
            urea_kg_ha = n_dose / 0.46
            cost = urea_kg_ha * area_hectares * fertilizer_prices.get("Urea", 6)
            fertilizers.append({
                "fertilizer": "Urea",
                "dose_kg_per_ha": round(urea_kg_ha, 1),
                "dose_kg_total": round(urea_kg_ha * area_hectares, 1),
                "application_stage": growth_stage.value,
                "application_method": "Top dressing" if growth_stage != GrowthStage.GERMINATION else "Basal",
                "cost_inr": round(cost, 0),
                "nutrient_supplied": {"N": round(n_dose, 1)},
            })
        
        p_dose = req.get("P", 0) * split.get("P", 0)
        if p_dose > 0:
            dap_kg_ha = p_dose / 0.46
            n_from_dap = dap_kg_ha * 0.18
            cost = dap_kg_ha * area_hectares * fertilizer_prices.get("DAP", 24)
            fertilizers.append({
                "fertilizer": "DAP",
                "dose_kg_per_ha": round(dap_kg_ha, 1),
                "dose_kg_total": round(dap_kg_ha * area_hectares, 1),
                "application_stage": growth_stage.value,
                "application_method": "Basal placement",
                "cost_inr": round(cost, 0),
                "nutrient_supplied": {"P": round(p_dose, 1), "N": round(n_from_dap, 1)},
            })
        
        k_dose = req.get("K", 0) * split.get("K", 0)
        if k_dose > 0:
            mop_kg_ha = k_dose / 0.60
            cost = mop_kg_ha * area_hectares * fertilizer_prices.get("MOP", 18)
            fertilizers.append({
                "fertilizer": "MOP",
                "dose_kg_per_ha": round(mop_kg_ha, 1),
                "dose_kg_total": round(mop_kg_ha * area_hectares, 1),
                "application_stage": growth_stage.value,
                "application_method": "Broadcast",
                "cost_inr": round(cost, 0),
                "nutrient_supplied": {"K": round(k_dose, 1)},
            })
        
        s_dose = req.get("S", 0) * split.get("S", 0)
        if s_dose > 0:
            gypsum_kg_ha = s_dose / 0.17
            cost = gypsum_kg_ha * area_hectares * fertilizer_prices.get("Gypsum", 3)
            fertilizers.append({
                "fertilizer": "Gypsum",
                "dose_kg_per_ha": round(gypsum_kg_ha, 1),
                "dose_kg_total": round(gypsum_kg_ha * area_hectares, 1),
                "application_stage": "Basal",
                "application_method": "Broadcast",
                "cost_inr": round(cost, 0),
                "nutrient_supplied": {"S": round(s_dose, 1)},
            })
        
        zn_dose = req.get("Zn", 0) * split.get("Zn", 0)
        if zn_dose > 0:
            zinc_kg_ha = zn_dose / 0.33
            cost = zinc_kg_ha * area_hectares * fertilizer_prices.get("Zinc_Sulphate", 45)
            fertilizers.append({
                "fertilizer": "Zinc Sulphate",
                "dose_kg_per_ha": round(zinc_kg_ha, 1),
                "dose_kg_total": round(zinc_kg_ha * area_hectares, 1),
                "application_stage": "Basal",
                "application_method": "Soil application",
                "cost_inr": round(cost, 0),
                "nutrient_supplied": {"Zn": round(zn_dose, 1)},
            })
        
        total_cost = sum(f["cost_inr"] for f in fertilizers)
        
        deficiencies = []
        if soil_test:
            if soil_test.get("available_n", 0) < 140: deficiencies.append("Nitrogen")
            if soil_test.get("available_p", 0) < 10: deficiencies.append("Phosphorus")
            if soil_test.get("available_k", 0) < 120: deficiencies.append("Potassium")
            if soil_test.get("zn_ppm", 1) < 0.6: deficiencies.append("Zinc")
            if soil_test.get("fe_ppm", 1) < 4.5: deficiencies.append("Iron")
            if soil_test.get("ph", 7) > 8.5: deficiencies.append("High pH - micronutrient availability limited")
            if soil_test.get("ph", 7) < 5.5: deficiencies.append("Low pH - aluminum toxicity risk")
        
        organic_alts = [
            {"name": "Vermicompost", "dose_t_per_ha": 5, "nutrients": "N-P-K + micros", "cost_inr_per_ha": 5000},
            {"name": "FYM", "dose_t_per_ha": 10, "nutrients": "N-P-K + organic matter", "cost_inr_per_ha": 3000},
            {"name": "Neem Cake", "dose_kg_per_ha": 500, "nutrients": "N + pest repellent", "cost_inr_per_ha": 11000},
            {"name": "Biofertilizers (Azotobacter/PSB)", "dose_kg_per_ha": 5, "nutrients": "N-fixing/P-solubilizing", "cost_inr_per_ha": 300},
            {"name": "Green Manuring (Sesbania)", "dose_t_per_ha": 15, "nutrients": "N + organic matter", "cost_inr_per_ha": 2500},
        ]
        
        return {
            "recommended_npk_kg_ha": {k: round(v, 1) for k, v in req.items()},
            "stage_dose_kg_ha": {k: round(req.get(k, 0) * split.get(k, 0), 1) for k in ["N", "P", "K", "S", "Zn"]},
            "fertilizers": fertilizers,
            "total_cost_inr": round(total_cost, 0),
            "organic_alternatives": organic_alts,
            "deficiency_risks": deficiencies,
            "efficiency_score": 0.85,
        }


class FertilizerOptimizer:
    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_names = []
        self.metrics = None

    def generate_training_data(self, n_samples: int = 15000):
        np.random.seed(42)
        rule_model = RuleBasedFertilizerModel()
        
        X = []
        y = []
        
        crops = list(CropType)
        stages = list(GrowthStage)
        
        import random
        for _ in range(n_samples):
            crop = random.choice(crops)
            stage = random.choice(stages)
            
            soil_test = {
                "available_n": np.random.uniform(80, 350),
                "available_p": np.random.uniform(5, 40),
                "available_k": np.random.uniform(60, 300),
                "zn_ppm": np.random.uniform(0.3, 1.5),
                "fe_ppm": np.random.uniform(2, 12),
                "ph": np.random.uniform(5.5, 8.5),
            }
            
            target_yield = np.random.uniform(0.5, 3.0) * {
                CropType.COTTON: 2.5, CropType.GROUNDNUT: 2.0, CropType.WHEAT: 4.5,
                CropType.MAIZE: 5.5, CropType.CUMIN: 0.6, CropType.CASTOR: 1.8,
            }.get(crop, 2.0)
            
            area = np.random.uniform(0.5, 20)
            
            prices = {
                "Urea": np.random.uniform(5.5, 7),
                "DAP": np.random.uniform(22, 26),
                "MOP": np.random.uniform(16, 20),
                "Gypsum": np.random.uniform(2.5, 4),
                "Zinc_Sulphate": np.random.uniform(40, 50),
            }
            
            prev_apps = []
            for _ in range(np.random.randint(0, 3)):
                prev_apps.append({
                    "fertilizer": random.choice(["Urea", "DAP", "MOP"]),
                    "dose_kg_ha": np.random.uniform(20, 100),
                    "days_ago": np.random.randint(7, 60),
                })
            
            features = [
                list(CropType).index(crop),
                list(GrowthStage).index(stage),
                soil_test["available_n"], soil_test["available_p"], soil_test["available_k"],
                soil_test["zn_ppm"], soil_test["fe_ppm"], soil_test["ph"],
                target_yield, area,
                prices["Urea"], prices["DAP"], prices["MOP"], prices["Gypsum"], prices["Zinc_Sulphate"],
                len(prev_apps),
            ]
            
            result = rule_model.optimize(crop, stage, soil_test, target_yield, area, prices, prev_apps)
            
            target = [
                result["recommended_npk_kg_ha"].get("N", 0),
                result["recommended_npk_kg_ha"].get("P", 0),
                result["recommended_npk_kg_ha"].get("K", 0),
                result["total_cost_inr"],
            ]
            
            X.append(features)
            y.append(target)
        
        self.feature_names = [
            "crop_encoded", "stage_encoded", "soil_n", "soil_p", "soil_k",
            "soil_zn", "soil_fe", "soil_ph", "target_yield", "area_hectares",
            "urea_price", "dap_price", "mop_price", "gypsum_price", "zinc_price",
            "prev_app_count"
        ]
        
        return np.array(X), np.array(y)

    def train(self, X=None, y=None, n_samples=15000):
        if X is None or y is None:
            X, y = self.generate_training_data(n_samples)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        targets = ["rec_N", "rec_P", "rec_K", "total_cost"]
        
        for i, target_name in enumerate(targets):
            model = GradientBoostingRegressor(
                n_estimators=200, learning_rate=0.1, max_depth=5, subsample=0.8, random_state=42
            )
            model.fit(X_train_scaled, y_train[:, i])
            score = model.score(X_test_scaled, y_test[:, i])
            self.models[target_name] = model
            print(f"[Fertilizer] {target_name} R²: {score:.3f}")
        
        self.metrics = {
            "training_date": date.today().isoformat(),
            "n_samples": len(X),
            "target_scores": {t: self.models[t].score(X_test_scaled, y_test[:, i]) 
                             for i, t in enumerate(targets)},
        }
        
        self.save()
        return self.metrics

    def predict(self, crop, stage, soil_test, target_yield, area, prices, prev_apps):
        if not self.models:
            self.load()
        
        if not self.models:
            rule = RuleBasedFertilizerModel()
            return rule.optimize(crop, stage, soil_test, target_yield, area, prices, prev_apps)
        
        features = np.array([[
            list(CropType).index(crop),
            list(GrowthStage).index(stage),
            soil_test.get("available_n", 200), soil_test.get("available_p", 18), soil_test.get("available_k", 180),
            soil_test.get("zn_ppm", 0.7), soil_test.get("fe_ppm", 4.5), soil_test.get("ph", 7.2),
            target_yield or 2.0, area,
            prices.get("Urea", 6), prices.get("DAP", 24), prices.get("MOP", 18), 
            prices.get("Gypsum", 3), prices.get("Zinc_Sulphate", 45),
            len(prev_apps),
        ]])
        
        features_scaled = self.scaler.transform(features)
        
        predictions = {}
        for target_name, model in self.models.items():
            predictions[target_name] = model.predict(features_scaled)[0]
        
        rule = RuleBasedFertilizerModel()
        rule_result = rule.optimize(crop, stage, soil_test, target_yield, area, prices, prev_apps)
        
        rule_result["recommended_npk_kg_ha"]["N"] = round(predictions["rec_N"])
        rule_result["recommended_npk_kg_ha"]["P"] = round(predictions["rec_P"])
        rule_result["recommended_npk_kg_ha"]["K"] = round(predictions["rec_K"])
        rule_result["total_cost_inr"] = round(predictions["total_cost"])
        
        return rule_result

    def save(self):
        self.model_dir.mkdir(exist_ok=True)
        path = self.model_dir / "fertilizer_optimizer.joblib"
        joblib.dump({
            "models": self.models,
            "scaler": self.scaler,
            "feature_names": self.feature_names,
            "metrics": self.metrics,
        }, path)

    def load(self):
        path = self.model_dir / "fertilizer_optimizer.joblib"
        if path.exists():
            data = joblib.load(path)
            self.models = data["models"]
            self.scaler = data["scaler"]
            self.feature_names = data["feature_names"]
            self.metrics = data.get("metrics")
            return True
        return False