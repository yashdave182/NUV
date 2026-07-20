#!/usr/bin/env python3
"""
ML Model Training Script for AgriTech API
Trains yield prediction, price forecasting, disease risk, irrigation, and fertilizer models
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agritech_api.ml_models.yield_model import YieldPredictor
from agritech_api.ml_models.price_model import PriceForecaster
from agritech_api.ml_models.disease_model import DiseaseRiskClassifier
from agritech_api.ml_models.irrigation_model import IrrigationOptimizer
from agritech_api.ml_models.fertilizer_model import FertilizerOptimizer
from agritech_api.schemas import CropType


async def train_yield_models():
    print("=" * 60)
    print("Training Yield Prediction Models")
    print("=" * 60)
    
    for crop in CropType:
        if crop in [CropType.TOBACCO, CropType.GREEN_GRAM, CropType.BLACK_GRAM, 
                    CropType.PIGEON_PEA, CropType.CHILLI, CropType.ONION, 
                    CropType.POTATO, CropType.BANANA, CropType.PAPAYA, CropType.MANGO]:
            continue
            
        print(f"\nTraining {crop.value}...")
        try:
            predictor = YieldPredictor(crop)
            metrics = predictor.train(n_samples=15000)
            print(f"  MAE: {metrics['mae']:.3f}, RMSE: {metrics['rmse']:.3f}, R²: {metrics['r2']:.3f}")
            print(f"  CV MAE: {metrics['cv_mae']:.3f}")
        except Exception as e:
            print(f"  Error: {e}")


async def train_price_models():
    print("\n" + "=" * 60)
    print("Training Price Forecasting Models")
    print("=" * 60)
    
    for crop in CropType:
        if crop in [CropType.TOBACCO, CropType.GREEN_GRAM, CropType.BLACK_GRAM, 
                    CropType.PIGEON_PEA, CropType.CHILLI, CropType.ONION, 
                    CropType.POTATO, CropType.BANANA, CropType.PAPAYA, CropType.MANGO]:
            continue
            
        print(f"\nTraining {crop.value}...")
        try:
            forecaster = PriceForecaster(crop)
            forecaster.train(n_samples=15000)
            print(f"  Model saved")
        except Exception as e:
            print(f"  Error: {e}")


async def train_disease_model():
    print("\n" + "=" * 60)
    print("Training Disease Risk Classifier")
    print("=" * 60)
    
    try:
        classifier = DiseaseRiskClassifier()
        metrics = classifier.train(n_samples=25000)
        print(f"  Accuracy: {metrics['accuracy']:.3f}")
    except Exception as e:
        print(f"  Error: {e}")


async def train_irrigation_model():
    print("\n" + "=" * 60)
    print("Training Irrigation Optimizer")
    print("=" * 60)
    
    try:
        optimizer = IrrigationOptimizer()
        metrics = optimizer.train(n_samples=15000)
        for target, score in metrics['target_scores'].items():
            print(f"  {target} R²: {score:.3f}")
    except Exception as e:
        print(f"  Error: {e}")


async def train_fertilizer_model():
    print("\n" + "=" * 60)
    print("Training Fertilizer Optimizer")
    print("=" * 60)
    
    try:
        optimizer = FertilizerOptimizer()
        metrics = optimizer.train(n_samples=15000)
        for target, score in metrics['target_scores'].items():
            print(f"  {target} R²: {score:.3f}")
    except Exception as e:
        print(f"  Error: {e}")


async def main():
    print("AgriTech ML Model Training Pipeline")
    print("=" * 60)
    
    os.makedirs("models", exist_ok=True)
    
    await train_yield_models()
    await train_price_models()
    await train_disease_model()
    await train_irrigation_model()
    await train_fertilizer_model()
    
    print("\n" + "=" * 60)
    print("All models trained and saved!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())