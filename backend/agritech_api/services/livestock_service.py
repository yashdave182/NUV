import random
import math
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from ..schemas import (
    AnimalType, BreedType, VaccinationStatus, LactationStage,
    HousingType, VaccineDose, DewormerOption, FeedIngredient,
    FeedFormulation, Language, Location
)


VACCINATION_SCHEDULES = {
    AnimalType.COW: [
        VaccineDose(
            vaccine_name="FMD",
            disease_prevented="Foot and Mouth Disease",
            dose_number=1,
            recommended_age_months=4,
            route="Subcutaneous",
            dose_ml="2 ml",
            booster_interval_months=6,
            notes="Every 6 months",
            government_scheme="Livestock Health & Disease Control",
        ),
        VaccineDose(
            vaccine_name="HS",
            disease_prevented="Hemorrhagic Septicemia",
            dose_number=1,
            recommended_age_months=6,
            route="Subcutaneous",
            dose_ml="2 ml",
            booster_interval_months=6,
            notes="Before monsoon",
            government_scheme="Livestock Health & Disease Control",
        ),
        VaccineDose(
            vaccine_name="BQ",
            disease_prevented="Black Quarter",
            dose_number=1,
            recommended_age_months=6,
            route="Subcutaneous",
            dose_ml="2 ml",
            booster_interval_months=6,
            notes="Before monsoon",
            government_scheme="Livestock Health & Disease Control",
        ),
        VaccineDose(
            vaccine_name="Theileriosis",
            disease_prevented="Theileriosis (Crossbred)",
            dose_number=1,
            recommended_age_months=3,
            route="Subcutaneous",
            dose_ml="3 ml",
            booster_interval_months=12,
            notes="Crossbred only",
            government_scheme="State scheme",
        ),
        VaccineDose(
            vaccine_name="Brucellosis",
            disease_prevented="Brucellosis",
            dose_number=1,
            recommended_age_months=4,
            route="Subcutaneous",
            dose_ml="2 ml",
            booster_interval_months=0,
            notes="Calfhood vaccination (4-8 months), once only",
            government_scheme="National Animal Disease Control Programme",
        ),
        VaccineDose(
            vaccine_name="IBR",
            disease_prevented="Infectious Bovine Rhinotracheitis",
            dose_number=1,
            recommended_age_months=3,
            route="Intranasal",
            dose_ml="2 ml",
            booster_interval_months=6,
            notes="Crossbred dairy animals",
            government_scheme="State scheme",
        ),
    ],
    AnimalType.BUFFALO: [
        VaccineDose(
            vaccine_name="FMD",
            disease_prevented="Foot and Mouth Disease",
            dose_number=1,
            recommended_age_months=4,
            route="Subcutaneous",
            dose_ml="2 ml",
            booster_interval_months=6,
            notes="Every 6 months",
            government_scheme="Livestock Health & Disease Control",
        ),
        VaccineDose(
            vaccine_name="HS",
            disease_prevented="Hemorrhagic Septicemia",
            dose_number=1,
            recommended_age_months=6,
            route="Subcutaneous",
            dose_ml="2 ml",
            booster_interval_months=6,
            notes="Before monsoon",
            government_scheme="Livestock Health & Disease Control",
        ),
        VaccineDose(
            vaccine_name="BQ",
            disease_prevented="Black Quarter",
            dose_number=1,
            recommended_age_months=6,
            route="Subcutaneous",
            dose_ml="2 ml",
            booster_interval_months=6,
            notes="Before monsoon",
            government_scheme="Livestock Health & Disease Control",
        ),
        VaccineDose(
            vaccine_name="Brucellosis",
            disease_prevented="Brucellosis",
            dose_number=1,
            recommended_age_months=4,
            route="Subcutaneous",
            dose_ml="2 ml",
            booster_interval_months=0,
            notes="Calfhood vaccination (4-8 months), once only",
            government_scheme="National Animal Disease Control Programme",
        ),
    ],
    AnimalType.GOAT: [
        VaccineDose(
            vaccine_name="PPR",
            disease_prevented="Peste des Petits Ruminants",
            dose_number=1,
            recommended_age_months=3,
            route="Subcutaneous",
            dose_ml="1 ml",
            booster_interval_months=12,
            notes="Annual vaccination",
            government_scheme="PPR Eradication Programme",
        ),
        VaccineDose(
            vaccine_name="ET",
            disease_prevented="Enterotoxemia",
            dose_number=1,
            recommended_age_months=3,
            route="Subcutaneous",
            dose_ml="2 ml",
            booster_interval_months=6,
            notes="Every 6 months",
            government_scheme="Livestock Health & Disease Control",
        ),
        VaccineDose(
            vaccine_name="Goat Pox",
            disease_prevented="Goat Pox",
            dose_number=1,
            recommended_age_months=3,
            route="Subcutaneous",
            dose_ml="1 ml",
            booster_interval_months=12,
            notes="Annual in endemic areas",
            government_scheme="State scheme",
        ),
    ],
    AnimalType.SHEEP: [
        VaccineDose(
            vaccine_name="PPR",
            disease_prevented="Peste des Petits Ruminants",
            dose_number=1,
            recommended_age_months=3,
            route="Subcutaneous",
            dose_ml="1 ml",
            booster_interval_months=12,
            notes="Annual vaccination",
            government_scheme="PPR Eradication Programme",
        ),
        VaccineDose(
            vaccine_name="ET",
            disease_prevented="Enterotoxemia",
            dose_number=1,
            recommended_age_months=3,
            route="Subcutaneous",
            dose_ml="2 ml",
            booster_interval_months=6,
            notes="Every 6 months",
            government_scheme="Livestock Health & Disease Control",
        ),
        VaccineDose(
            vaccine_name="Sheep Pox",
            disease_prevented="Sheep Pox",
            dose_number=1,
            recommended_age_months=3,
            route="Subcutaneous",
            dose_ml="1 ml",
            booster_interval_months=12,
            notes="Annual in endemic areas",
            government_scheme="State scheme",
        ),
        VaccineDose(
            vaccine_name="Blue Tongue",
            disease_prevented="Blue Tongue",
            dose_number=1,
            recommended_age_months=6,
            route="Subcutaneous",
            dose_ml="1 ml",
            booster_interval_months=12,
            notes="Annual in endemic areas",
            government_scheme="State scheme",
        ),
    ],
}


DEWORMERS = [
    DewormerOption(
        dewormer_name="Fenbendazole",
        active_ingredient="Fenbendazole",
        dose_per_kg="5 mg/kg",
        route="Oral",
        withdrawal_milk_days=0,
        withdrawal_meat_days=7,
        safe_in_pregnancy=True,
        safe_in_lactation=True,
        target_parasites=["Roundworms", "Lungworms", "Tapeworms"],
        cost_per_dose_inr=15,
    ),
    DewormerOption(
        dewormer_name="Albendazole",
        active_ingredient="Albendazole",
        dose_per_kg="7.5 mg/kg",
        route="Oral",
        withdrawal_milk_days=3,
        withdrawal_meat_days=14,
        safe_in_pregnancy=False,
        safe_in_lactation=True,
        target_parasites=["Roundworms", "Tapeworms", "Flukes"],
        cost_per_dose_inr=12,
    ),
    DewormerOption(
        dewormer_name="Ivermectin",
        active_ingredient="Ivermectin",
        dose_per_kg="0.2 mg/kg",
        route="Subcutaneous",
        withdrawal_milk_days=28,
        withdrawal_meat_days=28,
        safe_in_pregnancy=False,
        safe_in_lactation=False,
        target_parasites=["Roundworms", "Mites", "Lice", "Ticks"],
        cost_per_dose_inr=25,
    ),
    DewormerOption(
        dewormer_name="Levamisole",
        active_ingredient="Levamisole",
        dose_per_kg="7.5 mg/kg",
        route="Oral",
        withdrawal_milk_days=3,
        withdrawal_meat_days=7,
        safe_in_pregnancy=True,
        safe_in_lactation=True,
        target_parasites=["Roundworms"],
        cost_per_dose_inr=8,
    ),
    DewormerOption(
        dewormer_name="Triclabendazole",
        active_ingredient="Triclabendazole",
        dose_per_kg="12 mg/kg",
        route="Oral",
        withdrawal_milk_days=3,
        withdrawal_meat_days=21,
        safe_in_pregnancy=False,
        safe_in_lactation=True,
        target_parasites=["Liver flukes"],
        cost_per_dose_inr=30,
    ),
]


FEED_INGREDIENTS_DB = {
    "maize": {"dm": 88, "cp": 9, "tdn": 82, "ca": 0.02, "p": 0.28, "cost": 18},
    "wheat_bran": {"dm": 89, "cp": 15, "tdn": 70, "ca": 0.12, "p": 1.2, "cost": 16},
    "rice_bran": {"dm": 90, "cp": 12, "tdn": 72, "ca": 0.07, "p": 1.6, "cost": 14},
    "soybean_meal": {"dm": 90, "cp": 48, "tdn": 85, "ca": 0.3, "p": 0.7, "cost": 45},
    "cottonseed_cake": {"dm": 92, "cp": 23, "tdn": 75, "ca": 0.18, "p": 0.6, "cost": 22},
    "groundnut_cake": {"dm": 92, "cp": 45, "tdn": 85, "ca": 0.2, "p": 0.6, "cost": 30},
    "mustard_cake": {"dm": 92, "cp": 38, "tdn": 78, "ca": 0.5, "p": 1.2, "cost": 20},
    "maize_gluten": {"dm": 90, "cp": 20, "tdn": 80, "ca": 0.05, "p": 0.5, "cost": 18},
    "dcp": {"dm": 95, "cp": 0, "tdn": 0, "ca": 24, "p": 18, "cost": 35},
    "mineral_mix": {"dm": 98, "cp": 0, "tdn": 0, "ca": 20, "p": 12, "cost": 60},
    "salt": {"dm": 100, "cp": 0, "tdn": 0, "ca": 0, "p": 0, "cost": 5},
    "molasses": {"dm": 75, "cp": 5, "tdn": 65, "ca": 0.8, "p": 0.1, "cost": 12},
    "urea": {"dm": 99, "cp": 288, "tdn": 0, "ca": 0, "p": 0, "cost": 20},
    "green_fodder": {"dm": 20, "cp": 2.5, "tdn": 13, "ca": 0.5, "p": 0.3, "cost": 2},
    "dry_fodder": {"dm": 90, "cp": 4, "tdn": 45, "ca": 0.4, "p": 0.2, "cost": 5},
    "silage": {"dm": 30, "cp": 2, "tdn": 18, "ca": 0.5, "p": 0.3, "cost": 3},
}


NUTRIENT_REQUIREMENTS = {
    AnimalType.COW: {
        LactationStage.EARLY: {"dm_kg": 18, "cp_kg": 2.5, "tdn_kg": 12, "ca_g": 70, "p_g": 45},
        LactationStage.MID: {"dm_kg": 16, "cp_kg": 2.0, "tdn_kg": 11, "ca_g": 60, "p_g": 40},
        LactationStage.LATE: {"dm_kg": 14, "cp_kg": 1.6, "tdn_kg": 9, "ca_g": 50, "p_g": 35},
        LactationStage.DRY: {"dm_kg": 11, "cp_kg": 1.0, "tdn_kg": 7, "ca_g": 40, "p_g": 25},
        LactationStage.HEIFER: {"dm_kg": 8, "cp_kg": 0.8, "tdn_kg": 5, "ca_g": 30, "p_g": 20},
    },
    AnimalType.BUFFALO: {
        LactationStage.EARLY: {"dm_kg": 18, "cp_kg": 2.5, "tdn_kg": 12, "ca_g": 70, "p_g": 45},
        LactationStage.MID: {"dm_kg": 16, "cp_kg": 2.0, "tdn_kg": 11, "ca_g": 60, "p_g": 40},
        LactationStage.LATE: {"dm_kg": 14, "cp_kg": 1.6, "tdn_kg": 9, "ca_g": 50, "p_g": 35},
        LactationStage.DRY: {"dm_kg": 11, "cp_kg": 1.0, "tdn_kg": 7, "ca_g": 40, "p_g": 25},
        LactationStage.HEIFER: {"dm_kg": 8, "cp_kg": 0.8, "tdn_kg": 5, "ca_g": 30, "p_g": 20},
    },
    AnimalType.GOAT: {
        LactationStage.EARLY: {"dm_kg": 2.5, "cp_kg": 0.35, "tdn_kg": 1.6, "ca_g": 8, "p_g": 5},
        LactationStage.MID: {"dm_kg": 2.0, "cp_kg": 0.28, "tdn_kg": 1.3, "ca_g": 6, "p_g": 4},
        LactationStage.LATE: {"dm_kg": 1.8, "cp_kg": 0.25, "tdn_kg": 1.1, "ca_g": 5, "p_g": 3},
        LactationStage.DRY: {"dm_kg": 1.5, "cp_kg": 0.18, "tdn_kg": 0.9, "ca_g": 4, "p_g": 2},
    },
    AnimalType.SHEEP: {
        LactationStage.EARLY: {"dm_kg": 2.5, "cp_kg": 0.35, "tdn_kg": 1.6, "ca_g": 8, "p_g": 5},
        LactationStage.MID: {"dm_kg": 2.0, "cp_kg": 0.28, "tdn_kg": 1.3, "ca_g": 6, "p_g": 4},
        LactationStage.LATE: {"dm_kg": 1.8, "cp_kg": 0.25, "tdn_kg": 1.1, "ca_g": 5, "p_g": 3},
        LactationStage.DRY: {"dm_kg": 1.5, "cp_kg": 0.18, "tdn_kg": 0.9, "ca_g": 4, "p_g": 2},
    },
}


def get_vaccination_schedule(
    animal_type: AnimalType,
    age_months: int,
    last_vaccination_date: Optional[date] = None,
    last_vaccine_name: Optional[str] = None,
    pregnancy_month: Optional[int] = None,
) -> List[VaccineDose]:
    schedule = VACCINATION_SCHEDULES.get(animal_type, [])
    today = date.today()
    
    result = []
    for vaccine in schedule:
        due_date = None
        status = "pending"
        
        if last_vaccination_date and vaccine.vaccine_name.lower() == last_vaccine_name.lower():
            if vaccine.booster_interval_months and vaccine.booster_interval_months > 0:
                due_date = last_vaccination_date + timedelta(days=vaccine.booster_interval_months * 30)
                if due_date <= today:
                    status = "overdue" if (today - due_date).days > 30 else "due"
                else:
                    status = "pending"
            else:
                status = "completed"
        else:
            age_at_due = vaccine.recommended_age_months
            if age_months >= age_at_due:
                due_date = today - timedelta(days=(age_months - age_at_due) * 30)
                status = "overdue"
            else:
                due_date = today + timedelta(days=(age_at_due - age_months) * 30)
                status = "pending"
        
        if pregnancy_month and pregnancy_month > 5:
            if vaccine.vaccine_name in ["Brucellosis", "FMD"]:
                notes = vaccine.notes + " - Consult vet during late pregnancy"
            else:
                notes = vaccine.notes
        else:
            notes = vaccine.notes
        
        result.append(VaccineDose(
            vaccine_name=vaccine.vaccine_name,
            disease_prevented=vaccine.disease_prevented,
            dose_number=vaccine.dose_number,
            recommended_age_months=vaccine.recommended_age_months,
            recommended_date=due_date,
            status=status,
            route=vaccine.route,
            dose_ml=vaccine.dose_ml,
            booster_interval_months=vaccine.booster_interval_months,
            notes=notes,
            government_scheme=vaccine.government_scheme,
        ))
    
    return result


def get_deworming_schedule(
    animal_type: AnimalType,
    age_months: int,
    weight_kg: float,
    last_deworming_date: Optional[date] = None,
    lactation_stage: Optional[LactationStage] = None,
    pregnancy_month: Optional[int] = None,
    faecal_egg_count: Optional[int] = None,
) -> Dict[str, Any]:
    
    schedule = []
    
    if last_deworming_date:
        days_since = (date.today() - last_deworming_date).days
        if days_since > 90:
            schedule.append({
                "action": "Deworming due",
                "timeline": "Immediate",
                "reason": f"Last deworming {days_since} days ago (>3 months)",
            })
        elif days_since > 60:
            schedule.append({
                "action": "Plan deworming",
                "timeline": "Within 30 days",
                "reason": f"Last deworming {days_since} days ago",
            })
    else:
        schedule.append({
            "action": "Deworming due",
            "timeline": "Immediate",
            "reason": "No deworming history available",
        })
    
    if faecal_egg_count:
        if faecal_egg_count > 500:
            schedule.append({
                "action": "High worm burden - Deworm immediately",
                "timeline": "Immediate",
                "reason": f"FEC: {faecal_egg_count} epg (High)",
            })
        elif faecal_egg_count > 200:
            schedule.append({
                "action": "Moderate worm burden - Deworm soon",
                "timeline": "Within 15 days",
                "reason": f"FEC: {faecal_egg_count} epg (Moderate)",
            })
        else:
            schedule.append({
                "action": "Low worm burden - Routine deworming",
                "timeline": "As per schedule",
                "reason": f"FEC: {faecal_egg_count} epg (Low)",
            })
    
    if lactation_stage == LactationStage.EARLY:
        schedule.append({
            "action": "Post-partum deworming",
            "timeline": "2-3 weeks after calving",
            "reason": "Reduced immunity post-calving",
        })
    
    if pregnancy_month and pregnancy_month > 6:
        schedule.append({
            "action": "Use pregnancy-safe dewormer only",
            "timeline": "Consult veterinarian",
            "reason": f"Pregnancy month {pregnancy_month}",
        })
    
    recommended = []
    for dewormer in DEWORMERS:
        if pregnancy_month and pregnancy_month > 4 and not dewormer.safe_in_pregnancy:
            continue
        if lactation_stage and not dewormer.safe_in_lactation:
            continue
        recommended.append(dewormer)
    
    if not recommended:
        recommended = [d for d in DEWORMERS if d.safe_in_pregnancy and d.safe_in_lactation]
    
    fec_interpretation = None
    if faecal_egg_count is not None:
        if faecal_egg_count < 100:
            fec_interpretation = "Low burden - routine deworming sufficient"
        elif faecal_egg_count < 500:
            fec_interpretation = "Moderate burden - deworming recommended"
        elif faecal_egg_count < 1000:
            fec_interpretation = "High burden - immediate deworming needed"
        else:
            fec_interpretation = "Very high burden - deworm + management changes"
    
    return {
        "schedule": schedule,
        "recommended_dewormers": recommended[:3],
        "faecal_egg_count_interpretation": fec_interpretation,
    }


def formulate_feed(
    animal_type: AnimalType,
    weight_kg: float,
    lactation_stage: Optional[LactationStage],
    milk_yield_litres: Optional[float],
    pregnancy_month: Optional[int],
    available_ingredients: List[str],
    budget_per_kg: Optional[float],
) -> Dict[str, Any]:
    
    req = NUTRIENT_REQUIREMENTS.get(animal_type, {}).get(lactation_stage, None)
    if not req:
        req = {"dm_kg": 16, "cp_kg": 2.0, "tdn_kg": 11, "ca_g": 60, "p_g": 40}
    
    if milk_yield_litres and milk_yield_litres > 10:
        req = req.copy()
        req["dm_kg"] *= 1.1
        req["cp_kg"] *= 1.2
        req["tdn_kg"] *= 1.1
    
    if pregnancy_month and pregnancy_month > 6:
        req = req.copy()
        req["dm_kg"] *= 1.15
        req["cp_kg"] *= 1.2
        req["ca_g"] *= 1.5
        req["p_g"] *= 1.3
    
    ingredients_to_use = available_ingredients if available_ingredients else [
        "maize", "wheat_bran", "soybean_meal", "cottonseed_cake", "green_fodder", "dry_fodder", "mineral_mix", "salt"
    ]
    
    formulations = []
    
    for _ in range(3):
        formula = {}
        remaining = {k: v for k, v in req.items()}
        
        for ing_name in ingredients_to_use:
            if ing_name not in FEED_INGREDIENTS_DB:
                continue
            ing = FEED_INGREDIENTS_DB[ing_name]
            
            max_possible = remaining.get("dm_kg", 10) / (ing["dm"] / 100)
            if ing_name in ["mineral_mix", "salt"]:
                qty = random.uniform(0.03, 0.08) * weight_kg / 500
            elif ing_name in ["green_fodder", "silage"]:
                qty = random.uniform(0.5, 2.0) * weight_kg / 500
            elif ing_name == "dry_fodder":
                qty = random.uniform(1.0, 3.0) * weight_kg / 500
            else:
                qty = random.uniform(0.1, 0.5) * weight_kg / 500
            
            qty = min(qty, max_possible)
            formula[ing_name] = round(qty, 2)
            
            for nut, req_val in remaining.items():
                if nut in ["dm_kg", "cp_kg", "tdn_kg"]:
                    nut_key = {"dm_kg": "dm", "cp_kg": "cp", "tdn_kg": "tdn"}[nut]
                    remaining[nut] = max(0, req_val - qty * ing[nut_key] / 100)
                elif nut in ["ca_g", "p_g"]:
                    nut_key = {"ca_g": "ca", "p_g": "p"}[nut]
                    remaining[nut] = max(0, req_val - qty * ing[nut_key] * 10)
        
        ingredients_list = []
        total_dm = total_cp = total_tdn = total_cost = 0
        
        for ing_name, qty in formula.items():
            if qty <= 0:
                continue
            ing = FEED_INGREDIENTS_DB[ing_name]
            ingredients_list.append(FeedIngredient(
                ingredient=ing_name,
                quantity_kg_per_day=round(qty, 2),
                cost_per_kg_inr=ing["cost"],
                dry_matter_percent=ing["dm"],
                crude_protein_percent=ing["cp"],
                tdn_percent=ing["tdn"],
                calcium_percent=ing.get("ca"),
                phosphorus_percent=ing.get("p"),
            ))
            total_dm += qty * ing["dm"] / 100
            total_cp += qty * ing["cp"] / 100
            total_tdn += qty * ing["tdn"] / 100
            total_cost += qty * ing["cost"]
        
        meets = (
            total_dm >= req.get("dm_kg", 0) * 0.9 and
            total_cp >= req.get("cp_kg", 0) * 0.9 and
            total_tdn >= req.get("tdn_kg", 0) * 0.9
        )
        
        deficiencies = []
        if total_dm < req.get("dm_kg", 0):
            deficiencies.append(f"DM short by {req.get('dm_kg',0)-total_dm:.1f} kg")
        if total_cp < req.get("cp_kg", 0):
            deficiencies.append(f"CP short by {req.get('cp_kg',0)-total_cp:.1f} kg")
        if total_tdn < req.get("tdn_kg", 0):
            deficiencies.append(f"TDN short by {req.get('tdn_kg',0)-total_tdn:.1f} kg")
        
        cost_per_litre = None
        if milk_yield_litres and milk_yield_litres > 0:
            cost_per_litre = round(total_cost / milk_yield_litres, 2)
        
        formulations.append(FeedFormulation(
            ingredients=ingredients_list,
            total_dry_matter_kg=round(total_dm, 2),
            total_crude_protein_kg=round(total_cp, 2),
            total_tdn_kg=round(total_tdn, 2),
            total_cost_per_day_inr=round(total_cost, 2),
            cost_per_litre_milk_inr=cost_per_litre,
            meets_requirements=meets,
            deficiencies=deficiencies,
        ))
    
    formulations.sort(key=lambda f: (not f.meets_requirements, f.total_cost_per_day_inr))
    
    return {
        "nutritional_requirements": req,
        "formulations": formulations,
        "recommended_formulation": formulations[0],
        "locally_available_substitutes": {
            "maize": ["wheat", "bajra", "sorghum"],
            "soybean_meal": ["cottonseed_cake", "groundnut_cake", "mustard_cake"],
            "green_fodder": ["silage", "hydroponic_fodder"],
            "dry_fodder": ["straw", "stover"],
        },
        "feeding_schedule": [
            "Divide concentrate into 2 feeds (morning/evening)",
            "Offer green fodder ad libitum",
            "Provide clean water at all times",
            "Mineral mixture 30-50g daily",
            "Salt lick available freely",
        ],
    }


def diagnose_health(
    animal_type: AnimalType,
    breed: Optional[BreedType],
    age_months: int,
    symptoms: List[str],
    duration_days: int,
    temperature: Optional[float],
    appetite: Optional[str],
    milk_change: Optional[str],
    faeces: Optional[str],
    respiration: Optional[str],
    behaviour: Optional[str],
    skin_lesions: Optional[str],
    discharge: Optional[str],
    lameness: Optional[bool],
    recent_vaccination: Optional[bool],
    recent_deworming: Optional[bool],
    herd_size: Optional[int],
    similar_cases: Optional[int],
) -> Dict[str, Any]:
    
    disease_db = {
        "Foot and Mouth Disease": {
            "animal_types": [AnimalType.COW, AnimalType.BUFFALO],
            "symptoms": ["fever", "salivation", "lameness", "blisters_mouth", "blisters_feet", "reduced_milk"],
            "key_features": ["Vesicles in mouth/feet", "High morbidity", "Drooling"],
            "urgency": "high",
        },
        "Hemorrhagic Septicemia": {
            "animal_types": [AnimalType.COW, AnimalType.BUFFALO],
            "symptoms": ["high_fever", "swelling_throat", "difficulty_breathing", "sudden_death"],
            "key_features": ["Hot painful throat swelling", "Rapid course", "High mortality"],
            "urgency": "emergency",
        },
        "Black Quarter": {
            "animal_types": [AnimalType.COW, AnimalType.BUFFALO],
            "symptoms": ["fever", "lameness", "swelling_muscle", "crepitus", "sudden_death"],
            "key_features": ["Gas gangrene", "Crepitus on palpation", "Rapid death"],
            "urgency": "emergency",
        },
        "Mastitis": {
            "animal_types": [AnimalType.COW, AnimalType.BUFFALO],
            "symptoms": ["udder_swelling", "udder_hot", "udder_painful", "milk_changes", "reduced_milk", "fever"],
            "key_features": ["Clinical signs in udder", "Milk abnormalities", "CMT positive"],
            "urgency": "high",
        },
        "Theileriosis": {
            "animal_types": [AnimalType.COW],
            "symptoms": ["fever", "anemia", "lymph_node_swelling", "jaundice", "reduced_milk", "weakness"],
            "key_features": ["Crossbred cattle", "Tick exposure", "Schizonts in lymph node"],
            "urgency": "high",
        },
        "Babesiosis": {
            "animal_types": [AnimalType.COW, AnimalType.BUFFALO],
            "symptoms": ["high_fever", "hemoglobinuria", "anemia", "jaundice", "reduced_milk"],
            "key_features": ["Red urine", "Tick exposure", "Intraerythrocytic parasites"],
            "urgency": "high",
        },
        "PPR": {
            "animal_types": [AnimalType.GOAT, AnimalType.SHEEP],
            "symptoms": ["fever", "nasal_discharge", "ocular_discharge", "diarrhea", "mouth_lesions", "pneumonia"],
            "key_features": ["Goats/sheep", "High mortality", "Mouth lesions"],
            "urgency": "high",
        },
        "Enterotoxemia": {
            "animal_types": [AnimalType.GOAT, AnimalType.SHEEP],
            "symptoms": ["sudden_death", "abdominal_pain", "diarrhea", "neurological_signs", "convulsions"],
            "key_features": ["Sudden death", "Young animals", "Overeating history"],
            "urgency": "emergency",
        },
        "Worm Infestation": {
            "animal_types": [AnimalType.COW, AnimalType.BUFFALO, AnimalType.GOAT, AnimalType.SHEEP],
            "symptoms": ["weight_loss", "diarrhea", "anemia", "bottle_jaw", "rough_coat", "reduced_milk"],
            "key_features": ["Chronic course", "Pale mucous membranes", "High FEC"],
            "urgency": "medium",
        },
        "Milk Fever": {
            "animal_types": [AnimalType.COW, AnimalType.BUFFALO],
            "symptoms": ["recumbency", "cold_ears", "low_temperature", "muscle_tremors", "constipation", "reduced_milk"],
            "key_features": ["Post-calving", "Hypocalcemia", "Responds to calcium"],
            "urgency": "emergency",
        },
        "Ketosis": {
            "animal_types": [AnimalType.COW, AnimalType.BUFFALO],
            "symptoms": ["reduced_milk", "weight_loss", "acetone_smell", "reduced_appetite", "firm_feces", "nervous_signs"],
            "key_features": ["Early lactation", "Negative energy balance", "Ketones in urine/milk"],
            "urgency": "medium",
        },
    }
    
    matches = []
    for disease, info in disease_db.items():
        if animal_type not in info["animal_types"]:
            continue
        
        matched_symptoms = [s for s in symptoms if any(s in ds for ds in info["symptoms"])]
        if matched_symptoms:
            prob = len(matched_symptoms) / len(info["symptoms"])
            if temperature and temperature > 40 and "fever" in info["symptoms"]:
                prob += 0.1
            if milk_change == "decreased" and "reduced_milk" in info["symptoms"]:
                prob += 0.1
            if faeces == "bloody" and "bloody_diarrhea" in info["symptoms"]:
                prob += 0.15
            
            matches.append({
                "disease_name": disease,
                "probability": round(min(prob, 0.95), 2),
                "matching_symptoms": matched_symptoms,
                "key_differentiating_features": info["key_features"],
                "urgency": info["urgency"],
            })
    
    matches.sort(key=lambda x: x["probability"], reverse=True)
    
    most_likely = matches[0] if matches else {
        "disease_name": "Undiagnosed",
        "probability": 0.0,
        "matching_symptoms": [],
        "key_differentiating_features": [],
        "urgency": "low",
    }
    
    immediate_actions = []
    if most_likely["urgency"] == "emergency":
        immediate_actions = [
            "Contact veterinarian IMMEDIATELY",
            "Isolate affected animal",
            "Do not wait - high mortality risk",
        ]
    elif most_likely["urgency"] == "high":
        immediate_actions = [
            "Contact veterinarian within 2-4 hours",
            "Isolate affected animal",
            "Provide supportive care (water, shade)",
        ]
    else:
        immediate_actions = [
            "Monitor closely",
            "Contact veterinarian within 24 hours",
            "Ensure clean water and feed",
        ]
    
    recommended_tests = [
        "CBC and blood smear",
        "Fecal examination (FEC)",
        "Milk CMT test" if animal_type in [AnimalType.COW, AnimalType.BUFFALO] else "Fecal culture",
    ]
    
    if "fever" in symptoms:
        recommended_tests.append("Blood smear for parasites")
    if "diarrhea" in symptoms:
        recommended_tests.append("Fecal culture/sensitivity")
    if discharge:
        recommended_tests.append("Swab for culture")
    
    treatment_suggestions = []
    if most_likely["disease_name"] == "Foot and Mouth Disease":
        treatment_suggestions = ["Supportive care", "Antiseptic mouth wash", "Soft feed", "Fly control", "Vaccinate contacts"]
    elif most_likely["disease_name"] == "Hemorrhagic Septicemia":
        treatment_suggestions = ["Antibiotics (Penicillin/Sulfa) - Vet only", "Anti-inflammatory", "Fluid therapy", "Vaccinate herd immediately"]
    elif most_likely["disease_name"] == "Mastitis":
        treatment_suggestions = ["Intramammary antibiotics", "Systemic antibiotics if systemic signs", "Frequent stripping", "Teat dip", "Milk culture/sensitivity"]
    elif most_likely["disease_name"] == "Theileriosis":
        treatment_suggestions = ["Buparvaquone (Vet only)", "Supportive care", "Blood transfusion if severe anemia", "Tick control"]
    elif most_likely["disease_name"] == "PPR":
        treatment_suggestions = ["Supportive care", "Antibiotics for secondary infection", "Fluid therapy", "Vaccinate remaining herd"]
    elif most_likely["disease_name"] == "Enterotoxemia":
        treatment_suggestions = ["Antitoxin (Vet only)", "Antibiotics", "Fluid therapy", "Vaccinate herd"]
    elif most_likely["disease_name"] == "Worm Infestation":
        treatment_suggestions = ["Appropriate dewormer (see deworming schedule)", "Improve sanitation", "Rotational grazing", "Repeat FEC in 14 days"]
    elif most_likely["disease_name"] == "Milk Fever":
        treatment_suggestions = ["IV Calcium borogluconate (Vet only)", "Oral calcium follow-up", "Monitor heart", "Prevent with anionic salts pre-calving"]
    elif most_likely["disease_name"] == "Ketosis":
        treatment_suggestions = ["Propylene glycol oral", "IV Glucose (Vet only)", "Improve energy intake", "Check for displaced abomasum"]
    else:
        treatment_suggestions = ["Symptomatic treatment under veterinary guidance", "Supportive care"]
    
    withdrawal = {
        "Antibiotics (intramammary)": 72,
        "Antibiotics (systemic)": 5,
        "Anti-inflammatory": 3,
        "Buparvaquone": 21,
        "Anthelmintics": 7,
    }
    
    preventive = [
        "Timely vaccination as per schedule",
        "Regular deworming",
        "Tick/ectoparasite control",
        "Clean housing and sanitation",
        "Balanced nutrition",
        "Quarantine new animals (21 days)",
        "Daily observation for early detection",
    ]
    
    requires_vet = most_likely["urgency"] in ["emergency", "high"]
    
    return {
        "differential_diagnoses": matches[:3],
        "most_likely": most_likely,
        "immediate_actions": immediate_actions,
        "recommended_tests": recommended_tests,
        "treatment_suggestions": treatment_suggestions,
        "withdrawal_periods": withdrawal,
        "preventive_measures": preventive,
        "requires_vet_visit": requires_vet,
    }


def get_breeding_advice(
    animal_type: AnimalType,
    age_months: int,
    weight_kg: float,
    bcs: Optional[float],
    lactation_number: Optional[int],
    last_calving_date: Optional[date],
    heat_signs: Optional[List[str]],
    ai_history: Optional[List[Dict]],
) -> Dict[str, Any]:
    
    if animal_type in [AnimalType.COW, AnimalType.BUFFALO]:
        puberty_age = 18 if animal_type == AnimalType.COW else 24
        optimal_weight = 300 if animal_type == AnimalType.COW else 350
    else:
        puberty_age = 7
        optimal_weight = 25
    
    heat_guide = [
        "Standing to be mounted (primary sign)",
        "Mounting other animals",
        "Clear mucous discharge from vulva",
        "Swollen, red vulva",
        "Restlessness, bellowing",
        "Decreased milk yield",
        "Frequent urination",
        "Chin resting on other animals",
    ]
    
    if heat_signs:
        observed = len(set(heat_signs) & set([s.lower().replace(" ", "_") for s in heat_guide]))
        heat_detected = observed >= 2
    else:
        heat_detected = False
    
    if last_calving_date:
        days_postpartum = (date.today() - last_calving_date).days
        voluntary_wait = 60
        if days_postpartum < voluntary_wait:
            breeding_window = f"Wait until {voluntary_wait} days post-calving ({voluntary_wait - days_postpartum} days remaining)"
        elif days_postpartum < 90:
            breeding_window = "OPTIMAL BREEDING PERIOD - Inseminate at next heat"
        elif days_postpartum < 120:
            breeding_window = "Breeding recommended - Conception rates declining"
        else:
            breeding_window = "EXTENDED OPEN PERIOD - Veterinary check needed"
    else:
        if age_months < puberty_age:
            breeding_window = f"Too young - Wait until {puberty_age} months age"
        elif weight_kg < optimal_weight:
            breeding_window = f"Underweight - Target {optimal_weight} kg before breeding"
        else:
            breeding_window = "Ready for breeding at next heat"
    
    ai_vs_natural = {
        "ai_advantages": [
            "Genetic improvement with proven bulls",
            "Disease control (no venereal disease risk)",
            "No need to maintain bull",
            "Sexed semen available",
            "Better record keeping",
        ],
        "natural_advantages": [
            "Higher conception rate in some conditions",
            "No technician required",
            "Lower upfront cost",
            "Bull detects heat naturally",
        ],
        "recommendation": "AI recommended for genetic improvement" if animal_type in [AnimalType.COW, AnimalType.BUFFALO] else "Natural service common for small ruminants",
    }
    
    bull_breeds = {
        AnimalType.COW: ["Gir", "Sahiwal", "Tharparkar", "Red Sindhi", "HF Cross (50-75%)", "Jersey Cross"],
        AnimalType.BUFFALO: ["Murrah", "Jaffrabadi", "Mehsana", "Surti", "Banni"],
        AnimalType.GOAT: ["Sirohi", "Jamunapari", "Beetal", "Osmanabadi", "Barbari"],
        AnimalType.SHEEP: ["Nellore", "Deccani", "Mandya", "Nilgiri", "Magra"],
    }
    
    preg_diagnosis = [
        "Day 28-35: Rectal palpation by veterinarian",
        "Day 30-35: Ultrasonography (most accurate)",
        "Day 45+: Palpation of fetal membrane slip",
        "Day 60+: Cotyledons palpable",
        "Milk progesterone test (Day 21-24 post-AI)",
    ]
    
    dry_period = [
        "Dry off 60 days before expected calving",
        "Abrupt dry-off for high yielders",
        "Dry cow therapy (intramammary antibiotics)",
        "Transition diet 3 weeks pre-calving",
        "Anionic salts for milk fever prevention",
        "Vaccinate for FMD/HS/BQ if due",
        "Deworm 2-3 weeks pre-calving",
    ]
    
    calving_prep = [
        "Clean, dry, well-bedded calving area",
        "Separate calving pen 2 weeks before due date",
        "Monitor for calving signs (udder filling, pelvic relaxation, mucous)",
        "Calving kit: clean ropes, iodine, towels, gloves, lubricant",
        "Colostrum feeding within 1 hour (10% body weight)",
        "Navel dip with 7% iodine",
        "Post-calving: calcium, energy, monitor for retained placenta/milk fever",
    ]
    
    return {
        "heat_detection_guide": heat_guide,
        "heat_detected": heat_detected,
        "optimal_breeding_window": breeding_window,
        "ai_vs_natural_service": ai_vs_natural,
        "recommended_bull_breeds": bull_breeds.get(animal_type, []),
        "pregnancy_diagnosis_timeline": preg_diagnosis,
        "dry_period_management": dry_period,
        "calving_preparation": calving_prep,
    }


def assess_milk_quality(
    fat_percent: float,
    snf_percent: float,
    density: Optional[float],
    ph: Optional[float],
    temperature: Optional[float],
    scc: Optional[int],
    bacterial_count: Optional[int],
    antibiotic_residue: Optional[bool],
) -> Dict[str, Any]:
    
    parameters = {
        "fat_percent": {"value": fat_percent, "standard_min": 3.5, "standard_max": 6.0, "unit": "%"},
        "snf_percent": {"value": snf_percent, "standard_min": 8.5, "standard_max": 10.0, "unit": "%"},
    }
    
    if density:
        parameters["density"] = {"value": density, "standard_min": 1.028, "standard_max": 1.034, "unit": "g/ml"}
    if ph:
        parameters["ph"] = {"value": ph, "standard_min": 6.6, "standard_max": 6.8, "unit": "pH"}
    if temperature:
        parameters["temperature"] = {"value": temperature, "standard_min": 0, "standard_max": 4, "unit": "°C"}
    if scc:
        parameters["scc"] = {"value": scc, "standard_max": 200000, "unit": "cells/ml"}
    if bacterial_count:
        parameters["bacterial_count"] = {"value": bacterial_count, "standard_max": 100000, "unit": "cfu/ml"}
    if antibiotic_residue is not None:
        parameters["antibiotic_residue"] = {"value": "Positive" if antibiotic_residue else "Negative", "standard": "Negative", "unit": ""}
    
    compliance = {}
    issues = []
    
    if fat_percent < 3.5:
        compliance["fat"] = "Below standard"
        issues.append(f"Low fat ({fat_percent}% < 3.5%) - Check diet energy/fiber")
    elif fat_percent > 6.0:
        compliance["fat"] = "Above standard"
    else:
        compliance["fat"] = "Compliant"
    
    if snf_percent < 8.5:
        compliance["snf"] = "Below standard"
        issues.append(f"Low SNF ({snf_percent}% < 8.5%) - Check protein/energy balance")
    elif snf_percent > 10.0:
        compliance["snf"] = "Above standard"
    else:
        compliance["snf"] = "Compliant"
    
    if density and (density < 1.028 or density > 1.034):
        compliance["density"] = "Non-compliant"
        issues.append("Abnormal density - Possible water adulteration or mastitis")
    elif density:
        compliance["density"] = "Compliant"
    
    if ph and (ph < 6.6 or ph > 6.8):
        compliance["ph"] = "Non-compliant"
        issues.append("Abnormal pH - Possible mastitis or adulteration")
    elif ph:
        compliance["ph"] = "Compliant"
    
    if temperature and temperature > 4:
        compliance["temperature"] = "Non-compliant"
        issues.append("High temperature - Poor cooling, bacterial growth risk")
    elif temperature:
        compliance["temperature"] = "Compliant"
    
    if scc and scc > 200000:
        compliance["scc"] = "High"
        issues.append(f"High SCC ({scc:,}) - Subclinical mastitis likely")
    elif scc:
        compliance["scc"] = "Compliant"
    
    if bacterial_count and bacterial_count > 100000:
        compliance["bacterial_count"] = "High"
        issues.append(f"High bacterial count ({bacterial_count:,}) - Hygiene/cooling issue")
    elif bacterial_count:
        compliance["bacterial_count"] = "Compliant"
    
    if antibiotic_residue:
        compliance["antibiotic"] = "Positive - REJECTED"
        issues.append("ANTIBIOTIC RESIDUE DETECTED - Milk cannot be sold")
    elif antibiotic_residue is not None:
        compliance["antibiotic"] = "Compliant"
    
    if "REJECTED" in str(compliance.get("antibiotic", "")):
        grade = "Rejected"
    elif len([k for k, v in compliance.items() if v in ["Non-compliant", "High", "Below standard"]]) >= 2:
        grade = "Grade-C"
    elif len([k for k, v in compliance.items() if v in ["Non-compliant", "High", "Below standard"]]) == 1:
        grade = "Grade-B"
    else:
        grade = "Grade-A"
    
    corrective = []
    if fat_percent < 3.5:
        corrective.append("Increase dietary energy (grains, bypass fat)")
        corrective.append("Ensure adequate fiber for butterfat synthesis")
    if snf_percent < 8.5:
        corrective.append("Increase dietary protein (bypass protein)")
        corrective.append("Balance energy:protein ratio")
    if scc and scc > 200000:
        corrective.append("CMT test all quarters")
        corrective.append("Treat clinical/subclinical mastitis")
        corrective.append("Improve milking hygiene")
        corrective.append("Post-milking teat dip")
    if bacterial_count and bacterial_count > 100000:
        corrective.append("Clean milking equipment thoroughly")
        corrective.append("Rapid cooling to <4°C")
        corrective.append("Check water quality")
    if antibiotic_residue:
        corrective.append("Observe withdrawal period strictly")
        corrective.append("Maintain treatment records")
        corrective.append("Test before sending to dairy")
    
    pricing = {
        "Grade-A": 1.0,
        "Grade-B": 0.9,
        "Grade-C": 0.75,
        "Rejected": 0.0,
    }
    
    return {
        "quality_grade": grade,
        "parameters": parameters,
        "compliance_status": compliance,
        "issues_identified": issues,
        "corrective_actions": corrective,
        "pricing_impact": {k: round(v * 100, 1) for k, v in pricing.items()},
    }


def get_disease_alerts(location: Location, animal_type: Optional[AnimalType], radius_km: int) -> List[Dict[str, Any]]:
    alerts = [
        {
            "disease_name": "Foot and Mouth Disease",
            "affected_villages": ["Village A", "Village B"],
            "cases_reported": 12,
            "deaths_reported": 0,
            "outbreak_date": (date.today() - timedelta(days=5)).isoformat(),
            "risk_level": "high",
            "symptoms_to_watch": ["Fever", "Salivation", "Lameness", "Mouth/foot vesicles", "Drop in milk"],
            "preventive_measures": ["Vaccinate immediately", "Restrict animal movement", "Disinfect premises", "Report to vet dept"],
            "vaccination_recommended": True,
            "vaccination_details": "FMD vaccine (bivalent/trivalent) - Contact veterinary officer",
            "helpline_number": "1800-180-1551",
        },
        {
            "disease_name": "Hemorrhagic Septicemia",
            "affected_villages": ["Village C"],
            "cases_reported": 5,
            "deaths_reported": 3,
            "outbreak_date": (date.today() - timedelta(days=2)).isoformat(),
            "risk_level": "critical",
            "symptoms_to_watch": ["High fever", "Throat swelling", "Difficulty breathing", "Sudden death"],
            "preventive_measures": ["Emergency vaccination", "Antibiotic prophylaxis for contacts", "Strict quarantine", "Immediate vet attention"],
            "vaccination_recommended": True,
            "vaccination_details": "HS vaccine - Oil adjuvant, single dose",
            "helpline_number": "1800-180-1551",
        },
    ]
    
    if animal_type in [AnimalType.GOAT, AnimalType.SHEEP]:
        alerts.append({
            "disease_name": "PPR",
            "affected_villages": ["Village D", "Village E"],
            "cases_reported": 25,
            "deaths_reported": 8,
            "outbreak_date": (date.today() - timedelta(days=10)).isoformat(),
            "risk_level": "high",
            "symptoms_to_watch": ["Fever", "Nasal/ocular discharge", "Diarrhea", "Mouth lesions", "Pneumonia"],
            "preventive_measures": ["PPR vaccination", "Isolate sick animals", "Disinfect", "Report immediately"],
            "vaccination_recommended": True,
            "vaccination_details": "PPR vaccine (live attenuated) - Annual",
            "helpline_number": "1800-180-1551",
        })
    
    return alerts


def get_livestock_schemes(location: Location, animal_type: Optional[AnimalType], farmer_category: Optional[str]) -> List[Dict[str, Any]]:
    schemes = [
        {
            "scheme_name": "National Livestock Mission (NLM)",
            "sponsoring_agency": "Department of Animal Husbandry & Dairying",
            "description": "Entrepreneurship development, breed improvement, feed/fodder development",
            "eligibility": ["Farmers/entrepreneurs/SHGs/FPOs", "For poultry, piggery, small ruminants, feed units"],
            "benefits": ["25-50% capital subsidy", "Interest subvention", "Training & capacity building"],
            "subsidy_amount": "Up to 50% project cost",
            "application_process": ["Prepare DPR with vet officer", "Submit to District AH Officer", "State level approval", "Fund release through bank"],
            "documents_required": ["DPR", "Land documents", "Aadhaar/PAN", "Bank details", "Caste certificate if applicable"],
            "contact_info": "District Animal Husbandry Officer",
            "deadline": "Ongoing",
            "website": "https://nlm.udyamimitra.in",
        },
        {
            "scheme_name": "Livestock Insurance Scheme",
            "sponsoring_agency": "Department of Animal Husbandry & Dairying",
            "description": "Insurance for milch animals against death",
            "eligibility": ["Milch cattle/buffalo (indigenous/crossbred)", "Max 2 animals per beneficiary", "Subsidy: 50% General, 70% SC/ST/BPL"],
            "benefits": ["Market value coverage", "Premium subsidized", "Claim on death with PM"],
            "subsidy_amount": "50-70% premium subsidy",
            "application_process": ["Animal valuation by vet", "Proposal to insurance company", "Pay beneficiary share", "Policy issuance"],
            "documents_required": ["Health certificate", "Animal ID (ear tag/photo)", "Aadhaar", "Bank passbook", "Caste/BPL certificate if applicable"],
            "contact_info": "District Animal Husbandry Officer / Insurance company",
            "deadline": "Ongoing",
            "website": "https://dahd.nic.in",
        },
        {
            "scheme_name": "Rashtriya Gokul Mission",
            "sponsoring_agency": "Department of Animal Husbandry & Dairying",
            "description": "Conservation and development of indigenous breeds",
            "eligibility": ["Farmers with indigenous breeds", "Gaushalas", "Breeders' associations"],
            "benefits": ["Incentive for elite animals", "Bull mother farms", "Genomic selection", "AI network strengthening"],
            "subsidy_amount": "As per component guidelines",
            "application_process": ["Apply through State Implementing Agency", "Animal identification & registration", "Performance recording"],
            "documents_required": ["Animal registration", "Performance records", "Aadhaar", "Land documents"],
            "contact_info": "State Livestock Development Board",
            "deadline": "Ongoing",
            "website": "https://dahd.nic.in",
        },
        {
            "scheme_name": "Dairy Processing & Infrastructure Development Fund (DIDF)",
            "sponsoring_agency": "Department of Animal Husbandry & Dairying / NABARD",
            "description": "Infrastructure for milk processing, value addition, cold chain",
            "eligibility": ["Milk unions", "Federations", "FPOs", "Private dairies (with conditions)"],
            "benefits": ["Loan at 6% interest", "Long repayment period", "Processing plant, chilling, powder plant"],
            "subsidy_amount": "Interest subvention",
            "application_process": ["DPR preparation", "Submit through State Govt to NABARD", "Sanction & disbursement"],
            "documents_required": ["DPR", "Registration certificates", "Financial statements", "Land documents", "Environmental clearance"],
            "contact_info": "NABARD Regional Office / State Dairy Federation",
            "deadline": "Ongoing",
            "website": "https://www.nabard.org",
        },
    ]
    
    if farmer_category in ["sc_st", "women", "small", "marginal"]:
        for s in schemes:
            s["priority_note"] = "Priority for SC/ST/Women/Small/Marginal farmers"
    
    return schemes