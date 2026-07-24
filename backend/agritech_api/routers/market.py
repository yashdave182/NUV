from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, date, timedelta
import uuid

from agritech_api.schemas import (
    MandiPriceRequest, MandiPriceResponse, MandiPriceData,
    PriceTrendRequest, PriceTrendResponse, PriceTrendPoint,
    SellDecisionRequest, SellDecisionResponse, SellOption,
    TransportOptimizationRequest, TransportOptimizationResponse, TransportOption,
    StorageAdvisoryRequest, StorageAdvisoryResponse, StorageOption,
    SpoilagePredictionRequest, SpoilagePredictionResponse, SpoilagePredictionPoint,
    PriceAlertSetupRequest, PriceAlertSetupResponse,
    PriceAlertTriggerRequest, PriceAlertTriggerResponse,
    MarketIntelligenceRequest, MarketIntelligenceResponse,
    MandiListRequest, MandiListResponse, MandiInfo,
    CropType, MandiType, TransportMode, StorageCondition, DecisionAction, PriceTrend, AlertType,
    Language, Location,
)
from agritech_api.services.market_service import (
    generate_mandi_prices, get_price_trend, determine_price_trend,
    calculate_spoilage_curve, evaluate_sell_options, calculate_transport_cost,
    forecast_prices_ml as forecast_prices, check_price_alert as service_check_price_alert, get_mandis_for_crop,
)
from agritech_api.schemas.common import Language
from agritech_api.utils.cache import async_ttl_cache

router = APIRouter(prefix="/market", tags=["Market Intelligence"])


@router.post("/mandi-prices", response_model=MandiPriceResponse)
@async_ttl_cache(ttl_seconds=300)
async def get_mandi_prices(request: MandiPriceRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        prices = await generate_mandi_prices(request.crop_type, request.location.state or "Gujarat", 10, date.today())
        
        mandi_data = []
        for p in prices[:10]:
            mandi_data.append(MandiPriceData(
                mandi_name=p["mandi_name"],
                mandi_type=p["mandi_type"],
                district=p["district"],
                state=p["state"],
                distance_km=p["distance_km"],
                date=date.fromisoformat(p["date"]),
                min_price=p["min_price"],
                max_price=p["max_price"],
                modal_price=p["modal_price"],
                arrival_tonnes=p["arrival_tonnes"],
                variety=p.get("variety"),
                grade=None,
            ))
        
        best = max(mandi_data, key=lambda x: x.modal_price)
        avg_price = sum(m.modal_price for m in mandi_data) / len(mandi_data) if mandi_data else 0
        trend = determine_price_trend(await get_price_trend(request.crop_type, request.days))
        total_arrivals = sum(m.arrival_tonnes for m in mandi_data if m.arrival_tonnes)
        
        crop_name = request.crop_type.value.title() if hasattr(request.crop_type, 'value') else str(request.crop_type).title()
        best_mandi = best.mandi_name
        best_price = best.modal_price
        trend_str = trend.value if hasattr(trend, 'value') else str(trend)
        sms = f"{crop_name}: Best price ₹{best_price}/q at {best_mandi}. Avg: ₹{avg_price:.0f}/q. Trend: {trend_str}. Check {len(mandi_data)} mandis."
        
        return MandiPriceResponse(
            request_id=request_id,
            phone=request.phone,
            crop_type=request.crop_type,
            prices=mandi_data,
            best_price=best,
            average_modal_price=round(avg_price),
            price_trend=trend,
            total_arrivals_tonnes=round(total_arrivals, 1),
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/price-trend", response_model=PriceTrendResponse)
async def get_price_trend_endpoint(request: PriceTrendRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        history = await get_price_trend(request.crop_type, request.days)
        trend = determine_price_trend(history)
        
        trend_points = []
        for h in history:
            trend_points.append(PriceTrendPoint(
                date=date.fromisoformat(h["date"]),
                modal_price=h["price_per_quintal"],
                min_price=h["price_per_quintal"] - 50,
                max_price=h["price_per_quintal"] + 50,
                arrival_tonnes=h.get("arrival_tonnes"),
            ))
        
        prices = [h["price_per_quintal"] for h in history]
        stats = {
            "min": min(prices) if prices else 0,
            "max": max(prices) if prices else 0,
            "avg": sum(prices) / len(prices) if prices else 0,
            "current": prices[-1] if prices else 0,
            "change_7d": round((prices[-1] - prices[-8]) / prices[-8] * 100, 1) if len(prices) >= 8 and prices[-8] != 0 else 0,
            "change_30d": round((prices[-1] - prices[0]) / prices[0] * 100, 1) if len(prices) >= 30 and prices[0] != 0 else 0,
        }
        
        volatility = "high" if (max(prices) - min(prices)) / sum(prices) * len(prices) > 0.1 else "medium" if (max(prices) - min(prices)) / sum(prices) * len(prices) > 0.05 else "low"
        
        observations = [
            f"Current price: ₹{stats['current']}/q",
            f"7-day change: {stats['change_7d']}%",
            f"30-day change: {stats['change_30d']}%",
            f"Volatility: {volatility}",
        ]
        
        crop_name = request.crop_type.value.title()
        sms = f"{crop_name} trend: {trend.value}. Current ₹{stats['current']}/q (7d: {stats['change_7d']}%). Volatility: {volatility}."
        
        return PriceTrendResponse(
            request_id=request_id,
            phone=request.phone,
            crop_type=request.crop_type,
            mandi_name=request.mandi_name,
            trend_data=trend_points,
            trend=trend,
            statistics=stats,
            price_volatility=volatility,
            key_observations=observations,
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sell-decision", response_model=SellDecisionResponse)
async def get_sell_decision(request: SellDecisionRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        options_data = await evaluate_sell_options(
            request.crop_type,
            request.quantity_kg,
            request.storage_condition,
            request.current_mandi_price or 2500,
            request.farmer_price_expectation,
            request.days_stored,
            request.quality_grade,
            request.transport_mode,
            request.transport_cost_per_km,
            request.max_transport_distance_km,
            request.location.state or "Gujarat"
        )
        
        options = []
        for opt in options_data:
            options.append(SellOption(
                action=DecisionAction(opt["action"]),
                mandi_name=opt.get("mandi_name"),
                mandi_distance_km=opt.get("mandi_distance_km"),
                mandi_type=None,
                expected_price_per_quintal=opt["expected_price_per_quintal"],
                transport_cost=opt["transport_cost"],
                loading_unloading_cost=opt["handling_cost"],
                storage_cost=opt["storage_cost"],
                spoilage_loss_kg=opt["spoilage_loss_kg"],
                spoilage_loss_value=opt["spoilage_loss_kg"] * opt["expected_price_per_quintal"] / 100,
                total_costs=opt["transport_cost"] + opt["handling_cost"] + opt["storage_cost"],
                net_realisation_per_quintal=opt["net_realisation_per_quintal"],
                total_net_income=opt["total_net_income"],
                days_to_execute=opt["days_to_execute"],
                risk_level=opt["risk_level"],
                reasoning=opt["reasoning"],
                break_even_price=opt["expected_price_per_quintal"] - opt["net_realisation_per_quintal"] + opt["expected_price_per_quintal"],
            ))
        
        recommended = options[0] if options else None
        
        sensitivity = []
        base_price = request.current_mandi_price or 2500
        for pct in [-10, -5, 0, 5, 10]:
            test_price = base_price * (1 + pct / 100)
            test_options = await evaluate_sell_options(
                request.crop_type, request.quantity_kg, request.storage_condition,
                test_price, request.farmer_price_expectation, request.days_stored,
                request.quality_grade, request.transport_mode, request.transport_cost_per_km,
                request.max_transport_distance_km, request.location.state or "Gujarat"
            )
            sensitivity.append({
                "price_change_pct": pct,
                "test_price": round(test_price),
                "recommended_action": test_options[0]["action"] if test_options else "hold",
                "net_income": test_options[0]["total_net_income"] if test_options else 0,
            })
        
        situation = {
            "crop": request.crop_type.value,
            "quantity_kg": request.quantity_kg,
            "storage": request.storage_condition.value,
            "days_stored": request.days_stored,
            "current_price": request.current_mandi_price,
            "expected_price": request.farmer_price_expectation,
        }
        
        crop_name = request.crop_type.value.title()
        sms = f"{crop_name} {request.quantity_kg/100:.0f}q: {recommended.action.replace('_', ' ').title()} at {recommended.mandi_name or 'local'}. Net: ₹{recommended.net_realisation_per_quintal:.0f}/q. Total: ₹{recommended.total_net_income:.0f}. Risk: {recommended.risk_level}."
        
        return SellDecisionResponse(
            request_id=request_id,
            phone=request.phone,
            crop_type=request.crop_type,
            quantity_kg=request.quantity_kg,
            current_situation=situation,
            options=options,
            recommended_action=recommended,
            price_sensitivity=sensitivity,
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
            detailed_report_id=f"rpt_sell_{request_id}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transport-optimize", response_model=TransportOptimizationResponse)
async def optimize_transport(request: TransportOptimizationRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        distance = 50.0
        
        options = []
        for mode in TransportMode:
            cost_data = await calculate_transport_cost(distance, request.quantity_kg, mode, request.crop_type)
            options.append(TransportOption(
                transport_mode=mode,
                distance_km=distance,
                estimated_time_hours=cost_data["estimated_time_hours"],
                cost_per_km=cost_data["cost_per_km_per_tonne"],
                total_transport_cost=cost_data["variable_cost"],
                loading_unloading_cost=cost_data["loading_unloading_cost"],
                total_cost=cost_data["total_cost"],
                cost_per_quintal=cost_data["cost_per_quintal"],
                capacity_kg=cost_data["quantity_tonnes"] * 1000 / cost_data["trips_required"],
                trips_required=cost_data["trips_required"],
                reliability="high" if mode in [TransportMode.TRUCK, TransportMode.RAILWAY] else "medium",
                availability="immediate" if mode != TransportMode.RAILWAY else "within_48h",
            ))
        
        options.sort(key=lambda x: x.total_cost)
        recommended = options[0]
        savings = options[-1].total_cost - recommended.total_cost if len(options) > 1 else 0
        
        sms = f"Transport {request.quantity_kg/1000:.1f}t {distance:.0f}km: {recommended.transport_mode.value} ₹{recommended.total_cost:.0f} ({recommended.cost_per_quintal:.0f}/q). Save ₹{savings:.0f} vs {options[-1].transport_mode.value}. Time: {recommended.estimated_time_hours:.1f}h."
        
        return TransportOptimizationResponse(
            request_id=request_id,
            phone=request.phone,
            origin=request.origin,
            destination=request.destination,
            options=options,
            recommended_option=recommended,
            cost_savings_vs_default=round(savings),
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/storage-advisory", response_model=StorageAdvisoryResponse)
async def get_storage_advisory(request: StorageAdvisoryRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        current_spoilage = await calculate_spoilage_curve(
            request.crop_type, request.current_storage, request.current_moisture_percent,
            25, 60, request.days_stored, 30
        )
        
        options = []
        for storage in StorageCondition:
            spoilage = await calculate_spoilage_curve(
                request.crop_type, storage, request.current_moisture_percent,
                25, 60, request.days_stored, request.target_storage_days
            )
            
            setup_costs = {
                StorageCondition.OPEN: 0,
                StorageCondition.SHED: 5000,
                StorageCondition.WAREHOUSE: 20000,
                StorageCondition.COLD_STORAGE: 100000,
                StorageCondition.HERMETIC: 3000,
                StorageCondition.SILOS: 50000,
            }
            
            monthly_costs = {
                StorageCondition.OPEN: 0,
                StorageCondition.SHED: 500,
                StorageCondition.WAREHOUSE: 2000,
                StorageCondition.COLD_STORAGE: 15000,
                StorageCondition.HERMETIC: 200,
                StorageCondition.SILOS: 1000,
            }
            
            quality_retention = {
                StorageCondition.OPEN: "poor",
                StorageCondition.SHED: "fair",
                StorageCondition.WAREHOUSE: "good",
                StorageCondition.COLD_STORAGE: "excellent",
                StorageCondition.HERMETIC: "excellent",
                StorageCondition.SILOS: "good",
            }
            
            pest_control = storage in [StorageCondition.OPEN, StorageCondition.SHED, StorageCondition.WAREHOUSE]
            ventilation = storage in [StorageCondition.OPEN, StorageCondition.SHED, StorageCondition.WAREHOUSE]
            
            total_cost = setup_costs[storage] + monthly_costs[storage] * (request.target_storage_days / 30)
            final_quality = spoilage[-1]["remaining_quality_percent"] if spoilage else 50
            recovery = final_quality
            
            options.append(StorageOption(
                storage_condition=storage,
                setup_cost_inr=setup_costs[storage],
                monthly_cost_inr=monthly_costs[storage],
                spoilage_rate_per_month_percent=round((100 - final_quality) / max(1, request.target_storage_days / 30), 2),
                max_storage_months=12 if storage in [StorageCondition.COLD_STORAGE, StorageCondition.HERMETIC, StorageCondition.SILOS] else 6,
                quality_retention=quality_retention[storage],
                pest_control_needed=pest_control,
                ventilation_needed=ventilation,
                total_cost_for_period=round(total_cost),
                expected_recovery_percent=round(recovery),
            ))
        
        options.sort(key=lambda x: x.total_cost_for_period - x.expected_recovery_percent * 100)
        recommended = options[0]
        
        moisture_mgmt = [
            f"Current moisture: {request.current_moisture_percent}% - {'Dry to safe level' if request.current_moisture_percent > 12 else 'Maintain current level'}",
            "Use moisture meter for regular checks",
            "Aerate if moisture >14%",
            "Sun dry on clean surface if needed",
        ]
        
        pest_mgmt = [
            "Clean storage before use",
            "Treat structure with malathion 50% EC",
            "Use hermetic bags for small quantity",
            "Regular inspection weekly",
        ]
        
        monitoring = [
            "Check moisture weekly",
            "Inspect for pests/insects",
            "Monitor temperature",
            "Check for mold/off-odors",
        ]
        
        sms = f"Storage: {request.crop_type.value} {request.quantity_kg/100:.0f}q. Current: {request.current_storage.value} ({current_spoilage[0]['risk_level']} risk). Recommended: {recommended.storage_condition.value}. Recovery: {recommended.expected_recovery_percent}%. Cost: ₹{recommended.total_cost_for_period:.0f}."
        
        return StorageAdvisoryResponse(
            request_id=request_id,
            phone=request.phone,
            crop_type=request.crop_type,
            current_storage_assessment={
                "condition": request.current_storage.value,
                "moisture": request.current_moisture_percent,
                "risk": current_spoilage[0]["risk_level"],
                "days_stored": request.days_stored,
            },
            options=options,
            recommended_storage=recommended,
            moisture_management=moisture_mgmt,
            pest_management=pest_mgmt,
            monitoring_schedule=monitoring,
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
            detailed_report_id=f"rpt_store_{request_id}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/spoilage-prediction", response_model=SpoilagePredictionResponse)
async def predict_spoilage(request: SpoilagePredictionRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        temp = request.temperature_celsius or 25
        humidity = request.humidity_percent or 60
        
        predictions = await calculate_spoilage_curve(
            request.crop_type, request.storage_condition, request.current_moisture_percent,
            temp, humidity, request.days_stored, 30
        )
        
        pred_points = []
        for p in predictions:
            pred_points.append(SpoilagePredictionPoint(
                day=p["day"],
                remaining_quality_percent=p["remaining_quality_percent"],
                spoilage_loss_kg=p["spoilage_loss_kg_per_tonne"] * request.quantity_kg / 1000,
                marketable_kg=p["marketable_kg_per_tonne"] * request.quantity_kg / 1000,
                value_loss_inr=p["value_loss_inr_per_tonne"] * request.quantity_kg / 1000,
                risk_level=p["risk_level"],
            ))
        
        critical_day = next((p["day"] for p in predictions if p["risk_level"] in ["high", "critical"]), 30)
        action_day = next((p["day"] for p in predictions if p["risk_level"] == "medium"), 15)
        
        base_price = 2500
        total_value = request.quantity_kg / 100 * base_price
        total_at_risk = sum(p.value_loss_inr for p in pred_points)
        
        sms = f"Spoilage: {request.crop_type.value} {request.quantity_kg/100:.0f}q in {request.storage_condition.value}. Critical day: {critical_day} ({predictions[critical_day - request.days_stored]['risk_level']} risk). Act by day {action_day}. Value at risk: ₹{total_at_risk:.0f}."
        
        return SpoilagePredictionResponse(
            request_id=request_id,
            phone=request.phone,
            crop_type=request.crop_type,
            initial_quality=f"{100 - (predictions[0]['spoilage_loss_kg_per_tonne'] / 10):.0f}%",
            predictions=pred_points,
            critical_threshold_day=critical_day,
            recommended_action_day=action_day,
            total_value_at_risk=round(total_at_risk),
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
            detailed_report_id=f"rpt_spoil_{request_id}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/price-alert", response_model=PriceAlertSetupResponse)
async def setup_price_alert(request: PriceAlertSetupRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        alert_id = f"ALT_{request_id}"
        
        current_price = 2500
        
        sms = f"Price alert set: {request.crop_type.value} at {request.mandi_name or 'any mandi'}. Alert when price {'above' if request.threshold_direction == 'above' else 'below'} ₹{request.threshold_price}/q. Current: ₹{current_price}/q. Channel: {request.notification_channel}."
        
        return PriceAlertSetupResponse(
            request_id=request_id,
            phone=request.phone,
            alert_id=alert_id,
            status="active",
            crop_type=request.crop_type,
            mandi_name=request.mandi_name,
            alert_type=request.alert_type,
            threshold_price=request.threshold_price,
            threshold_direction=request.threshold_direction,
            current_price=current_price,
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/price-alert/check", response_model=PriceAlertTriggerResponse)
async def check_price_alert(request: PriceAlertTriggerRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        threshold = 2500
        direction = "above"
        
        triggered = await service_check_price_alert(threshold, request.current_price, direction)
        
        if triggered:
            message = f"ALERT: {request.alert_id} triggered! Price ₹{request.current_price}/q crossed threshold ₹{threshold}/q."
            action = "Consider selling immediately"
        else:
            message = f"Price ₹{request.current_price}/q. Threshold ₹{threshold}/q not crossed. Monitoring continues."
            action = "Continue monitoring"
        
        sms = f"Alert check: {request.current_price} vs {threshold}. {'TRIGGERED!' if triggered else 'Not triggered'}. {action}."
        
        return PriceAlertTriggerResponse(
            request_id=request_id,
            phone=request.phone,
            alert_id=request.alert_id,
            triggered=triggered,
            current_price=request.current_price,
            threshold_price=threshold,
            message=message,
            recommended_action=action,
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/market-intelligence", response_model=MarketIntelligenceResponse)
async def get_market_intelligence(request: MarketIntelligenceRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        current_prices = await generate_mandi_prices(request.crop_type, request.location.state or "Gujarat", 5, date.today())
        best = max(current_prices, key=lambda x: x["price_per_quintal"])
        avg = sum(p["price_per_quintal"] for p in current_prices) / len(current_prices)
        
        forecast = await forecast_prices(request.crop_type, request.horizon_days, current_price=avg)
        
        arrivals_forecast = []
        for i in range(request.horizon_days):
            d = date.today() + timedelta(days=i)
            arrivals_forecast.append({
                "date": d.isoformat(),
                "expected_arrivals_tonnes": round(1000 + i * 10),
                "trend": "increasing" if i < 7 else "stable",
            })
        
        demand_supply = {
            "demand_trend": "stable",
            "supply_trend": "increasing",
            "stock_to_use_ratio": "adequate",
            "export_demand": "moderate",
            "procurement_status": "ongoing",
        }
        
        recommendations = [
            f"Current avg price: ₹{avg:.0f}/q",
            f"Best mandi: {best['mandi_name']} at ₹{best['price_per_quintal']}/q",
            "Prices expected to remain stable",
            "Consider selling in lots",
            "Monitor government procurement",
        ]
        
        risks = [
            "Weather impact on arrivals",
            "Policy changes",
            "Global price fluctuations",
        ]
        
        sms = f"Market Intel {request.crop_type.value}: Avg ₹{avg:.0f}/q. Best: {best['mandi_name']} ₹{best['price_per_quintal']}/q. Forecast: stable. Sell in lots. Monitor procurement."
        
        return MarketIntelligenceResponse(
            request_id=request_id,
            phone=request.phone,
            crop_type=request.crop_type,
            current_market_summary={
                "average_price": round(avg),
                "best_price": best["price_per_quintal"],
                "best_mandi": best["mandi_name"],
                "total_arrivals": sum(p.get("arrival_tonnes", 0) for p in current_prices),
            },
            price_forecast=forecast,
            arrivals_forecast=arrivals_forecast,
            demand_supply_analysis=demand_supply,
            trading_recommendations=recommendations,
            risk_factors=risks,
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
            detailed_report_id=f"rpt_mkt_{request_id}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mandi-list", response_model=MandiListResponse)
async def get_mandi_list(request: MandiListRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        mandis = await get_mandis_for_crop(request.location.state or "Gujarat", request.crop_type or CropType.COTTON)
        
        mandi_infos = []
        for m in mandis[:10]:
            mandi_infos.append(MandiInfo(
                mandi_name=m["name"],
                mandi_type=m["type"],
                district=m["district"],
                state=m["state"],
                distance_km=m.get("distance_km", 25),
                contact_number="0265-XXXXXXX",
                email="apmc@district.gov.in",
                operating_hours="9:00 AM - 6:00 PM",
                facilities=["Weighbridge", "Godown", "Auction hall", "Bank"],
                crops_traded=[request.crop_type] if request.crop_type else [CropType.COTTON, CropType.WHEAT],
                e_nam_enabled=m["type"] == MandiType.E_NAM,
            ))
        
        sms = f"Found {len(mandi_infos)} mandis for {request.crop_type.value if request.crop_type else 'all crops'} near {request.location.district}. Closest: {mandi_infos[0].mandi_name} ({mandi_infos[0].distance_km:.0f}km)."
        
        return MandiListResponse(
            request_id=request_id,
            phone=request.phone,
            location=request.location,
            mandis=mandi_infos,
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))