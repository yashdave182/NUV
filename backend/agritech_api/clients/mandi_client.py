import os
import asyncio
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import httpx
import random

from agritech_api.schemas import CropType, MandiType


@dataclass
class MandiPrice:
    mandi_name: str
    mandi_type: MandiType
    district: str
    state: str
    crop: CropType
    variety: Optional[str]
    min_price: int
    max_price: int
    modal_price: int
    arrival_tonnes: float
    date: date
    source: str = "agmarknet"


class MandiClient:
    def __init__(self):
        self.agmarknet_key = os.getenv("AGMARKNET_API_KEY")
        self.data_gov_key = os.getenv("DATA_GOV_IN_API_KEY")
        self.client = httpx.AsyncClient(timeout=30.0)
        self._cache: Dict[str, List[MandiPrice]] = {}
        self._cache_ttl = 3600

    async def get_prices(
        self,
        crop: CropType,
        state: str = "Gujarat",
        district: Optional[str] = None,
        days: int = 7
    ) -> List[MandiPrice]:
        cache_key = f"{crop.value}_{state}_{district}_{days}"
        
        if cache_key in self._cache:
            cached_time, cached_prices = self._cache[cache_key]
            if (datetime.now() - cached_time).total_seconds() < self._cache_ttl:
                return cached_prices

        prices = await self._fetch_from_sources(crop, state, district, days)
        
        if not prices:
            prices = self._generate_mock_prices(crop, state, district, days)
        
        self._cache[cache_key] = (datetime.now(), prices)
        return prices

    async def _fetch_from_sources(
        self,
        crop: CropType,
        state: str,
        district: Optional[str],
        days: int
    ) -> List[MandiPrice]:
        results = []
        
        if self.agmarknet_key:
            try:
                agmark = await self._fetch_agmarknet(crop, state, district, days)
                results.extend(agmark)
            except Exception as e:
                print(f"[MandiClient] Agmarknet error: {e}")
        
        if self.data_gov_key and not results:
            try:
                datagov = await self._fetch_data_gov_in(crop, state, district, days)
                results.extend(datagov)
            except Exception as e:
                print(f"[MandiClient] Data.gov.in error: {e}")
        
        return results

    async def _fetch_agmarknet(
        self,
        crop: CropType,
        state: str,
        district: Optional[str],
        days: int
    ) -> List[MandiPrice]:
        url = "https://api.agmarknet.gov.in/v1/prices"
        params = {
            "api_key": self.agmarknet_key,
            "commodity": crop.value,
            "state": state,
            "from_date": (date.today() - timedelta(days=days)).isoformat(),
            "to_date": date.today().isoformat(),
        }
        if district:
            params["district"] = district
        
        resp = await self.client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        prices = []
        for item in data.get("data", []):
            prices.append(MandiPrice(
                mandi_name=item.get("market", ""),
                mandi_type=MandiType.APMC,
                district=item.get("district", ""),
                state=item.get("state", state),
                crop=crop,
                variety=item.get("variety"),
                min_price=int(item.get("min_price", 0)),
                max_price=int(item.get("max_price", 0)),
                modal_price=int(item.get("modal_price", 0)),
                arrival_tonnes=float(item.get("arrival", 0)),
                date=datetime.strptime(item.get("date", ""), "%Y-%m-%d").date(),
                source="agmarknet",
            ))
        
        return prices

    async def _fetch_data_gov_in(
        self,
        crop: CropType,
        state: str,
        district: Optional[str],
        days: int
    ) -> List[MandiPrice]:
        url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        params = {
            "api-key": self.data_gov_key,
            "format": "json",
            "filters[commodity]": crop.value,
            "filters[state]": state,
            "limit": 1000,
        }
        if district:
            params["filters[district]"] = district
        
        resp = await self.client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        prices = []
        for record in data.get("records", []):
            try:
                prices.append(MandiPrice(
                    mandi_name=record.get("market", ""),
                    mandi_type=MandiType(record.get("market_type", "APMC").upper()),
                    district=record.get("district", ""),
                    state=record.get("state", state),
                    crop=crop,
                    variety=record.get("variety"),
                    min_price=int(record.get("min_price", 0)),
                    max_price=int(record.get("max_price", 0)),
                    modal_price=int(record.get("modal_price", 0)),
                    arrival_tonnes=float(record.get("arrival", 0)),
                    date=datetime.strptime(record.get("arrival_date", ""), "%d/%m/%Y").date(),
                    source="data.gov.in",
                ))
            except Exception:
                continue
        
        return prices

    def _generate_mock_prices(
        self,
        crop: CropType,
        state: str,
        district: Optional[str],
        days: int
    ) -> List[MandiPrice]:
        base_prices = {
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
        
        mandis = {
            "Gujarat": {
                "Ahmedabad": ["Ahmedabad APMC", "Ahmedabad E-NAM"],
                "Rajkot": ["Rajkot APMC", "Rajkot FPO Market"],
                "Surat": ["Surat APMC"],
                "Vadodara": ["Vadodara APMC"],
                "Junagadh": ["Junagadh APMC"],
                "Bhavnagar": ["Bhavnagar APMC"],
            },
            "Maharashtra": {
                "Pune": ["Pune APMC", "Pune E-NAM"],
                "Nashik": ["Nashik APMC"],
                "Aurangabad": ["Aurangabad APMC"],
            },
            "Rajasthan": {
                "Jaipur": ["Jaipur APMC", "Jaipur E-NAM"],
                "Jodhpur": ["Jodhpur APMC"],
            },
            "Madhya Pradesh": {
                "Indore": ["Indore APMC", "Indore E-NAM"],
                "Bhopal": ["Bhopal APMC"],
            },
            "Uttar Pradesh": {
                "Lucknow": ["Lucknow APMC"],
                "Kanpur": ["Kanpur APMC"],
            },
        }
        
        state_mandis = mandis.get(state, mandis["Gujarat"])
        if district and district in state_mandis:
            selected = {district: state_mandis[district]}
        else:
            selected = state_mandis
        
        base = base_prices.get(crop, 2500)
        prices = []
        
        for d in range(days):
            current_date = date.today() - timedelta(days=d)
            for dist, mandi_list in selected.items():
                for mandi_name in mandi_list:
                    variation = random.uniform(0.92, 1.08)
                    modal = base * variation
                    
                    min_p = int(modal * random.uniform(0.95, 0.98))
                    max_p = int(modal * random.uniform(1.02, 1.05))
                    modal_p = int(modal * random.uniform(0.98, 1.02))
                    arrival = random.uniform(50, 2000)
                    
                    prices.append(MandiPrice(
                        mandi_name=mandi_name,
                        mandi_type=MandiType.APMC if "APMC" in mandi_name else MandiType.E_NAM,
                        district=dist,
                        state=state,
                        crop=crop,
                        variety=None,
                        min_price=min_p,
                        max_price=max_p,
                        modal_price=modal_p,
                        arrival_tonnes=round(arrival, 1),
                        date=current_date,
                        source="mock",
                    ))
        
        return prices

    async def get_price_trend(
        self,
        crop: CropType,
        state: str = "Gujarat",
        days: int = 30
    ) -> List[Dict[str, Any]]:
        prices = await self.get_prices(crop, state, days=days)
        
        trend = {}
        for p in prices:
            d = p.date.isoformat()
            if d not in trend:
                trend[d] = {"prices": [], "arrivals": []}
            trend[d]["prices"].append(p.modal_price)
            trend[d]["arrivals"].append(p.arrival_tonnes)
        
        result = []
        for d in sorted(trend.keys()):
            vals = trend[d]
            result.append({
                "date": d,
                "avg_price": sum(vals["prices"]) / len(vals["prices"]),
                "total_arrival": sum(vals["arrivals"]),
                "mandi_count": len(vals["prices"]),
            })
        
        return result

    async def search_mandis(
        self,
        crop: CropType,
        latitude: float,
        longitude: float,
        radius_km: float = 50
    ) -> List[Dict[str, Any]]:
        return []

    async def close(self):
        await self.client.aclose()


_mandi_client: Optional[MandiClient] = None


def get_mandi_client() -> MandiClient:
    global _mandi_client
    if _mandi_client is None:
        _mandi_client = MandiClient()
    return _mandi_client