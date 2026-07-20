import numpy as np
import pandas as pd
from datetime import date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
from pathlib import Path

from agritech_api.schemas import CropType, SoilType, GrowthStage, IrrigationSource


@dataclass
class YieldPrediction:
    predicted_yield_tonnes_ha: float
    confidence_interval: Tuple[float, float]
    confidence_level: float
    key_factors: List[str]
    risk_factors: List[str]
    recommendation: str


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
            CropType.TOBACCO: 1.5,
            CropType.GREEN_GRAM: 1.0,
            CropType.BLACK_GRAM: 0.9,
            CropType.PIGEON_PEA: 1.2,
            CropType.CHILLI: 1.8,
            CropType.ONION: 25.0,
            CropType.POTATO: 20.0,
            CropType.BANANA: 45.0,
            CropType.PAPAYA: 50.0,
            CropType.MANGO: 8.0,
        }
        
        self.soil_factors = {
            SoilType.BLACK_COTTON: 1.05,
            SoilType.ALLUVIAL: 1.1,
            SoilType.RED_LOAM: 0.95,
            SoilType.SANDY_LOAM: 0.85,
            SoilType.CLAY: 0.9,
            SoilType.SALINE: 0.6,
            SoilType.ALKALINE: 0.7,
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
        pest_pressure: float,
        disease_pressure: float,
        ndvi_avg: float
    ) -> YieldPrediction:
        base = self.base_yields.get(self.crop, 2.0)
        
        soil_factor = self.soil_factors.get(soil_type, 1.0)
        
        temp_factor = 1.0
        if temperature_avg > 38:
            temp_factor = 0.85
        elif temperature_avg > 35:
            temp_factor = 0.95
        elif temperature_avg < 15:
            temp_factor = 0.9
        
        rain_factor = 1.0
        optimal_rain = {
            CropType.COTTON: 700, CropType.GROUNDNUT: 500, CropType.WHEAT: 450,
            CropType.BAJRA: 400, CropType.MAIZE: 550, CropType.CUMIN: 300,
            CropType.CASTOR: 500,
        }.get(self.crop, 500)
        
        if rainfall_total < optimal_rain * 0.5:
            rain_factor = 0.7 + 0.3 * (rainfall_total / (optimal_rain * 0.5))
        elif rainfall_total > optimal_rain * 1.5:
            rain_factor = 0.85
        
        n_factor = min(1.2, max(0.5, soil_n / 200))
        p_factor = min(1.15, max(0.6, soil_p / 20))
        k_factor = min(1.1, max(0.6, soil_k / 180))
        soil_fertility = (n_factor + p_factor + k_factor) / 3
        
        ph_factor = 1.0
        if soil_ph < 6.0 or soil_ph > 8.0:
            ph_factor = 0.85
        elif soil_ph < 6.5 or soil_ph > 7.5:
            ph_factor = 0.95
        
        irrigation_factor = min(1.2, 0.6 + irrigation_count * 0.08)
        
        fert_factor = min(1.15, 0.85 + (fertilizer_n / 120) * 0.2)
        
        stress_factor = max(0.4, 1.0 - pest_pressure - disease_pressure)
        
        ndvi_factor = 0.5 + ndvi_avg * 0.6
        
        management_score = (
            irrigation_factor * 0.2 +
            fert_factor * 0.2 +
            soil_fertility * 0.3 +
            ph_factor * 0.1 +
            stress_factor * 0.2
        )
        
        weather_score = temp_factor * rain_factor * 0.5 + 0.5
        
        predicted = base * soil_factor * weather_score * management_score * ndvi_factor
        predicted = max(base * 0.3, min(base * 2.0, predicted))
        
        ci_width = predicted * 0.2
        
        key_factors = []
        if soil_factor > 1.0: key_factors.append(f"Favorable {soil_type.value} soil")
        if temp_factor < 0.95: key_factors.append("Heat stress reducing yield")
        if rain_factor < 0.9: key_factors.append("Water deficit limiting yield")
        if soil_fertility > 1.1: key_factors.append("Good soil fertility")
        if management_score > 1.0: key_factors.append("Good management practices")
        if ndvi_factor > 1.0: key_factors.append("Healthy crop vigor (high NDVI)")
        
        risk_factors = []
        if temp_factor < 0.95: risk_factors.append("High temperature stress")
        if rain_factor < 0.9: risk_factors.append("Moisture deficit")
        if pest_pressure > 0.15: risk_factors.append("High pest pressure")
        if disease_pressure > 0.15: risk_factors.append("High disease pressure")
        if soil_fertility < 0.8: risk_factors.append("Low soil fertility")
        if irrigation_count < 3: risk_factors.append("Insufficient irrigation")
        
        recs = []
        if rain_factor < 0.9: recs.append("Increase irrigation frequency")
        if soil_fertility < 0.9: recs.append("Apply balanced NPK fertilizer")
        if pest_pressure > 0.15: recs.append("Implement IPM for pest control")
        if disease_pressure > 0.15: recs.append("Preventive fungicide application")
        if ndvi_factor < 0.9: recs.append("Monitor crop health, check for nutrient deficiency")
        
        return YieldPrediction(
            predicted_yield_tonnes_ha=round(predicted, 2),
            confidence_interval=(round(predicted - ci_width, 2), round(predicted + ci_width, 2)),
            confidence_level=0.75,
            key_factors=key_factors,
            risk_factors=risk_factors,
            recommendation="; ".join(recs) if recs else "Maintain current practices",
        )


class YieldPredictor:
    def __init__(self, crop: CropType, model_dir: str = "models"):
        self.crop = crop
        self.model_dir = Path(model_dir)
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.metrics = None
        
    def generate_synthetic_data(self, n_samples: int = 10000) -> Tuple[np.ndarray, np.ndarray]:
        np.random.seed(42)
        
        data = []
        yields = []
        
        base = RuleBasedYieldModel(self.crop).base_yields.get(self.crop, 2.0)
        
        for _ in range(n_samples):
            area = np.random.uniform(0.5, 20)
            soil_type = np.random.randint(0, len(SoilType))
            das = np.random.randint(10, 180)
            
            ph = np.random.uniform(5.5, 8.5)
            ec = np.random.uniform(0.1, 2.0)
            oc = np.random.uniform(0.2, 1.2)
            avail_n = np.random.uniform(80, 350)
            avail_p = np.random.uniform(5, 40)
            avail_k = np.random.uniform(60, 300)
            
            fert_n = np.random.uniform(0, 200)
            fert_p = np.random.uniform(0, 100)
            fert_k = np.random.uniform(0, 100)
            irrigation = np.random.randint(0, 15)
            
            temp_max = np.random.uniform(20, 45)
            temp_min = np.random.uniform(10, 30)
            humidity = np.random.uniform(30, 95)
            rainfall = np.random.uniform(0, 800)
            wind = np.random.uniform(2, 30)
            
            ndvi = np.random.uniform(0.1, 0.9)
            soil_moist = np.random.uniform(10, 90)
            health = np.random.uniform(30, 95)
            
            features = [
                area, self._crop_encoded(), soil_type, das,
                ph, ec, oc, avail_n, avail_p, avail_k,
                fert_n, fert_p, fert_k, irrigation,
                temp_max, temp_min, humidity, rainfall, wind,
                ndvi, soil_moist, health,
            ]
            
            model = RuleBasedYieldModel(self.crop)
            pred = model.predict(
                area_hectares=area,
                soil_type=list(SoilType)[soil_type],
                sowing_date=date.today() - timedelta(days=das),
                temperature_avg=(temp_max + temp_min) / 2,
                rainfall_total=rainfall,
                humidity_avg=humidity,
                soil_n=avail_n,
                soil_p=avail_p,
                soil_k=avail_k,
                soil_ph=ph,
                irrigation_count=irrigation,
                fertilizer_n=fert_n,
                fertilizer_p=fert_p,
                fertilizer_k=fert_k,
                pest_pressure=np.random.uniform(0, 0.3),
                disease_pressure=np.random.uniform(0, 0.3),
                ndvi_avg=ndvi,
            )
            
            yield_val = pred.predicted_yield_tonnes_ha * np.random.uniform(0.9, 1.1)
            
            data.append(features)
            yields.append(yield_val)
        
        self.feature_names = [
            "area_hectares", "crop_encoded", "soil_encoded", "days_after_sowing",
            "ph", "ec", "organic_carbon", "available_n", "available_p", "available_k",
            "fertilizer_n", "fertilizer_p", "fertilizer_k", "irrigation_count",
            "temp_max_avg", "temp_min_avg", "humidity_avg", "rainfall_14d", "wind_avg",
            "ndvi_avg", "soil_moisture_avg", "health_score_avg"
        ]
        
        return np.array(data), np.array(yields)

    def _crop_encoded(self) -> int:
        return list(CropType).index(self.crop)

    def train(self, X: np.ndarray = None, y: np.ndarray = None, n_samples: int = 10000):
        if X is None or y is None:
            X, y = self.generate_synthetic_data(n_samples)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.model = GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=6,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        y_pred = self.model.predict(X_test_scaled)
        
        self.metrics = {
            "mae": mean_absolute_error(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "r2": r2_score(y_test, y_pred),
            "mape": np.mean(np.abs((y_test - y_pred) / y_test)) * 100,
            "training_date": date.today().isoformat(),
            "samples": len(X),
        }
        
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5, scoring='neg_mean_absolute_error')
        self.metrics["cv_mae"] = -cv_scores.mean()
        
        self.save()
        
        return self.metrics

    def predict(self, features: List[float]) -> float:
        if self.model is None:
            self.load()
        
        if self.model is None:
            self.train()
        
        features_scaled = self.scaler.transform([features])
        return self.model.predict(features_scaled)[0]

    def save(self):
        self.model_dir.mkdir(exist_ok=True)
        path = self.model_dir / f"yield_{self.crop.value}.joblib"
        joblib.dump({
            "model": self.model,
            "scaler": self.scaler,
            "feature_names": self.feature_names,
            "metrics": self.metrics,
        }, path)

    def load(self):
        path = self.model_dir / f"yield_{self.crop.value}.joblib"
        if path.exists():
            data = joblib.load(path)
            self.model = data["model"]
            self.scaler = data["scaler"]
            self.feature_names = data["feature_names"]
            self.metrics = data["metrics"]
            return True
        return False