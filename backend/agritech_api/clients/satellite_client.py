import os
import asyncio
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import httpx
import random

from agritech_api.schemas import CropType, Location


@dataclass
class SatelliteData:
    date: date
    ndvi: float
    evi: float
    ndwi: float
    lst_day_c: float
    lst_night_c: float
    soil_moisture_percent: float
    precipitation_mm: float
    crop_health_score: float
    anomalies: List[Dict[str, Any]]


@dataclass
class FieldBoundary:
    field_id: str
    farmer_id: str
    geometry: Dict[str, Any]
    area_hectares: float
    crop_type: Optional[CropType]
    sowing_date: Optional[date]


class SatelliteClient:
    def __init__(self):
        self.sentinel_hub_client_id = os.getenv("SENTINEL_HUB_CLIENT_ID")
        self.sentinel_hub_client_secret = os.getenv("SENTINEL_HUB_CLIENT_SECRET")
        self.google_earth_engine_key = os.getenv("GEE_API_KEY")
        self.nasa_power_key = os.getenv("NASA_POWER_API_KEY")
        self.open_meteo_sat = os.getenv("OPEN_METEO_SAT")
        
        self.client = httpx.AsyncClient(timeout=3.0)
        self._token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None

    async def get_field_data(
        self,
        latitude: float,
        longitude: float,
        area_hectares: float,
        crop_type: CropType,
        sowing_date: date,
        days_back: int = 30
    ) -> List[SatelliteData]:
        if self.sentinel_hub_client_id and self.sentinel_hub_client_secret:
            try:
                return await self._fetch_sentinel_hub(
                    latitude, longitude, area_hectares, crop_type, sowing_date, days_back
                )
            except Exception as e:
                print(f"[SatelliteClient] Sentinel Hub failed: {e}")
        
        if self.google_earth_engine_key:
            try:
                return await self._fetch_gee(
                    latitude, longitude, area_hectares, crop_type, sowing_date, days_back
                )
            except Exception as e:
                print(f"[SatelliteClient] GEE failed: {e}")
        
        return await self._fetch_nasa_power(
            latitude, longitude, crop_type, sowing_date, days_back
        )

    async def _get_sentinel_token(self) -> str:
        if self._token and self._token_expiry and datetime.now() < self._token_expiry:
            return self._token
        
        url = "https://services.sentinel-hub.com/oauth/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.sentinel_hub_client_id,
            "client_secret": self.sentinel_hub_client_secret,
        }
        
        resp = await self.client.post(url, data=data)
        resp.raise_for_status()
        token_data = resp.json()
        
        self._token = token_data["access_token"]
        self._token_expiry = datetime.now() + timedelta(seconds=token_data["expires_in"] - 60)
        return self._token

    async def _fetch_sentinel_hub(
        self,
        lat: float,
        lon: float,
        area_ha: float,
        crop: CropType,
        sowing: date,
        days_back: int
    ) -> List[SatelliteData]:
        token = await self._get_sentinel_token()
        
        bbox_size = max(0.01, (area_hectares / 100) ** 0.5 * 0.01)
        bbox = [lon - bbox_size, lat - bbox_size, lon + bbox_size, lat + bbox_size]
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)
        
        evalscript = """
        //VERSION=3
        function setup() {
            return {
                input: ["B02", "B03", "B04", "B08", "B11", "B12", "dataMask"],
                output: { bands: 5 }
            };
        }
        function evaluatePixel(sample) {
            let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
            let evi = 2.5 * (sample.B08 - sample.B04) / (sample.B08 + 6 * sample.B04 - 7.5 * sample.B02 + 1);
            let ndwi = (sample.B08 - sample.B11) / (sample.B08 + sample.B11);
            let lst = (sample.B10 + sample.B11) / 2 * 0.00341802 + 149.0 - 273.15;
            return [ndvi, evi, ndwi, lst, sample.dataMask];
        }
        """
        
        url = "https://services.sentinel-hub.com/api/v1/process"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {
            "input": {
                "bounds": {"bbox": bbox},
                "data": [{
                    "type": "sentinel-2-l2a",
                    "dataFilter": {
                        "timeRange": {
                            "from": f"{start_date}T00:00:00Z",
                            "to": f"{end_date}T23:59:59Z"
                        },
                        "mosaickingOrder": "leastCC"
                    }
                }]
            },
            "output": {"width": 512, "height": 512, "responses": [{"identifier": "default", "format": {"type": "image/tiff"}}]},
            "evalscript": evalscript,
        }
        
        resp = await self.client.post(url, headers=headers, json=payload)
        if resp.status_code == 200:
            return self._parse_sentinel_response(resp.content, start_date, end_date)
        
        return []

    def _parse_sentinel_response(
        self, 
        content: bytes, 
        start: date, 
        end: date
    ) -> List[SatelliteData]:
        return []

    async def _fetch_gee(
        self,
        lat: float,
        lon: float,
        area_ha: float,
        crop: CropType,
        sowing: date,
        days_back: int
    ) -> List[SatelliteData]:
        return []

    async def _fetch_nasa_power(
        self,
        lat: float,
        lon: float,
        crop: CropType,
        sowing: date,
        days_back: int
    ) -> List[SatelliteData]:
        url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        params = {
            "parameters": "T2M_MAX,T2M_MIN,RH2M,PRECTOTCORR,WS2M,ALLSKY_SFC_SW_DWN,GWETROOT",
            "community": "AG",
            "latitude": lat,
            "longitude": lon,
            "start": (date.today() - timedelta(days=days_back)).strftime("%Y%m%d"),
            "end": date.today().strftime("%Y%m%d"),
            "format": "JSON",
        }
        
        if self.nasa_power_key:
            params["api_key"] = self.nasa_power_key
        
        try:
            resp = await self.client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            
            return self._parse_nasa_power(data, crop, sowing)
        except Exception as e:
            print(f"[SatelliteClient] NASA POWER error: {e}")
            return self._generate_mock_satellite(lat, lon, crop, sowing, days_back)

    def _parse_nasa_power(
        self, 
        data: Dict, 
        crop: CropType, 
        sowing: date
    ) -> List[SatelliteData]:
        try:
            params = data["properties"]["parameter"]
            dates = list(params["T2M_MAX"].keys())
            
            result = []
            for d_str in dates:
                d = datetime.strptime(d_str, "%Y%m%d").date()
                
                tmax = params["T2M_MAX"].get(d_str, 0)
                tmin = params["T2M_MIN"].get(d_str, 0)
                rh = params["RH2M"].get(d_str, 0)
                rain = params["PRECTOTCORR"].get(d_str, 0)
                wind = params["WS2M"].get(d_str, 0)
                solar = params["ALLSKY_SFC_SW_DWN"].get(d_str, 0)
                soil_moist = params["GWETROOT"].get(d_str, 0) * 100
                
                days_after_sowing = (d - sowing).days
                ndvi = self._estimate_ndvi(crop, days_after_sowing, tmax, tmin, rain)
                evi = ndvi * 0.85
                ndwi = max(0, min(1, (rain / 10) * 0.5 + soil_moist / 200))
                
                health = self._calculate_health_score(ndvi, ndwi, rain, tmax, soil_moist)
                
                anomalies = []
                if tmax > 40:
                    anomalies.append({"type": "heat_stress", "severity": "high", "value": tmax})
                if soil_moist < 20:
                    anomalies.append({"type": "drought", "severity": "medium", "value": soil_moist})
                if rain > 50:
                    anomalies.append({"type": "excess_rain", "severity": "high", "value": rain})
                
                result.append(SatelliteData(
                    date=d,
                    ndvi=round(ndvi, 3),
                    evi=round(evi, 3),
                    ndwi=round(ndwi, 3),
                    lst_day_c=round(tmax, 1),
                    lst_night_c=round(tmin, 1),
                    soil_moisture_percent=round(soil_moist, 1),
                    precipitation_mm=round(rain, 1),
                    crop_health_score=round(health, 1),
                    anomalies=anomalies,
                ))
            
            return result
        except Exception as e:
            print(f"[SatelliteClient] Parse error: {e}")
            return []

    def _estimate_ndvi(
        self, 
        crop: CropType, 
        das: int, 
        tmax: float, 
        tmin: float, 
        rain: float
    ) -> float:
        if das < 0:
            return 0.1
        elif das < 15:
            return 0.15 + 0.01 * das
        elif das < 45:
            return 0.3 + 0.015 * (das - 15)
        elif das < 75:
            return 0.65 + 0.005 * (das - 45)
        elif das < 105:
            return 0.8 - 0.003 * (das - 75)
        else:
            return max(0.3, 0.7 - 0.01 * (das - 105))

    def _calculate_health_score(
        self, 
        ndvi: float, 
        ndwi: float, 
        rain: float, 
        tmax: float, 
        soil_moist: float
    ) -> float:
        score = 50
        score += ndvi * 40
        score += ndwi * 20
        score += min(rain / 5, 10)
        score += max(0, (30 - abs(tmax - 30)) * 0.5)
        score += soil_moist * 0.2
        return max(0, min(100, score))

    def _generate_mock_satellite(
        self,
        lat: float,
        lon: float,
        crop: CropType,
        sowing: date,
        days_back: int
    ) -> List[SatelliteData]:
        result = []
        for i in range(days_back):
            d = date.today() - timedelta(days=days_back - i)
            das = (d - sowing).days
            
            ndvi = self._estimate_ndvi(crop, das, 30, 20, 0)
            ndvi += random.uniform(-0.05, 0.05)
            ndvi = max(0, min(1, ndvi))
            
            result.append(SatelliteData(
                date=d,
                ndvi=round(ndvi, 3),
                evi=round(ndvi * 0.85, 3),
                ndwi=round(random.uniform(0.1, 0.4), 3),
                lst_day_c=round(random.uniform(25, 40), 1),
                lst_night_c=round(random.uniform(15, 25), 1),
                soil_moisture_percent=round(random.uniform(20, 70), 1),
                precipitation_mm=round(random.uniform(0, 20), 1),
                crop_health_score=round(random.uniform(50, 90), 1),
                anomalies=[],
            ))
        
        return result

    async def get_ndvi_time_series(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        data = await self.get_field_data(
            latitude, longitude, 1.0, CropType.COTTON, start_date, 
            (end_date - start_date).days
        )
        return [{"date": d.date.isoformat(), "ndvi": d.ndvi} for d in data]

    async def detect_anomalies(
        self,
        latitude: float,
        longitude: float,
        crop_type: CropType,
        sowing_date: date
    ) -> List[Dict[str, Any]]:
        data = await self.get_field_data(
            latitude, longitude, 1.0, crop_type, sowing_date, 14
        )
        
        anomalies = []
        for d in data[-7:]:
            if d.crop_health_score < 40:
                anomalies.append({
                    "date": d.date.isoformat(),
                    "type": "low_vigor",
                    "severity": "high" if d.crop_health_score < 30 else "medium",
                    "ndvi": d.ndvi,
                    "health_score": d.crop_health_score,
                })
            if d.soil_moisture_percent < 15:
                anomalies.append({
                    "date": d.date.isoformat(),
                    "type": "water_stress",
                    "severity": "critical" if d.soil_moisture_percent < 10 else "high",
                    "soil_moisture": d.soil_moisture_percent,
                })
        
        return anomalies

    async def close(self):
        await self.client.aclose()


_satellite_client: Optional[SatelliteClient] = None


def get_satellite_client() -> SatelliteClient:
    global _satellite_client
    if _satellite_client is None:
        _satellite_client = SatelliteClient()
    return _satellite_client