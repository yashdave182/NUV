import random
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from ..schemas import (
    Language, Location, Gender, AgeGroup, HealthCategory,
    TriageLevel, VitalSigns, SymptomInput, ConfidenceLevel
)


DISEASE_SYMPTOMS = {
    "malaria": ["fever", "chills", "headache", "sweating", "nausea", "vomiting"],
    "dengue": ["fever", "severe_headache", "pain_behind_eyes", "joint_pain", "muscle_pain", "rash"],
    "typhoid": ["fever", "headache", "abdominal_pain", "diarrhea", "constipation", "weakness"],
    "diarrhea": ["loose_stools", "abdominal_cramps", "dehydration", "fever", "vomiting"],
    "pneumonia": ["cough", "fever", "difficulty_breathing", "chest_pain", "rapid_breathing"],
    "tuberculosis": ["cough_3weeks", "weight_loss", "night_sweats", "fever", "blood_in_sputum"],
    "covid19": ["fever", "cough", "loss_taste_smell", "difficulty_breathing", "fatigue"],
    "jaundice": ["yellow_eyes", "yellow_skin", "dark_urine", "fatigue", "abdominal_pain"],
    "anemia": ["fatigue", "pale_skin", "shortness_of_breath", "dizziness", "cold_hands"],
    "diabetes": ["frequent_urination", "excessive_thirst", "hunger", "weight_loss", "fatigue", "blurred_vision"],
    "hypertension": ["headache", "dizziness", "blurred_vision", "chest_pain", "difficulty_breathing"],
    "pregnancy_complication": ["vaginal_bleeding", "severe_headache", "vision_changes", "swelling", "reduced_fetal_movement"],
    "malnutrition_child": ["weight_loss", "stunted_growth", "weakness", "irritability", "frequent_illness"],
}


RED_FLAGS = {
    "general": [
        "difficulty_breathing",
        "chest_pain",
        "unconscious",
        "severe_bleeding",
        "high_fever_above_103",
        "severe_dehydration",
        "persistent_vomiting",
        "blood_in_vomit_or_stool",
    ],
    "pregnant": [
        "vaginal_bleeding",
        "severe_headache",
        "blurred_vision",
        "severe_abdominal_pain",
        "reduced_fetal_movement",
        "water_breaking_before_37_weeks",
        "convulsions",
    ],
    "child": [
        "not_drinking",
        "not_urinated_6_hours",
        "sunken_eyes",
        "lethargic_unconscious",
        "convulsions",
        "fast_breathing",
        "chest_indrawing",
    ],
    "elderly": [
        "confusion",
        "falls",
        "not_eating_drinking",
        "medication_side_effects",
    ],
}


VACCINATION_SCHEDULE = [
    {"vaccine": "BCG", "age": "At birth", "diseases": ["Tuberculosis"], "dose": 1},
    {"vaccine": "Hepatitis B", "age": "At birth", "diseases": ["Hepatitis B"], "dose": 1},
    {"vaccine": "OPV", "age": "At birth", "diseases": ["Polio"], "dose": 1},
    {"vaccine": "OPV", "age": "6 weeks", "diseases": ["Polio"], "dose": 2},
    {"vaccine": "Pentavalent", "age": "6 weeks", "diseases": ["Diphtheria", "Pertussis", "Tetanus", "Hepatitis B", "Hib"], "dose": 1},
    {"vaccine": "Rotavirus", "age": "6 weeks", "diseases": ["Rotavirus diarrhea"], "dose": 1},
    {"vaccine": "PCV", "age": "6 weeks", "diseases": ["Pneumococcal"], "dose": 1},
    {"vaccine": "OPV", "age": "10 weeks", "diseases": ["Polio"], "dose": 3},
    {"vaccine": "Pentavalent", "age": "10 weeks", "diseases": ["Diphtheria", "Pertussis", "Tetanus", "Hepatitis B", "Hib"], "dose": 2},
    {"vaccine": "Rotavirus", "age": "10 weeks", "diseases": ["Rotavirus diarrhea"], "dose": 2},
    {"vaccine": "PCV", "age": "10 weeks", "diseases": ["Pneumococcal"], "dose": 2},
    {"vaccine": "OPV", "age": "14 weeks", "diseases": ["Polio"], "dose": 4},
    {"vaccine": "Pentavalent", "age": "14 weeks", "diseases": ["Diphtheria", "Pertussis", "Tetanus", "Hepatitis B", "Hib"], "dose": 3},
    {"vaccine": "Rotavirus", "age": "14 weeks", "diseases": ["Rotavirus diarrhea"], "dose": 3},
    {"vaccine": "PCV", "age": "14 weeks", "diseases": ["Pneumococcal"], "dose": 3},
    {"vaccine": "IPV", "age": "14 weeks", "diseases": ["Polio"], "dose": 1},
    {"vaccine": "Measles-Rubella", "age": "9-12 months", "diseases": ["Measles", "Rubella"], "dose": 1},
    {"vaccine": "JE", "age": "9-12 months", "diseases": ["Japanese Encephalitis"], "dose": 1},
    {"vaccine": "Vitamin A", "age": "9 months", "diseases": ["Vitamin A deficiency"], "dose": 1},
    {"vaccine": "DPT Booster", "age": "16-24 months", "diseases": ["Diphtheria", "Pertussis", "Tetanus"], "dose": 1},
    {"vaccine": "OPV Booster", "age": "16-24 months", "diseases": ["Polio"], "dose": 1},
    {"vaccine": "Measles-Rubella", "age": "16-24 months", "diseases": ["Measles", "Rubella"], "dose": 2},
    {"vaccine": "JE", "age": "16-24 months", "diseases": ["Japanese Encephalitis"], "dose": 2},
    {"vaccine": "Vitamin A", "age": "16-24 months", "diseases": ["Vitamin A deficiency"], "dose": 2},
    {"vaccine": "DPT Booster", "age": "5-6 years", "diseases": ["Diphtheria", "Pertussis", "Tetanus"], "dose": 2},
    {"vaccine": "TT", "age": "10 years", "diseases": ["Tetanus"], "dose": 1},
    {"vaccine": "TT", "age": "16 years", "diseases": ["Tetanus"], "dose": 2},
    {"vaccine": "HPV", "age": "9-14 years (girls)", "diseases": ["Cervical cancer"], "dose": 2},
]


MATERNAL_SCHEDULE = [
    {"visit": "1st ANC", "weeks": "8-12", "checks": ["BP", "Weight", "Hb", "Urine", "Blood group", "HIV", "Syphilis"], "supplements": ["Folic acid", "Iron"]},
    {"visit": "2nd ANC", "weeks": "14-26", "checks": ["BP", "Weight", "Hb", "Urine", "Fundal height", "Fetal heart"], "supplements": ["Iron", "Calcium"]},
    {"visit": "3rd ANC", "weeks": "28-34", "checks": ["BP", "Weight", "Hb", "Urine", "Fundal height", "Fetal heart", "Presentation"], "supplements": ["Iron", "Calcium"]},
    {"visit": "4th ANC", "weeks": "36-40", "checks": ["BP", "Weight", "Hb", "Urine", "Fundal height", "Fetal heart", "Presentation", "Pelvic assessment"], "supplements": ["Iron", "Calcium"]},
]


def match_symptoms_to_conditions(symptoms: List[str]) -> List[Dict[str, Any]]:
    matches = []
    for condition, condition_symptoms in DISEASE_SYMPTOMS.items():
        matched = set(symptoms) & set(condition_symptoms)
        if matched:
            probability = len(matched) / len(condition_symptoms)
            matches.append({
                "condition": condition,
                "probability": round(probability, 2),
                "matched_symptoms": list(matched),
                "missing_symptoms": list(set(condition_symptoms) - matched),
            })
    
    matches.sort(key=lambda x: x["probability"], reverse=True)
    return matches[:5]


def check_red_flags(symptoms: List[str], age_group: AgeGroup, pregnant: bool = False) -> List[str]:
    flags = []
    
    if pregnant:
        for flag in RED_FLAGS["pregnant"]:
            if flag in symptoms:
                flags.append(flag.replace("_", " ").title())
    
    if age_group in [AgeGroup.INFANT, AgeGroup.TODDLER, AgeGroup.CHILD]:
        for flag in RED_FLAGS["child"]:
            if flag in symptoms:
                flags.append(flag.replace("_", " ").title())
    elif age_group == AgeGroup.SENIOR:
        for flag in RED_FLAGS["elderly"]:
            if flag in symptoms:
                flags.append(flag.replace("_", " ").title())
    
    for flag in RED_FLAGS["general"]:
        if flag in symptoms:
            flags.append(flag.replace("_", " ").title())
    
    return flags


def triage_level(symptoms: List[str], vital_signs: Optional[VitalSigns], age_group: AgeGroup, pregnant: bool = False) -> TriageLevel:
    red_flags = check_red_flags(symptoms, age_group, pregnant)
    if red_flags:
        return TriageLevel.RED
    
    if vital_signs:
        if vital_signs.temperature_c and vital_signs.temperature_c >= 39.5:
            return TriageLevel.RED
        if vital_signs.oxygen_saturation and vital_signs.oxygen_saturation < 90:
            return TriageLevel.RED
        if vital_signs.respiratory_rate and vital_signs.respiratory_rate > 30:
            return TriageLevel.YELLOW
        if vital_signs.heart_rate_bpm and vital_signs.heart_rate_bpm > 120:
            return TriageLevel.YELLOW
    
    high_risk_symptoms = ["chest_pain", "difficulty_breathing", "severe_abdominal_pain", "blood_in_stool", "blood_in_vomit"]
    if any(s in symptoms for s in high_risk_symptoms):
        return TriageLevel.YELLOW
    
    medium_risk = ["fever", "persistent_vomiting", "persistent_diarrhea", "severe_headache"]
    if any(s in symptoms for s in medium_risk):
        return TriageLevel.YELLOW
    
    return TriageLevel.GREEN


def generate_health_advisory(
    symptoms: List[str],
    age_group: AgeGroup,
    gender: Gender,
    pregnant: bool,
    vital_signs: Optional[VitalSigns],
    language: Language
) -> List[Dict[str, Any]]:
    
    advisories = []
    conditions = match_symptoms_to_conditions(symptoms)
    red_flags = check_red_flags(symptoms, age_group, pregnant)
    
    if red_flags:
        advisories.append({
            "category": HealthCategory.EMERGENCY.value,
            "title": "⚠️ EMERGENCY SIGNS DETECTED",
            "description": f"Red flags: {', '.join(red_flags)}. Seek immediate medical attention.",
            "confidence": ConfidenceLevel.HIGH.value,
            "rationale": "These symptoms indicate potentially life-threatening conditions",
            "action_items": [
                "Go to nearest emergency department immediately",
                "Call 108 ambulance if available",
                "Do not delay - time is critical",
            ],
            "timeline_hours": 1,
            "priority": 1,
            "warning_signs": red_flags,
        })
    
    if conditions:
        top = conditions[0]
        condition_name = top["condition"].replace("_", " ").title()
        prob = top["probability"]
        
        if prob > 0.6:
            conf = ConfidenceLevel.HIGH
        elif prob > 0.3:
            conf = ConfidenceLevel.MEDIUM
        else:
            conf = ConfidenceLevel.LOW
        
        advisories.append({
            "category": HealthCategory.GENERAL.value,
            "title": f"Possible {condition_name} (Confidence: {conf.value})",
            "description": f"Based on symptoms: {', '.join(top['matched_symptoms'])}. Probability: {int(prob*100)}%",
            "confidence": conf.value,
            "rationale": f"Matched {len(top['matched_symptoms'])} out of {len(DISEASE_SYMPTOMS.get(top['condition'], []))} typical symptoms",
            "action_items": get_condition_advice(top["condition"]),
            "timeline_hours": 24 if conf != ConfidenceLevel.HIGH else 6,
            "priority": 1 if conf == ConfidenceLevel.HIGH else 2,
            "warning_signs": get_warning_signs(top["condition"]),
        })
    
    if pregnant:
        advisories.append(get_pregnancy_advice(symptoms, vital_signs))
    
    if age_group in [AgeGroup.INFANT, AgeGroup.TODDLER, AgeGroup.CHILD]:
        advisories.append(get_child_advice(symptoms, age_group, vital_signs))
    
    if age_group == AgeGroup.SENIOR:
        advisories.append(get_elderly_advice(symptoms, vital_signs))
    
    return advisories


def get_condition_advice(condition: str) -> List[str]:
    advice_map = {
        "malaria": ["Get blood test (RDT/microscopy)", "Complete full course of ACT if positive", "Use mosquito net", "Eliminate breeding sites"],
        "dengue": ["Get NS1/IgM test", "Monitor platelet count daily", "Maintain hydration", "Avoid NSAIDs", "Watch for warning signs"],
        "typhoid": ["Blood culture/Widal test", "Complete antibiotic course", "Safe water and food", "Hand hygiene"],
        "diarrhea": ["ORS after each loose stool", "Continue feeding", "Zinc 20mg for 14 days (children)", "Seek help if blood in stool or signs of dehydration"],
        "pneumonia": ["Chest X-ray if available", "Complete antibiotic course", "Monitor breathing rate", "Oxygen if saturation <94%"],
        "tuberculosis": ["Sputum CBNAAT test", "Start DOTS treatment if positive", "Screen family contacts", "Nutritional support"],
        "covid19": ["RAT/RT-PCR test", "Isolate 7 days", "Monitor oxygen saturation", "Seek help if breathing difficulty"],
        "jaundice": ["Liver function tests", "Hepatitis A/E/B/C serology", "Avoid alcohol/hepatotoxic drugs", "Adequate nutrition"],
        "anemia": ["CBC with peripheral smear", "Iron/folic acid/B12 as per cause", "Deworming", "Iron-rich diet"],
        "diabetes": ["Fasting/HbA1c test", "Diet modification", "Regular exercise", "Medication adherence", "Foot care"],
        "hypertension": ["BP monitoring", "Low salt diet", "Regular medication", "Stress management", "Eye/kidney check"],
    }
    return advice_map.get(condition, ["Consult doctor for proper diagnosis", "Follow prescribed treatment", "Monitor symptoms"])


def get_warning_signs(condition: str) -> List[str]:
    warnings = {
        "dengue": ["Severe abdominal pain", "Persistent vomiting", "Bleeding gums/nose", "Rapid breathing", "Fatigue/restlessness"],
        "malaria": ["Severe anemia", "Cerebral symptoms", "Kidney failure", "Pulmonary edema"],
        "diarrhea": ["Sunken eyes", "Skin pinch >2 sec", "Not drinking", "Blood in stool", "High fever"],
        "pneumonia": ["Chest indrawing", "Stridor", "Cyanosis", "Unable to drink", "Convulsions"],
        "pregnancy_complication": ["Vaginal bleeding", "Severe headache", "Vision changes", "Reduced fetal movement", "Convulsions"],
    }
    return warnings.get(condition, ["Worsening symptoms", "New symptoms appear", "No improvement in 2-3 days"])


def get_pregnancy_advice(symptoms: List[str], vital_signs: Optional[VitalSigns]) -> Dict[str, Any]:
    if any(s in symptoms for s in ["vaginal_bleeding", "severe_headache", "vision_changes", "reduced_fetal_movement"]):
        return {
            "category": HealthCategory.MATERNAL.value,
            "title": "🚨 Pregnancy Emergency",
            "description": "Symptoms suggest possible pregnancy complication",
            "confidence": ConfidenceLevel.HIGH.value,
            "rationale": "These are danger signs in pregnancy requiring immediate evaluation",
            "action_items": ["Go to nearest FRU/medical college immediately", "Call 108/102 ambulance", "Do not wait"],
            "timeline_hours": 1,
            "priority": 1,
            "warning_signs": ["Vaginal bleeding", "Severe headache", "Vision changes", "Reduced fetal movement", "Convulsions"],
        }
    
    return {
        "category": HealthCategory.MATERNAL.value,
        "title": "Pregnancy Care Reminder",
        "description": "Regular ANC visits are essential for safe pregnancy",
        "confidence": ConfidenceLevel.HIGH.value,
        "rationale": "Preventive care reduces maternal and infant mortality",
        "action_items": [
            "Attend all 4 ANC visits on schedule",
            "Take Iron-Folic acid daily",
            "Take Calcium after 14 weeks",
            "TT vaccination at 16 and 20 weeks",
            "Institutional delivery planning",
        ],
        "timeline_hours": 168,
        "priority": 3,
        "warning_signs": [],
    }


def get_child_advice(symptoms: List[str], age_group: AgeGroup, vital_signs: Optional[VitalSigns]) -> Dict[str, Any]:
    if age_group == AgeGroup.INFANT:
        return {
            "category": HealthCategory.CHILD.value,
            "title": "Infant Care",
            "description": "Infants are vulnerable - monitor closely",
            "confidence": ConfidenceLevel.HIGH.value,
            "rationale": "Immature immune system, rapid deterioration possible",
            "action_items": [
                "Exclusive breastfeeding till 6 months",
                "Monitor feeding, urine output, activity",
                "Complete immunization schedule",
                "Kangaroo mother care for low birth weight",
            ],
            "timeline_hours": 24,
            "priority": 2,
            "warning_signs": ["Not feeding", "Less urine", "Lethargy", "Fever >38°C", "Fast breathing"],
        }
    else:
        return {
            "category": HealthCategory.CHILD.value,
            "title": "Child Health",
            "description": "Monitor growth and development",
            "confidence": ConfidenceLevel.MEDIUM.value,
            "rationale": "Early intervention improves outcomes",
            "action_items": [
                "Regular growth monitoring",
                "Complete immunization",
                "Deworming every 6 months",
                "Vitamin A supplementation",
                "Balanced diet with local foods",
            ],
            "timeline_hours": 168,
            "priority": 3,
            "warning_signs": ["Weight loss", "Not playing", "Recurrent illness", "Delayed milestones"],
        }


def get_elderly_advice(symptoms: List[str], vital_signs: Optional[VitalSigns]) -> Dict[str, Any]:
    return {
        "category": HealthCategory.GENERAL.value,
        "title": "Elderly Care",
        "description": "Elderly need special attention for chronic conditions",
        "confidence": ConfidenceLevel.MEDIUM.value,
        "rationale": "Multiple comorbidities, polypharmacy, fall risk",
        "action_items": [
            "Regular BP/sugar monitoring",
            "Medication review with doctor",
            "Fall prevention at home",
            "Social engagement",
            "Regular eye/ear/dental checkups",
        ],
        "timeline_hours": 168,
        "priority": 3,
        "warning_signs": ["Confusion", "Falls", "Not eating", "Medication side effects", "Incontinence"],
    }


def get_vaccination_schedule(child_dob: date) -> Dict[str, Any]:
    today = date.today()
    age_days = (today - child_dob).days
    age_months = age_days / 30.44
    
    schedule = []
    for v in VACCINATION_SCHEDULE:
        due_date = calculate_due_date(child_dob, v["age"])
        is_due = due_date <= today
        is_overdue = (today - due_date).days > 30 if is_due else False
        
        schedule.append({
            "vaccine_name": v["vaccine"],
            "recommended_age": v["age"],
            "dose_number": v["dose"],
            "diseases_prevented": v["diseases"],
            "due_date": due_date.isoformat(),
            "is_due": is_due,
            "is_overdue": is_overdue,
            "status": "overdue" if is_overdue else ("due" if is_due else "upcoming"),
        })
    
    upcoming = [v for v in schedule if v["status"] in ["due", "overdue"]]
    completed = [v for v in schedule if v["status"] == "upcoming"]
    
    return {
        "child_age_months": round(age_months, 1),
        "schedule": schedule,
        "upcoming": upcoming[:5],
        "missed": [v for v in schedule if v["status"] == "overdue"],
    }


def calculate_due_date(dob: date, age_str: str) -> date:
    import re
    if "birth" in age_str.lower():
        return dob
    
    match = re.search(r"(\d+(?:\.\d+)?)\s*(week|month|year)", age_str)
    if not match:
        return dob
    
    value = float(match.group(1))
    unit = match.group(2)
    
    if unit == "week":
        return dob + timedelta(weeks=value)
    elif unit == "month":
        return dob + timedelta(days=int(value * 30.44))
    elif unit == "year":
        return dob + timedelta(days=int(value * 365.25))
    
    return dob


def find_health_camps(location: Location, radius_km: int, category: Optional[HealthCategory]) -> List[Dict[str, Any]]:
    camps = [
        {
            "name": "Weekly PHC Camp",
            "type": "Primary Health Centre",
            "location": f"{location.taluka} PHC",
            "distance_km": random.uniform(2, 15),
            "days": ["Monday", "Wednesday", "Friday"],
            "timings": "9:00 AM - 1:00 PM",
            "services": ["General OPD", "ANC", "Immunization", "NCD screening"],
            "contact": "104",
        },
        {
            "name": "Mobile Medical Unit",
            "type": "MMU",
            "location": f"Village {location.village or 'nearby'}",
            "distance_km": random.uniform(1, 10),
            "days": ["Tuesday", "Thursday"],
            "timings": "10:00 AM - 2:00 PM",
            "services": ["General OPD", "Free medicines", "Basic lab tests"],
            "contact": "104",
        },
        {
            "name": "Specialist Camp",
            "type": "District Hospital Outreach",
            "location": f"{location.district} HQ",
            "distance_km": random.uniform(20, 50),
            "days": ["1st Saturday monthly"],
            "timings": "9:00 AM - 3:00 PM",
            "services": ["Eye camp", "Dental", "Gynecology", "Pediatrics", "Surgery consultation"],
            "contact": "District Hospital",
        },
    ]
    
    camps = [c for c in camps if c["distance_km"] <= radius_km]
    return camps


def get_nearest_facilities(location: Location, emergency: bool = False) -> List[Dict[str, str]]:
    facilities = [
        {"name": f"{location.taluka} PHC", "type": "Primary Health Centre", "distance_km": f"{random.uniform(3, 15):.1f}", "phone": "104"},
        {"name": f"{location.district} CHC", "type": "Community Health Centre", "distance_km": f"{random.uniform(15, 30):.1f}", "phone": "108"},
        {"name": f"{location.district} District Hospital", "type": "District Hospital", "distance_km": f"{random.uniform(25, 50):.1f}", "phone": "108"},
    ]
    
    if emergency:
        facilities = [{"name": "108 Ambulance", "type": "Emergency", "distance_km": "0", "phone": "108"}] + facilities
    
    return facilities