import numpy as np
import pandas as pd
from datetime import date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import joblib
from pathlib import Path

from agritech_api.schemas import CropType, GrowthStage


@dataclass
class DiseaseRisk:
    crop: CropType
    disease: str
    risk_level: str
    probability: float
    days_to_peak: int
    recommended_action: str
    weather_trigger: Dict[str, Any]


class RuleBasedDiseaseModel:
    def __init__(self):
        self.disease_rules = {
            CropType.COTTON: {
                "boll_rot": {
                    "humidity_min": 85, "rainfall_mm": 10, "temp_range": (25, 35),
                    "stages": [GrowthStage.FLOWERING, GrowthStage.FRUITING],
                    "action": "Spray copper oxychloride 50% WP @ 2.5g/L + streptomycin 1g/L",
                    "vector": None
                },
                "leaf_curl": {
                    "humidity_min": 60, "temp_range": (30, 40), "rainfall_mm": 0,
                    "stages": [GrowthStage.VEGETATIVE, GrowthStage.FLOWERING],
                    "action": "Control whitefly: neem oil 5% @ 3ml/L or imidacloprid 17.8% SL @ 0.3ml/L",
                    "vector": "whitefly"
                },
                "root_rot": {
                    "soil_moisture_min": 80, "temp_range": (25, 30),
                    "stages": [GrowthStage.GERMINATION, GrowthStage.VEGETATIVE],
                    "action": "Drench carbendazim 50% WP @ 1g/L, improve drainage, avoid waterlogging",
                    "vector": None
                },
                "bacterial_blight": {
                    "humidity_min": 80, "rainfall_mm": 5, "temp_range": (28, 32),
                    "stages": [GrowthStage.VEGETATIVE, GrowthStage.FLOWERING],
                    "action": "Spray streptocycline 1g/L + copper oxychloride 2.5g/L",
                    "vector": None
                },
            },
            CropType.GROUNDNUT: {
                "tikka": {
                    "humidity_min": 85, "rainfall_mm": 5, "temp_range": (25, 32),
                    "stages": [GrowthStage.FLOWERING, GrowthStage.FRUITING],
                    "action": "Spray tebuconazole 25.9% EC @ 1ml/L or hexaconazole 5% SC @ 1ml/L",
                    "vector": None
                },
                "rust": {
                    "humidity_min": 80, "temp_range": (20, 28), "rainfall_mm": 2,
                    "stages": [GrowthStage.VEGETATIVE, GrowthStage.FLOWERING],
                    "action": "Spray propiconazole 25% EC @ 1ml/L at first sign",
                    "vector": None
                },
                "stem_rot": {
                    "soil_moisture_min": 75, "temp_range": (25, 30),
                    "stages": [GrowthStage.FRUITING],
                    "action": "Soil application of trichoderma @ 5kg/ha, avoid waterlogging",
                    "vector": None
                },
                "bud_necrosis": {
                    "humidity_min": 70, "temp_range": (25, 35),
                    "stages": [GrowthStage.FLOWERING],
                    "action": "Control thrips (vector): imidacloprid 17.8% SL @ 0.3ml/L",
                    "vector": "thrips"
                },
            },
            CropType.WHEAT: {
                "yellow_rust": {
                    "temp_range": (10, 20), "humidity_min": 90, "rainfall_mm": 2,
                    "stages": [GrowthStage.FLOWERING],
                    "action": "Spray triazole (tebuconazole/propiconazole) @ 1ml/L immediately",
                    "vector": None
                },
                "brown_rust": {
                    "temp_range": (15, 25), "humidity_min": 80, "rainfall_mm": 1,
                    "stages": [GrowthStage.FLOWERING, GrowthStage.FRUITING],
                    "action": "Spray propiconazole 25% EC @ 1ml/L",
                    "vector": None
                },
                "karnal_bunt": {
                    "humidity_min": 80, "rainfall_mm": 5,
                    "stages": [GrowthStage.FLOWERING],
                    "action": "Seed treatment with carbendazim, avoid late irrigation at flowering",
                    "vector": None
                },
                "loose_smut": {
                    "temp_range": (18, 22), "humidity_min": 70,
                    "stages": [GrowthStage.FLOWERING],
                    "action": "Seed treatment with carboxin 75% WP @ 2g/kg seed",
                    "vector": None
                },
            },
            CropType.MAIZE: {
                "maydis_leaf_blight": {
                    "humidity_min": 85, "rainfall_mm": 5, "temp_range": (25, 30),
                    "stages": [GrowthStage.VEGETATIVE, GrowthStage.FLOWERING],
                    "action": "Spray mancozeb 75% WP @ 2.5g/L or azoxystrobin 23% SC @ 1ml/L",
                    "vector": None
                },
                "tassel_blight": {
                    "humidity_min": 80, "rainfall_mm": 10, "temp_range": (25, 32),
                    "stages": [GrowthStage.FLOWERING],
                    "action": "Spray carbendazim 50% WP @ 1g/L at tasseling",
                    "vector": None
                },
                "stalk_rot": {
                    "soil_moisture_min": 70, "temp_range": (25, 30),
                    "stages": [GrowthStage.FRUITING, GrowthStage.MATURITY],
                    "action": "Avoid water stress at grain fill, balanced K nutrition",
                    "vector": None
                },
            },
            CropType.CUMIN: {
                "wilt": {
                    "soil_moisture_min": 75, "temp_range": (20, 28),
                    "stages": [GrowthStage.VEGETATIVE, GrowthStage.FLOWERING],
                    "action": "Seed treatment with trichoderma, soil solarization, avoid flooding",
                    "vector": None
                },
                "blight": {
                    "humidity_min": 85, "rainfall_mm": 5, "temp_range": (15, 25),
                    "stages": [GrowthStage.FLOWERING, GrowthStage.FRUITING],
                    "action": "Spray copper oxychloride 50% WP @ 2.5g/L, ensure drainage",
                    "vector": None
                },
                "powdery_mildew": {
                    "humidity_min": 70, "temp_range": (20, 30), "rainfall_mm": 0,
                    "stages": [GrowthStage.VEGETATIVE, GrowthStage.FLOWERING],
                    "action": "Spray sulfur 80% WP @ 2.5g/L or dinocap 48% EC @ 1ml/L",
                    "vector": None
                },
            },
            CropType.CASTOR: {
                "wilt": {
                    "soil_moisture_min": 70, "temp_range": (25, 30),
                    "stages": [GrowthStage.VEGETATIVE, GrowthStage.FLOWERING],
                    "action": "Seed treatment with carbendazim, crop rotation, resistant varieties",
                    "vector": None
                },
                "root_rot": {
                    "soil_moisture_min": 75, "temp_range": (25, 32),
                    "stages": [GrowthStage.GERMINATION, GrowthStage.VEGETATIVE],
                    "action": "Improve drainage, seed treatment with metalaxyl",
                    "vector": None
                },
                "leaf_spot": {
                    "humidity_min": 80, "rainfall_mm": 5, "temp_range": (25, 32),
                    "stages": [GrowthStage.VEGETATIVE, GrowthStage.FLOWERING],
                    "action": "Spray mancozeb 75% WP @ 2.5g/L",
                    "vector": None
                },
            },
        }

    def assess_risk(
        self,
        crop: CropType,
        growth_stage: GrowthStage,
        weather_forecast: List[Dict],
        satellite_data: List[Dict],
        pest_counts: Dict[str, int]
    ) -> List[DiseaseRisk]:
        rules = self.disease_rules.get(crop, {})
        risks = []
        
        avg_humidity = np.mean([w.get("humidity_percent", 60) for w in weather_forecast[:7]])
        max_humidity = max([w.get("humidity_percent", 60) for w in weather_forecast[:7]])
        total_rain = sum([w.get("rainfall_mm", 0) for w in weather_forecast[:7]])
        max_temp = max([w.get("temp_max_c", 30) for w in weather_forecast[:7]])
        min_temp = min([w.get("temp_min_c", 20) for w in weather_forecast[:7]])
        avg_soil_moist = np.mean([s.get("soil_moisture_percent", 50) for s in satellite_data[:7]]) if satellite_data else 50
        
        for disease, conditions in rules.items():
            prob = 0.1
            
            if growth_stage not in conditions.get("stages", []):
                continue
            
            if avg_humidity >= conditions.get("humidity_min", 99):
                prob += 0.25
            elif max_humidity >= conditions.get("humidity_min", 99):
                prob += 0.15
            
            if total_rain >= conditions.get("rainfall_mm", 0):
                prob += 0.2
            
            tmin, tmax = conditions.get("temp_range", (0, 50))
            if tmin <= max_temp <= tmax:
                prob += 0.2
            
            if "soil_moisture_min" in conditions:
                if avg_soil_moist >= conditions["soil_moisture_min"]:
                    prob += 0.25
            
            if conditions.get("vector") and conditions["vector"] in pest_counts:
                if pest_counts[conditions["vector"]] > 5:
                    prob += 0.2
            
            prob = min(0.95, prob)
            
            if prob < 0.15:
                continue
            
            if prob > 0.7:
                level = "critical"
                days_peak = 2
            elif prob > 0.5:
                level = "high"
                days_peak = 5
            elif prob > 0.3:
                level = "medium"
                days_peak = 10
            else:
                level = "low"
                days_peak = 14
            
            trigger = {}
            for w in weather_forecast[:3]:
                if w.get("humidity_percent", 0) >= conditions.get("humidity_min", 99):
                    trigger["high_humidity"] = w.get("humidity_percent")
                if w.get("rainfall_mm", 0) >= conditions.get("rainfall_mm", 0):
                    trigger["rainfall_mm"] = w.get("rainfall_mm")
                if tmin <= w.get("temp_max_c", 0) <= tmax:
                    trigger["temp_c"] = w.get("temp_max_c")
            
            risks.append(DiseaseRisk(
                crop=crop,
                disease=disease,
                risk_level=level,
                probability=round(prob, 2),
                days_to_peak=days_peak,
                recommended_action=conditions["action"],
                weather_trigger=trigger,
            ))
        
        risks.sort(key=lambda x: x.probability, reverse=True)
        return risks[:5]


class DiseaseRiskClassifier:
    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        self.disease_classes = []
        self.metrics = None
        
        self.disease_list = [
            "boll_rot", "leaf_curl", "root_rot", "bacterial_blight",
            "tikka", "rust", "stem_rot", "bud_necrosis",
            "yellow_rust", "brown_rust", "karnal_bunt", "loose_smut",
            "maydis_leaf_blight", "tassel_blight", "stalk_rot",
            "wilt", "blight", "powdery_mildew",
            "healthy"
        ]
        
        for d in self.disease_list:
            self.label_encoders[d] = LabelEncoder()
            self.label_encoders[d].fit(["low", "medium", "high", "critical"])

    def generate_training_data(self, n_samples: int = 20000) -> Tuple[np.ndarray, np.ndarray]:
        np.random.seed(42)
        
        rule_model = RuleBasedDiseaseModel()
        
        X = []
        y = []
        
        crops = list(CropType)
        
        for _ in range(n_samples):
            crop = np.random.choice(crops)
            stage = np.random.choice(list(GrowthStage))
            
            weather = []
            for i in range(7):
                weather.append({
                    "humidity_percent": np.random.uniform(30, 95),
                    "rainfall_mm": np.random.exponential(5),
                    "temp_max_c": np.random.uniform(15, 45),
                    "temp_min_c": np.random.uniform(8, 30),
                    "wind_speed_kmph": np.random.uniform(2, 30),
                })
            
            satellite = []
            for i in range(7):
                satellite.append({
                    "soil_moisture_percent": np.random.uniform(10, 90),
                    "ndvi": np.random.uniform(0.1, 0.9),
                    "lst_day_c": np.random.uniform(20, 45),
                })
            
            pest_counts = {
                "whitefly": np.random.poisson(3),
                "thrips": np.random.poisson(5),
                "aphid": np.random.poisson(10),
                "jassid": np.random.poisson(3),
            }
            
            features = self._extract_features(crop, stage, weather, satellite, pest_counts)
            
            risks = rule_model.assess_risk(crop, stage, weather, satellite, pest_counts)
            
            disease_probs = {}
            for disease in self.disease_list:
                matching = [r for r in risks if r.disease == disease]
                if matching:
                    disease_probs[disease] = matching[0].probability
                else:
                    disease_probs[disease] = 0.01
            
            primary_disease = max(disease_probs, key=disease_probs.get)
            risk_level = self._prob_to_level(disease_probs[primary_disease])
            
            X.append(features)
            y.append(primary_disease)
        
        self.feature_names = self._get_feature_names()
        return np.array(X), np.array(y)

    def _extract_features(
        self,
        crop: CropType,
        stage: GrowthStage,
        weather: List[Dict],
        satellite: List[Dict],
        pests: Dict[str, int]
    ) -> List[float]:
        return [
            list(CropType).index(crop),
            list(GrowthStage).index(stage),
            np.mean([w["humidity_percent"] for w in weather]),
            np.max([w["humidity_percent"] for w in weather]),
            np.sum([w["rainfall_mm"] for w in weather]),
            np.mean([w["temp_max_c"] for w in weather]),
            np.max([w["temp_max_c"] for w in weather]),
            np.min([w["temp_min_c"] for w in weather]),
            np.mean([s.get("soil_moisture_percent", 50) for s in satellite]),
            np.mean([s.get("ndvi", 0.5) for s in satellite]),
            np.max([s.get("lst_day_c", 30) for s in satellite]),
            pests.get("whitefly", 0),
            pests.get("thrips", 0),
            pests.get("aphid", 0),
            pests.get("jassid", 0),
        ]

    def _get_feature_names(self) -> List[str]:
        return [
            "crop_encoded", "stage_encoded", "avg_humidity", "max_humidity",
            "total_rainfall", "avg_temp_max", "max_temp", "min_temp",
            "avg_soil_moisture", "avg_ndvi", "max_lst",
            "whitefly_count", "thrips_count", "aphid_count", "jassid_count"
        ]

    def _prob_to_level(self, prob: float) -> str:
        if prob > 0.7: return "critical"
        elif prob > 0.5: return "high"
        elif prob > 0.3: return "medium"
        return "low"

    def train(self, X: np.ndarray = None, y: np.ndarray = None, n_samples: int = 20000):
        if X is None or y is None:
            X, y = self.generate_training_data(n_samples)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.model = GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=6,
            subsample=0.8,
            random_state=42
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        y_pred = self.model.predict(X_test_scaled)
        y_proba = self.model.predict_proba(X_test_scaled)
        
        self.metrics = {
            "accuracy": self.model.score(X_test_scaled, y_test),
            "classification_report": classification_report(y_test, y_pred, output_dict=True),
            "training_date": date.today().isoformat(),
            "n_samples": len(X),
        }
        
        self.save()
        return self.metrics

    def predict_risk(
        self,
        crop: CropType,
        stage: GrowthStage,
        weather: List[Dict],
        satellite: List[Dict],
        pests: Dict[str, int]
    ) -> List[DiseaseRisk]:
        if self.model is None:
            self.load()
        
        if self.model is None:
            rule_model = RuleBasedDiseaseModel()
            return rule_model.assess_risk(crop, stage, weather, satellite, pests)
        
        features = self._extract_features(crop, stage, weather, satellite, pests)
        features_scaled = self.scaler.transform([features])
        
        probs = self.model.predict_proba(features_scaled)[0]
        
        risks = []
        for disease, prob in zip(self.model.classes_, probs):
            if prob < 0.05:
                continue
            
            if prob > 0.7:
                level = "critical"
                days = 2
            elif prob > 0.5:
                level = "high"
                days = 5
            elif prob > 0.3:
                level = "medium"
                days = 10
            else:
                level = "low"
                days = 14
            
            rule_model = RuleBasedDiseaseModel()
            rule_risks = rule_model.assess_risk(crop, stage, weather, satellite, pests)
            matching = [r for r in rule_risks if r.disease == disease]
            action = matching[0].recommended_action if matching else "Monitor and consult KVK"
            trigger = matching[0].weather_trigger if matching else {}
            
            risks.append(DiseaseRisk(
                crop=crop,
                disease=disease,
                risk_level=level,
                probability=round(float(prob), 2),
                days_to_peak=days,
                recommended_action=action,
                weather_trigger=trigger,
            ))
        
        risks.sort(key=lambda x: x.probability, reverse=True)
        return risks[:5]

    def save(self):
        self.model_dir.mkdir(exist_ok=True)
        path = self.model_dir / "disease_risk.joblib"
        joblib.dump({
            "model": self.model,
            "scaler": self.scaler,
            "label_encoders": self.label_encoders,
            "feature_names": self.feature_names,
            "disease_classes": self.disease_classes,
            "metrics": self.metrics,
        }, path)

    def load(self):
        path = self.model_dir / "disease_risk.joblib"
        if path.exists():
            data = joblib.load(path)
            self.model = data["model"]
            self.scaler = data["scaler"]
            self.label_encoders = data["label_encoders"]
            self.feature_names = data["feature_names"]
            self.disease_classes = data["disease_classes"]
            self.metrics = data.get("metrics")
            return True
        return False