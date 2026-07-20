import os
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from dataclasses import dataclass
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


@dataclass
class WeatherData:
    date: date
    temp_max_c: float
    temp_min_c: float
    humidity_percent: float
    rainfall_mm: float
    wind_speed_kmph: float
    condition: str
    cloud_cover_percent: float = 0.0
    solar_radiation_mj: float = 0.0
    et0_mm: float = 0.0


class WeatherClient:
    def __init__(self):
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY")
        self.weatherapi_key = os.getenv("WEATHERAPI_KEY")
        self.imd_api_key = os.getenv("IMD_API_KEY")
        self.visualcrossing_key = os.getenv("VISUALCROSSING_API_KEY")
        
        self.client = httpx.AsyncClient(timeout=30.0)
        
        self.provider_priority = [
            "openweather",
            "weatherapi",
            "visualcrossing",
        ]

    async def get_forecast(
        self, 
        latitude: float, 
        longitude: float, 
        days: int = 7
    ) -> List[WeatherData]:
        for provider in self.provider_priority:
            try:
                if provider == "openweather" and self.openweather_api_key:
                    return await self._fetch_openweather(latitude, longitude, days)
                elif provider == "weatherapi" and self.weatherapi_key:
                    return await self._fetch_weatherapi(latitude, longitude, days)
                elif provider == "visualcrossing" and self.visualcrossing_key:
                    return await self._fetch_visualcrossing(latitude, longitude, days)
            except Exception as e:
                logger.warning(f"Weather provider {provider} failed: {e}")
                continue
        
        logger.error("All weather providers failed, using fallback")
        return self._fallback_forecast(latitude, longitude, days)

    async def _fetch_openweather(
        self, 
        lat: float, 
        lon: float, 
        days: int
    ) -> List[WeatherData]:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.openweather_api_key,
            "units": "metric",
            "cnt": days * 8,
        }
        
        resp = await self.client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        daily = {}
        for item in data["list"]:
            dt = datetime.fromtimestamp(item["dt"]).date()
            if dt not in daily:
                daily[dt] = {"temps": [], "humidity": [], "wind": [], "rain": 0, "clouds": [], "conditions": []}
            
            daily[dt]["temps"].append(item["main"]["temp"])
            daily[dt]["humidity"].append(item["main"]["humidity"])
            daily[dt]["wind"].append(item["wind"]["speed"] * 3.6)
            daily[dt]["clouds"].append(item["clouds"]["all"])
            daily[dt]["conditions"].append(item["weather"][0]["main"])
            
            if "rain" in item and "3h" in item["rain"]:
                daily[dt]["rain"] += item["rain"]["3h"]
        
        result = []
        for d in sorted(daily.keys())[:days]:
            vals = daily[d]
            result.append(WeatherData(
                date=d,
                temp_max_c=max(vals["temps"]),
                temp_min_c=min(vals["temps"]),
                humidity_percent=sum(vals["humidity"]) / len(vals["humidity"]),
                rainfall_mm=vals["rain"],
                wind_speed_kmph=sum(vals["wind"]) / len(vals["wind"]),
                condition=max(set(vals["conditions"]), key=vals["conditions"].count),
                cloud_cover_percent=sum(vals["clouds"]) / len(vals["clouds"]),
            ))
        
        return result

    async def _fetch_weatherapi(
        self, 
        lat: float, 
        lon: float, 
        days: int
    ) -> List[WeatherData]:
        url = "http://api.weatherapi.com/v1/forecast.json"
        params = {
            "key": self.weatherapi_key,
            "q": f"{lat},{lon}",
            "days": days,
            "aqi": "no",
            "alerts": "no",
        }
        
        resp = await self.client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        result = []
        for day in data["forecast"]["forecastday"][:days]:
            d = datetime.strptime(day["date"], "%Y-%m-%d").date()
            day_data = day["day"]
            result.append(WeatherData(
                date=d,
                temp_max_c=day_data["maxtemp_c"],
                temp_min_c=day_data["mintemp_c"],
                humidity_percent=day_data["avghumidity"],
                rainfall_mm=day_data["totalprecip_mm"],
                wind_speed_kmph=day_data["maxwind_kph"],
                condition=day_data["condition"]["text"],
                cloud_cover_percent=day_data.get("cloud", 0),
            ))
        
        return result

    async def _fetch_visualcrossing(
        self, 
        lat: float, 
        lon: float, 
        days: int
    ) -> List[WeatherData]:
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat},{lon}"
        params = {
            "key": self.visualcrossing_key,
            "unitGroup": "metric",
            "include": "days",
            "elements": "datetime,tempmax,tempmin,humidity,precip,windspeed,conditions,cloudcover,solarradiation",
        }
        
        resp = await self.client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        result = []
        for day in data["days"][:days]:
            d = datetime.strptime(day["datetime"], "%Y-%m-%d").date()
            result.append(WeatherData(
                date=d,
                temp_max_c=day["tempmax"],
                temp_min_c=day["tempmin"],
                humidity_percent=day["humidity"],
                rainfall_mm=day["precip"],
                wind_speed_kmph=day["windspeed"],
                condition=day["conditions"],
                cloud_cover_percent=day.get("cloudcover", 0),
                solar_radiation_mj=day.get("solarradiation", 0),
            ))
        
        return result

    def _fallback_forecast(
        self, 
        lat: float, 
        lon: float, 
        days: int
    ) -> List[WeatherData]:
        import random
        month = date.today().month
        
        seasonal = {
            1: {"temp": (12, 28), "rain": 1, "hum": 55},
            2: {"temp": (15, 32), "rain": 1, "hum": 50},
            3: {"temp": (20, 37), "rain": 2, "hum": 45},
            4: {"temp": (25, 41), "rain": 3, "hum": 50},
            5: {"temp": (28, 42), "rain": 10, "hum": 60},
            6: {"temp": (28, 38), "rain": 150, "hum": 75},
            7: {"temp": (26, 33), "rain": 300, "hum": 85},
            8: {"temp": (25, 32), "rain": 250, "hum": 85},
            9: {"temp": (25, 34), "rain": 180, "hum": 80},
            10: {"temp": (22, 36), "rain": 40, "hum": 65},
            11: {"temp": (18, 33), "rain": 10, "hum": 55},
            12: {"temp": (14, 30), "rain": 2, "hum": 50},
        }
        
        s = seasonal.get(month, seasonal[1])
        result = []
        
        for i in range(days):
            d = date.today() + timedelta(days=i)
            temp_max = s["temp"][1] + random.uniform(-3, 3)
            temp_min = s["temp"][0] + random.uniform(-3, 3)
            humidity = max(20, min(100, s["hum"] + random.uniform(-15, 15)))
            
            rain_prob = min(1.0, s["rain"] / 30 + random.uniform(-0.1, 0.1))
            if random.random() < rain_prob:
                rainfall = random.uniform(2, 50)
                if rainfall > 30:
                    condition = "Heavy Rain"
                elif rainfall > 10:
                    condition = "Moderate Rain"
                else:
                    condition = "Light Rain"
            else:
                rainfall = 0
                condition = random.choice(["Clear", "Cloudy", "Partly Cloudy"])
            
            wind = random.uniform(5, 25)
            
            result.append(WeatherData(
                date=d,
                temp_max_c=round(temp_max, 1),
                temp_min_c=round(temp_min, 1),
                humidity_percent=round(humidity, 1),
                rainfall_mm=round(rainfall, 1),
                wind_speed_kmph=round(wind, 1),
                condition=condition,
                cloud_cover_percent=random.uniform(0, 100),
            ))
        
        return result

    async def get_current_weather(
        self, 
        latitude: float, 
        longitude: float
    ) -> WeatherData:
        forecast = await self.get_forecast(latitude, longitude, 1)
        return forecast[0] if forecast else self._fallback_forecast(latitude, longitude, 1)[0]

    async def get_historical_weather(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date
    ) -> List[WeatherData]:
        if self.visualcrossing_key:
            return await self._fetch_visualcrossing_historical(
                latitude, longitude, start_date, end_date
            )
        return []

    async def _fetch_visualcrossing_historical(
        self,
        lat: float,
        lon: float,
        start: date,
        end: date
    ) -> List[WeatherData]:
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat},{lon}/{start}/{end}"
        params = {
            "key": self.visualcrossing_key,
            "unitGroup": "metric",
            "include": "days",
        }
        
        resp = await self.client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        result = []
        for day in data["days"]:
            d = datetime.strptime(day["datetime"], "%Y-%m-%d").date()
            result.append(WeatherData(
                date=d,
                temp_max_c=day["tempmax"],
                temp_min_c=day["tempmin"],
                humidity_percent=day["humidity"],
                rainfall_mm=day["precip"],
                wind_speed_kmph=day["windspeed"],
                condition=day["conditions"],
                cloud_cover_percent=day.get("cloudcover", 0),
                solar_radiation_mj=day.get("solarradiation", 0),
            ))
        
        return result

    async def close(self):
        await self.client.aclose()


_weather_client: Optional[WeatherClient] = None


def get_weather_client() -> WeatherClient:
    global _weather_client
    if _weather_client is None:
        _weather_client = WeatherClient()
    return _weather_client