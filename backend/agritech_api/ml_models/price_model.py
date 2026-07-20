import numpy as np
import pandas as pd
from datetime import date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from prophet import Prophet
import joblib
from pathlib import Path

from agritech_api.schemas import CropType


@dataclass
class PriceForecast:
    forecast_date: date
    predicted_price: float
    lower_bound: float
    upper_bound: float
    trend: str
    confidence: float
    drivers: List[str]


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
        
        self.seasonal_factors = {
            CropType.COTTON: {10: 1.1, 11: 1.15, 12: 1.1, 1: 1.05, 2: 1.0, 3: 0.95, 4: 0.9, 5: 0.9, 6: 0.85, 7: 0.85, 8: 0.9, 9: 0.95},
            CropType.GROUNDNUT: {3: 0.9, 4: 0.9, 5: 0.95, 6: 1.0, 7: 1.05, 8: 1.1, 9: 1.15, 10: 1.2, 11: 1.1, 12: 1.05, 1: 1.0, 2: 0.95},
            CropType.WHEAT: {3: 1.0, 4: 1.05, 5: 1.1, 6: 1.15, 7: 1.1, 8: 1.05, 9: 1.0, 10: 0.95, 11: 0.95, 12: 1.0},
            CropType.BAJRA: {9: 1.1, 10: 1.15, 11: 1.15, 12: 1.1, 1: 1.0, 2: 1.0, 3: 1.0},
            CropType.MAIZE: {9: 1.0, 10: 1.05, 11: 1.1, 12: 1.1, 1: 1.05, 2: 1.0},
            CropType.CUMIN: {1: 1.15, 2: 1.1, 3: 1.05, 4: 1.0, 5: 0.95, 6: 0.9, 7: 0.9, 8: 0.9, 9: 0.95, 10: 1.0, 11: 1.1, 12: 1.15},
            CropType.CASTOR: {1: 1.0, 2: 1.0, 3: 1.05, 4: 1.1, 5: 1.1, 6: 1.05, 7: 1.0, 8: 1.0, 9: 1.0, 10: 1.05, 11: 1.1, 12: 1.05},
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
        current_month = date.today().month
        
        seasonal = self.seasonal_factors.get(self.crop, {}).get(current_month, 1.0)
        
        trend = 0
        if len(historical_prices) >= 7:
            recent = np.mean([p["price"] for p in historical_prices[-7:]])
            older = np.mean([p["price"] for p in historical_prices[-14:-7]]) if len(historical_prices) >= 14 else recent
            trend = (recent - older) / older
        
        arrival_factor = 1.0
        if arrival_trend and len(arrival_trend) >= 7:
            avg_recent = np.mean(arrival_trend[-7:])
            avg_overall = np.mean(arrival_trend)
            if avg_recent > avg_overall * 1.2:
                arrival_factor = 0.95
            elif avg_recent < avg_overall * 0.8:
                arrival_factor = 1.05
        
        weather_factor = 1.0
        for w in weather_forecast[:7]:
            if w.get("rainfall_mm", 0) > 30:
                weather_factor *= 1.015
            if w.get("temp_max_c", 0) > 40:
                weather_factor *= 1.01
        
        results = []
        for i in range(1, days_ahead + 1):
            forecast_date = date.today() + timedelta(days=i)
            
            daily_trend = trend * 0.5 + np.random.normal(0, 0.008)
            daily_arrival = arrival_factor * (1 + np.random.normal(0, 0.015))
            daily_weather = weather_factor * (1 + np.random.normal(0, 0.01))
            
            predicted = current_price * (1 + daily_trend) * daily_arrival * daily_weather
            predicted = max(base * 0.7, min(base * 1.4, predicted))
            
            volatility = 0.025 + abs(daily_trend) * 0.5
            lower = predicted * (1 - volatility)
            upper = predicted * (1 + volatility)
            
            confidence = max(0.5, 0.9 - i * 0.025)
            
            if daily_trend > 0.01:
                trend_str = "rising"
            elif daily_trend < -0.01:
                trend_str = "falling"
            else:
                trend_str = "stable"
            
            drivers = []
            if abs(trend) > 0.02:
                drivers.append("Historical price trend")
            if arrival_factor != 1.0:
                drivers.append("Mandi arrival pressure")
            if weather_factor != 1.0:
                drivers.append("Weather impact on supply")
            if abs(seasonal - 1.0) > 0.05:
                drivers.append("Seasonal demand pattern")
            
            results.append(PriceForecast(
                forecast_date=forecast_date,
                predicted_price=round(predicted),
                lower_bound=round(lower),
                upper_bound=round(upper),
                trend=trend_str,
                confidence=round(confidence, 2),
                drivers=drivers,
            ))
        
        return results


class PriceForecaster:
    def __init__(self, crop: CropType, model_dir: str = "models"):
        self.crop = crop
        self.model_dir = Path(model_dir)
        self.prophet_model = None
        self.ml_model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.metrics = None
        
    def prepare_prophet_data(self, historical_prices: List[Dict]) -> pd.DataFrame:
        df = pd.DataFrame(historical_prices)
        df = df.rename(columns={"date": "ds", "price": "y"})
        df["ds"] = pd.to_datetime(df["ds"])
        df = df.sort_values("ds")
        return df[["ds", "y"]]

    def train_prophet(self, historical_prices: List[Dict], arrival_data: List[Dict] = None):
        df = self.prepare_prophet_data(historical_prices)
        
        self.prophet_model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10,
        )
        
        if arrival_data:
            arrivals_df = pd.DataFrame(arrival_data)
            arrivals_df = arrivals_df.rename(columns={"date": "ds", "arrival_tonnes": "arrival"})
            arrivals_df["ds"] = pd.to_datetime(arrivals_df["ds"])
            df = df.merge(arrivals_df, on="ds", how="left")
            df["arrival"] = df["arrival"].fillna(df["arrival"].mean())
            self.prophet_model.add_regressor("arrival")
        
        self.prophet_model.fit(df)
        
        future = self.prophet_model.make_future_dataframe(periods=30)
        if arrival_data:
            future["arrival"] = df["arrival"].iloc[-1]
        forecast = self.prophet_model.predict(future)
        
        self.metrics = {
            "prophet_mae": mean_absolute_error(df["y"], forecast.loc[:len(df)-1, "yhat"]),
            "training_date": date.today().isoformat(),
        }
        
        self.save()
        
        return self.metrics

    def forecast_prophet(self, days: int = 14, arrival_forecast: List[float] = None) -> List[PriceForecast]:
        if self.prophet_model is None:
            self.load()
        
        if self.prophet_model is None:
            raise ValueError("Model not trained")
        
        future = self.prophet_model.make_future_dataframe(periods=days)
        if arrival_forecast:
            future["arrival"] = arrival_forecast[-1]
        
        forecast = self.prophet_model.predict(future)
        
        results = []
        for i, row in forecast.tail(days).iterrows():
            results.append(PriceForecast(
                forecast_date=row["ds"].date(),
                predicted_price=round(row["yhat"]),
                lower_bound=round(row["yhat_lower"]),
                upper_bound=round(row["yhat_upper"]),
                trend="rising" if row["trend"] > 0 else "falling" if row["trend"] < 0 else "stable",
                confidence=0.8,
                drivers=["Prophet time series model"]
            ))
        
        return results

    def prepare_ml_features(
        self,
        historical_prices: List[Dict],
        arrival_data: List[Dict],
        weather_data: List[Dict],
        market_data: Dict
    ) -> Tuple[np.ndarray, np.ndarray]:
        min_len = min(len(historical_prices), len(arrival_data))
        
        X = []
        y = []
        
        for i in range(14, min_len - 1):
            price_window = [historical_prices[i-j]["price"] for j in range(14, 0, -1)]
            arrival_window = [arrival_data[i-j]["arrival_tonnes"] for j in range(14, 0, -1)]
            
            weather_idx = min(i, len(weather_data) - 1)
            w = weather_data[weather_idx] if weather_idx < len(weather_data) else {}
            
            features = price_window + arrival_window + [
                w.get("temp_max_c", 30),
                w.get("temp_min_c", 20),
                w.get("humidity_percent", 60),
                w.get("rainfall_mm", 0),
                w.get("wind_speed_kmph", 10),
                market_data.get("mandi_count", 5),
                market_data.get("transport_cost", 100),
            ]
            
            X.append(features)
            y.append(historical_prices[i+1]["price"])
        
        self.feature_names = (
            [f"price_lag_{j}" for j in range(1, 15)] +
            [f"arrival_lag_{j}" for j in range(1, 15)] +
            ["temp_max", "temp_min", "humidity", "rainfall", "wind", "mandi_count", "transport_cost"]
        )
        
        return np.array(X), np.array(y)

    def train_ml(self, X: np.ndarray, y: np.ndarray):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.ml_model = GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=5,
            subsample=0.8,
            random_state=42
        )
        
        self.ml_model.fit(X_train_scaled, y_train)
        
        y_pred = self.ml_model.predict(X_test_scaled)
        
        self.metrics = {
            "ml_mae": mean_absolute_error(y_test, y_pred),
            "ml_rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "ml_r2": r2_score(y_test, y_pred),
            "training_date": date.today().isoformat(),
        }
        
        self.save()
        
        return self.metrics

    def forecast_ml(
        self,
        historical_prices: List[Dict],
        arrival_data: List[Dict],
        weather_forecast: List[Dict],
        market_data: Dict,
        days_ahead: int = 14
    ) -> List[PriceForecast]:
        if self.ml_model is None:
            self.load()
        
        if self.ml_model is None:
            raise ValueError("ML model not trained")
        
        results = []
        
        price_hist = [p["price"] for p in historical_prices[-14:]]
        arrival_hist = [a["arrival_tonnes"] for a in arrival_data[-14:]]
        
        for i in range(days_ahead):
            w = weather_forecast[i] if i < len(weather_forecast) else {}
            
            features = price_hist + arrival_hist + [
                w.get("temp_max_c", 30),
                w.get("temp_min_c", 20),
                w.get("humidity_percent", 60),
                w.get("rainfall_mm", 0),
                w.get("wind_speed_kmph", 10),
                market_data.get("mandi_count", 5),
                market_data.get("transport_cost", 100),
            ]
            
            features_scaled = self.scaler.transform([features])
            predicted = self.ml_model.predict(features_scaled)[0]
            
            price_hist = price_hist[1:] + [predicted]
            arrival_hist = arrival_hist[1:] + [arrival_hist[-1] * 1.02]
            
            volatility = 0.03
            lower = predicted * (1 - volatility)
            upper = predicted * (1 + volatility)
            
            trend = "rising" if predicted > price_hist[-2] else "falling" if predicted < price_hist[-2] else "stable"
            
            results.append(PriceForecast(
                forecast_date=date.today() + timedelta(days=i+1),
                predicted_price=round(predicted),
                lower_bound=round(lower),
                upper_bound=round(upper),
                trend=trend,
                confidence=max(0.5, 0.85 - i * 0.02),
                drivers=["ML model with price/arrival/weather features"]
            ))
        
        return results

    def save(self):
        self.model_dir.mkdir(exist_ok=True)
        path = self.model_dir / f"price_{self.crop.value}.joblib"
        joblib.dump({
            "prophet_model": self.prophet_model,
            "ml_model": self.ml_model,
            "scaler": self.scaler,
            "feature_names": self.feature_names,
            "metrics": self.metrics,
        }, path)

    def load(self):
        path = self.model_dir / f"price_{self.crop.value}.joblib"
        if path.exists():
            data = joblib.load(path)
            self.prophet_model = data.get("prophet_model")
            self.ml_model = data.get("ml_model")
            self.scaler = data["scaler"]
            self.feature_names = data["feature_names"]
            self.metrics = data.get("metrics")
            return True
        return False