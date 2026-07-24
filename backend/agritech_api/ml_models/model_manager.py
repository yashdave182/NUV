import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import logging

from agritech_api.schemas import CropType, SoilType, GrowthStage, IrrigationSource, Location
from agritech_api.clients import get_weather_client, get_satellite_client, get_soil_client
from agritech_api.ml_models.yield_model import RuleBasedYieldModel
from agritech_api.ml_models.price_model import RuleBasedPriceModel
from agritech_api.ml_models.disease_model import RuleBasedDiseaseModel
from agritech_api.ml_models.irrigation_model import RuleBasedIrrigationModel, RuleBasedFertilizerModel

logger = logging.getLogger(__name__)


@dataclass
class ModelMetrics:
    mae: float
    rmse: float
    r2: float
    mape: float
    training_date: date
    samples: int


class MLModelManager:
    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        self.yield_models: Dict[CropType, Any] = {}
        self.price_models: Dict[CropType, Any] = {}
        self.disease_model = None
        self.irrigation_model = None
        self.fertilizer_model = None
        
        self.yield_scalers: Dict[CropType, Any] = {}
        self.price_scalers: Dict[CropType, Any] = {}
        
        self.metrics: Dict[str, ModelMetrics] = {}
        
        self._init_fallback_models()
        self._load_models()

    def _load_models(self):
        try:
            import joblib
            from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
            from sklearn.preprocessing import StandardScaler
            
            for crop in CropType:
                yield_path = self.model_dir / f"yield_{crop.value}.joblib"
                if yield_path.exists():
                    model_data = joblib.load(yield_path)
                    self.yield_models[crop] = model_data["model"]
                    self.yield_scalers[crop] = model_data.get("scaler")
                    _known = {f.name for f in __import__('dataclasses').fields(ModelMetrics)}
                    self.metrics[f"yield_{crop.value}"] = ModelMetrics(**{k: v for k, v in model_data["metrics"].items() if k in _known})
            
            for crop in CropType:
                price_path = self.model_dir / f"price_{crop.value}.joblib"
                if price_path.exists():
                    model_data = joblib.load(price_path)
                    self.price_models[crop] = model_data["model"]
                    self.price_scalers[crop] = model_data.get("scaler")
                    _known = {f.name for f in __import__('dataclasses').fields(ModelMetrics)}
                    self.metrics[f"price_{crop.value}"] = ModelMetrics(**{k: v for k, v in model_data["metrics"].items() if k in _known})
            
            disease_path = self.model_dir / "disease_risk.joblib"
            if disease_path.exists():
                self.disease_model = joblib.load(disease_path)
            
            irrigation_path = self.model_dir / "irrigation_optimizer.joblib"
            if irrigation_path.exists():
                self.irrigation_model = joblib.load(irrigation_path)
            
            fertilizer_path = self.model_dir / "fertilizer_optimizer.joblib"
            if fertilizer_path.exists():
                self.fertilizer_model = joblib.load(fertilizer_path)
                
            logger.info(f"Loaded {len(self.yield_models)} yield models, {len(self.price_models)} price models")
            
        except Exception as e:
            logger.warning(f"Could not load ML models, using rule-based: {e}")
            self._init_fallback_models()

    def _init_fallback_models(self):
        self.yield_models = {crop: RuleBasedYieldModel(crop) for crop in CropType}
        self.price_models = {crop: RuleBasedPriceModel(crop) for crop in CropType}
        self.disease_model = RuleBasedDiseaseModel()
        self.irrigation_model = RuleBasedIrrigationModel()
        self.fertilizer_model = RuleBasedFertilizerModel()

    async def predict_yield(
        self,
        crop: CropType,
        area_hectares: float,
        soil_type: SoilType,
        sowing_date: date,
        location: Location,
        soil_data: Dict[str, float],
        weather_history: List[Dict],
        satellite_data: List[Dict],
        management: Dict[str, Any]
    ) -> Dict[str, Any]:
        model = self.yield_models.get(crop)
        
        if hasattr(model, 'predict') and callable(getattr(model, 'predict', None)):
            features = self._prepare_yield_features(
                crop, area_hectares, soil_type, sowing_date, 
                soil_data, weather_history, satellite_data, management
            )
            
            if crop in self.yield_scalers:
                features = self.yield_scalers[crop].transform([features])[0]
            
            pred = model.predict([features])[0]
            
            return {
                "predicted_yield_tonnes_ha": round(pred, 2),
                "confidence": 0.85,
                "model_type": "ml",
                "features_used": list(self._get_yield_feature_names()),
            }
        else:
            return await self._fallback_yield_prediction(
                crop, area_hectares, soil_type, sowing_date,
                soil_data, weather_history, satellite_data, management
            )

    async def _fallback_yield_prediction(
        self,
        crop: CropType,
        area_hectares: float,
        soil_type: SoilType,
        sowing_date: date,
        soil_data: Dict,
        weather_history: List,
        satellite_data: List,
        management: Dict
    ) -> Dict[str, Any]:
        model = self.yield_models[crop]
        
        ndvi_avg = np.mean([d.get("ndvi", 0.6) for d in satellite_data[-14:]]) if satellite_data else 0.6
        temp_avg = np.mean([d.get("temp_max_c", 30) for d in weather_history[-14:]]) if weather_history else 30
        rainfall = sum(d.get("rainfall_mm", 0) for d in weather_history[-30:]) if weather_history else 200
        humidity = np.mean([d.get("humidity_percent", 60) for d in weather_history[-14:]]) if weather_history else 60
        
        result = model.predict(
            area_hectares=area_hectares,
            soil_type=soil_type,
            sowing_date=sowing_date,
            temperature_avg=temp_avg,
            rainfall_total=rainfall,
            humidity_avg=humidity,
            soil_n=soil_data.get("available_n_kg_ha", 200),
            soil_p=soil_data.get("available_p_kg_ha", 18),
            soil_k=soil_data.get("available_k_kg_ha", 180),
            soil_ph=soil_data.get("ph", 7.2),
            irrigation_count=management.get("irrigation_count", 5),
            fertilizer_n=management.get("fertilizer_n", 100),
            fertilizer_p=management.get("fertilizer_p", 50),
            fertilizer_k=management.get("fertilizer_k", 40),
            pest_pressure=management.get("pest_pressure", 0.1),
            disease_pressure=management.get("disease_pressure", 0.1),
            ndvi_avg=ndvi_avg,
        )
        
        return {
            "predicted_yield_tonnes_ha": result.predicted_yield_tonnes_ha,
            "confidence_interval": result.confidence_interval,
            "confidence_level": result.confidence_level,
            "key_factors": result.key_factors,
            "risk_factors": result.risk_factors,
            "recommendation": result.recommendation,
            "model_type": "rule_based",
        }

    def _prepare_yield_features(
        self,
        crop: CropType,
        area: float,
        soil_type: SoilType,
        sowing: date,
        soil: Dict,
        weather: List,
        satellite: List,
        management: Dict
    ) -> List[float]:
        das = (date.today() - sowing).days
        
        features = [
            area,
            list(CropType).index(crop),
            list(SoilType).index(soil_type),
            das,
            soil.get("ph", 7.2),
            soil.get("ec_ds_m", 0.4),
            soil.get("organic_carbon_percent", 0.5),
            soil.get("available_n_kg_ha", 200),
            soil.get("available_p_kg_ha", 18),
            soil.get("available_k_kg_ha", 180),
            management.get("fertilizer_n", 100),
            management.get("fertilizer_p", 50),
            management.get("fertilizer_k", 40),
            management.get("irrigation_count", 5),
        ]
        
        if weather:
            recent = weather[-14:]
            features.extend([
                np.mean([d.get("temp_max_c", 30) for d in recent]),
                np.mean([d.get("temp_min_c", 20) for d in recent]),
                np.mean([d.get("humidity_percent", 60) for d in recent]),
                sum(d.get("rainfall_mm", 0) for d in recent),
                np.mean([d.get("wind_speed_kmph", 10) for d in recent]),
            ])
        else:
            features.extend([30, 20, 60, 0, 10])
        
        if satellite:
            recent_sat = satellite[-14:]
            features.extend([
                np.mean([d.get("ndvi", 0.6) for d in recent_sat]),
                np.mean([d.get("soil_moisture_percent", 50) for d in recent_sat]),
                np.mean([d.get("crop_health_score", 70) for d in recent_sat]),
            ])
        else:
            features.extend([0.6, 50, 70])
        
        return features

    def _get_yield_feature_names(self) -> List[str]:
        return [
            "area_hectares", "crop_encoded", "soil_encoded", "days_after_sowing",
            "ph", "ec", "organic_carbon", "available_n", "available_p", "available_k",
            "fertilizer_n", "fertilizer_p", "fertilizer_k", "irrigation_count",
            "temp_max_avg", "temp_min_avg", "humidity_avg", "rainfall_14d", "wind_avg",
            "ndvi_avg", "soil_moisture_avg", "health_score_avg"
        ]

    async def forecast_prices(
        self,
        crop: CropType,
        current_price: float,
        historical_prices: List[Dict],
        arrival_data: List[Dict],
        weather_forecast: List[Dict],
        market_intelligence: Dict,
        days_ahead: int = 14
    ) -> List[Dict[str, Any]]:
        model = self.price_models.get(crop)
        
        if hasattr(model, 'forecast') and callable(getattr(model, 'forecast', None)):
            return model.forecast(
                current_price, historical_prices, 
                [a.get("arrival_tonnes", 0) for a in arrival_data],
                weather_forecast, days_ahead
            )
        else:
            arrivals = [a.get("arrival_tonnes", 0) for a in arrival_data]
            result = model.forecast(current_price, historical_prices, arrivals, weather_forecast, days_ahead)
            return [
                {
                    "forecast_date": r.forecast_date.isoformat(),
                    "predicted_price": r.predicted_price,
                    "lower_bound": r.lower_bound,
                    "upper_bound": r.upper_bound,
                    "trend": r.trend,
                    "confidence": r.confidence,
                    "drivers": r.drivers,
                }
                for r in result
            ]

    async def assess_disease_risk(
        self,
        crop: CropType,
        growth_stage: GrowthStage,
        weather_forecast: List[Dict],
        satellite_data: List[Dict],
        field_history: Dict,
        symptoms_observed: List[str]
    ) -> List[Dict[str, Any]]:
        if self.disease_model and hasattr(self.disease_model, 'predict'):
            return await self._ml_disease_risk(crop, growth_stage, weather_forecast, satellite_data)
        else:
            return await self._rule_disease_risk(crop, growth_stage, weather_forecast, satellite_data, symptoms_observed)

    async def _rule_disease_risk(
        self,
        crop: CropType,
        stage: GrowthStage,
        weather: List[Dict],
        satellite: List[Dict],
        symptoms: List[str]
    ) -> List[Dict[str, Any]]:
        return self.disease_model.assess_risk(crop, stage, weather, satellite, symptoms)

    async def optimize_irrigation(
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
        if self.irrigation_model and hasattr(self.irrigation_model, 'optimize'):
            return self.irrigation_model.optimize(
                crop, growth_stage, soil_type, soil_moisture,
                weather_forecast, et0_forecast, area_hectares,
                irrigation_method, water_cost_per_m3
            )
        else:
            return RuleBasedIrrigationModel().optimize(
                crop, growth_stage, soil_type, soil_moisture,
                weather_forecast, et0_forecast, area_hectares,
                irrigation_method, water_cost_per_m3
            )

    async def optimize_fertilizer(
        self,
        crop: CropType,
        growth_stage: GrowthStage,
        soil_test: Dict[str, float],
        target_yield: float,
        area_hectares: float,
        fertilizer_prices: Dict[str, float],
        previous_applications: List[Dict]
    ) -> Dict[str, Any]:
        if self.fertilizer_model and hasattr(self.fertilizer_model, 'optimize'):
            return self.fertilizer_model.optimize(
                crop, growth_stage, soil_test, target_yield,
                area_hectares, fertilizer_prices, previous_applications
            )
        else:
            return RuleBasedFertilizerModel().optimize(
                crop, growth_stage, soil_test, target_yield,
                area_hectares, fertilizer_prices, previous_applications
            )

    def get_model_status(self) -> Dict[str, Any]:
        return {
            "yield_models_loaded": len(self.yield_models),
            "price_models_loaded": len(self.price_models),
            "disease_model": "ml" if self.disease_model and not isinstance(self.disease_model, RuleBasedDiseaseModel) else "rule_based",
            "irrigation_model": "ml" if self.irrigation_model and not isinstance(self.irrigation_model, RuleBasedIrrigationModel) else "rule_based",
            "fertilizer_model": "ml" if self.fertilizer_model and not isinstance(self.fertilizer_model, RuleBasedFertilizerModel) else "rule_based",
            "metrics": {k: v.__dict__ for k, v in self.metrics.items()},
        }


_model_manager: Optional[MLModelManager] = None


def get_model_manager() -> MLModelManager:
    global _model_manager
    if _model_manager is None:
        _model_manager = MLModelManager()
    return _model_manager