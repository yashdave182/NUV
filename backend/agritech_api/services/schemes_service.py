from typing import List, Dict, Any, Optional
from datetime import date, datetime
from ..schemas import (
    SchemeCategory, BeneficiaryType, Location, Language
)


SCHEMES_DB = [
    {
        "scheme_id": "PMKISAN",
        "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "category": SchemeCategory.AGRICULTURE.value,
        "implementing_agency": "Ministry of Agriculture & Farmers Welfare",
        "level": "Central",
        "description": "Income support of ₹6000/year to all landholding farmer families",
        "target_beneficiaries": [BeneficiaryType.FARMER.value],
        "eligibility_criteria": [
            "Landholding farmer family",
            "Cultivable land ownership",
            "Excludes institutional landholders",
            "Excludes higher income category",
        ],
        "benefits": [
            {"type": "Direct cash transfer", "amount": "₹6000/year", "frequency": "3 installments of ₹2000"},
        ],
        "documents_required": [
            {"document_name": "Land records (7/12 extract)", "description": "Proof of land ownership", "mandatory": True},
            {"document_name": "Aadhaar card", "description": "Identity proof", "mandatory": True},
            {"document_name": "Bank passbook", "description": "For DBT", "mandatory": True},
        ],
        "application_process": [
            {"step_number": 1, "title": "Online registration", "description": "Register on pmkisan.gov.in", "channel": "online", "authority": "PM-KISAN portal", "estimated_days": 1, "documents_needed": ["Aadhaar", "Land records", "Bank details"]},
            {"step_number": 2, "title": "State verification", "description": "State government verifies land records", "channel": "offline", "authority": "State nodal officer", "estimated_days": 15, "documents_needed": []},
            {"step_number": 3, "title": "Approval & payment", "description": "Installment credited to bank account", "channel": "online", "authority": "PFMS", "estimated_days": 7, "documents_needed": []},
        ],
        "official_website": "https://pmkisan.gov.in",
        "helpline": "155261 / 1800-115-526",
        "contact_person": "State Nodal Officer",
        "last_updated": date.today().isoformat(),
    },
    {
        "scheme_id": "PMFBY",
        "name": "Pradhan Mantri Fasal Bima Yojana",
        "category": SchemeCategory.AGRICULTURE.value,
        "implementing_agency": "Ministry of Agriculture & Farmers Welfare",
        "level": "Central",
        "description": "Crop insurance scheme providing financial support for crop loss",
        "target_beneficiaries": [BeneficiaryType.FARMER.value, BeneficiaryType.SC_ST.value],
        "eligibility_criteria": [
            "Farmers growing notified crops",
            "Sharecroppers/tenant farmers eligible",
            "Compulsory for loanee farmers",
            "Voluntary for non-loanee farmers",
        ],
        "benefits": [
            {"type": "Insurance coverage", "amount": "Sum insured = Scale of finance", "details": "Premium: 2% Kharif, 1.5% Rabi, 5% commercial/horticulture"},
            {"type": "Claim", "amount": "Based on yield loss", "details": "Area approach / individual assessment"},
        ],
        "documents_required": [
            {"document_name": "Land records", "description": "Proof of cultivation", "mandatory": True},
            {"document_name": "Aadhaar card", "description": "Identity proof", "mandatory": True},
            {"document_name": "Bank passbook", "description": "For claim settlement", "mandatory": True},
            {"document_name": "Sowing certificate", "description": "From village officer", "mandatory": True},
        ],
        "application_process": [
            {"step_number": 1, "title": "Enrollment", "description": "Through bank/CSC/insurance portal", "channel": "both", "authority": "Insurance company", "estimated_days": 1, "documents_needed": ["Land records", "Aadhaar", "Bank details"]},
            {"step_number": 2, "title": "Premium payment", "description": "Farmer share deducted/paid", "channel": "both", "authority": "Bank/CSC", "estimated_days": 1, "documents_needed": []},
            {"step_number": 3, "title": "Claim intimation", "description": "Within 72 hours of loss", "channel": "both", "authority": "Insurance company", "estimated_days": 3, "documents_needed": ["Loss intimation", "Photos"]},
        ],
        "official_website": "https://pmfby.gov.in",
        "helpline": "1800-180-1551",
        "contact_person": "District Agriculture Officer",
        "last_updated": date.today().isoformat(),
    },
    {
        "scheme_id": "SOIL_HEALTH",
        "name": "Soil Health Card Scheme",
        "category": SchemeCategory.AGRICULTURE.value,
        "implementing_agency": "Department of Agriculture, Cooperation & Farmers Welfare",
        "level": "Central",
        "description": "Provides soil health cards with nutrient status and fertilizer recommendations",
        "target_beneficiaries": [BeneficiaryType.FARMER.value],
        "eligibility_criteria": [
            "All farmers",
            "Land ownership/cultivation proof",
        ],
        "benefits": [
            {"type": "Soil testing", "amount": "Free", "frequency": "Every 2 years"},
            {"type": "Recommendations", "amount": "Crop-specific fertilizer advice", "frequency": "Per card"},
        ],
        "documents_required": [
            {"document_name": "Land records", "description": "Proof of land", "mandatory": True},
            {"document_name": "Aadhaar card", "description": "Identity proof", "mandatory": True},
        ],
        "application_process": [
            {"step_number": 1, "title": "Sample collection", "description": "Grid-based soil sampling", "channel": "offline", "authority": "Agriculture department", "estimated_days": 7, "documents_needed": ["Land records"]},
            {"step_number": 2, "title": "Lab testing", "description": "12 parameter analysis", "channel": "offline", "authority": "Soil testing lab", "estimated_days": 30, "documents_needed": []},
            {"step_number": 3, "title": "Card distribution", "description": "Printed/e-card provided", "channel": "both", "authority": "Agriculture department", "estimated_days": 15, "documents_needed": []},
        ],
        "official_website": "https://soilhealth.dac.gov.in",
        "helpline": "1800-180-1551",
        "contact_person": "District Agriculture Officer",
        "last_updated": date.today().isoformat(),
    },
    {
        "scheme_id": "MAHILA_KISAN",
        "name": "Mahila Kisan Sashaktikaran Pariyojana (MKSP)",
        "category": SchemeCategory.AGRICULTURE.value,
        "implementing_agency": "Ministry of Rural Development",
        "level": "Central",
        "description": "Empowers women farmers through sustainable agriculture",
        "target_beneficiaries": [BeneficiaryType.WOMEN.value, BeneficiaryType.FARMER.value],
        "eligibility_criteria": [
            "Women farmers/SHGs",
            "Small/marginal farmers",
            "SC/ST women priority",
        ],
        "benefits": [
            {"type": "Training", "amount": "Capacity building in sustainable agriculture"},
            {"type": "Input support", "amount": "Seeds, bio-inputs, tools"},
            {"type": "Market linkage", "amount": "Collective marketing support"},
        ],
        "documents_required": [
            {"document_name": "SHG registration", "description": "Self Help Group proof", "mandatory": True},
            {"document_name": "Aadhaar card", "description": "Identity proof", "mandatory": True},
            {"document_name": "Land records", "description": "If available", "mandatory": False},
        ],
        "application_process": [
            {"step_number": 1, "title": "SHG formation/identification", "description": "Through NRLM", "channel": "offline", "authority": "Block NRLM", "estimated_days": 30, "documents_needed": []},
            {"step_number": 2, "title": "Project proposal", "description": "Village level planning", "channel": "offline", "authority": "DRDA", "estimated_days": 60, "documents_needed": []},
            {"step_number": 3, "title": "Implementation", "description": "Training and input support", "channel": "offline", "authority": "Implementing agency", "estimated_days": 365, "documents_needed": []},
        ],
        "official_website": "https://nrlm.gov.in",
        "helpline": "1800-110-777",
        "contact_person": "Block Project Manager",
        "last_updated": date.today().isoformat(),
    },
    {
        "scheme_id": "AYUSHMAN",
        "name": "Ayushman Bharat PM-JAY",
        "category": SchemeCategory.HEALTH.value,
        "implementing_agency": "National Health Authority",
        "level": "Central",
        "description": "Health insurance cover of ₹5 lakh per family per year",
        "target_beneficiaries": [
            BeneficiaryType.SC_ST.value,
            BeneficiaryType.LANDLESS_LABOURER.value,
            BeneficiaryType.FARMER.value,
        ],
        "eligibility_criteria": [
            "SECC 2011 deprivation criteria",
            "Rural: D1-D5, D7 categories",
            "Urban: Occupational categories",
            "No age/size limit",
        ],
        "benefits": [
            {"type": "Health cover", "amount": "₹5 lakh/family/year", "details": "Cashless treatment at empanelled hospitals"},
            {"type": "Pre-existing covered", "amount": "From day 1", "details": "All secondary/tertiary care"},
        ],
        "documents_required": [
            {"document_name": "Ration card / SECC data", "description": "Family identification", "mandatory": True},
            {"document_name": "Aadhaar card", "description": "Identity proof", "mandatory": True},
        ],
        "application_process": [
            {"step_number": 1, "title": "Check eligibility", "description": "On pmjay.gov.in or CSC", "channel": "online", "authority": "NHA", "estimated_days": 1, "documents_needed": ["Mobile number"]},
            {"step_number": 2, "title": "e-KYC", "description": "Aadhaar verification at CSC/hospital", "channel": "offline", "authority": "CSC/VLE", "estimated_days": 1, "documents_needed": ["Aadhaar", "Ration card"]},
            {"step_number": 3, "title": "Golden card", "description": "e-card issued for cashless treatment", "channel": "both", "authority": "NHA", "estimated_days": 7, "documents_needed": []},
        ],
        "official_website": "https://pmjay.gov.in",
        "helpline": "14555 / 1800-111-565",
        "contact_person": "District Implementation Unit",
        "last_updated": date.today().isoformat(),
    },
    {
        "scheme_id": "JSY",
        "name": "Janani Suraksha Yojana",
        "category": SchemeCategory.HEALTH.value,
        "implementing_agency": "Ministry of Health & Family Welfare",
        "level": "Central",
        "description": "Cash assistance for institutional delivery",
        "target_beneficiaries": [BeneficiaryType.WOMEN.value, BeneficiaryType.SC_ST.value, BeneficiaryType.FARMER.value],
        "eligibility_criteria": [
            "Pregnant women ≥19 years",
            "BPL families (rural)",
            "All SC/ST women (rural)",
            "Institutional delivery in govt/accredited private",
        ],
        "benefits": [
            {"type": "Cash assistance", "amount": "₹1400 (rural)", "details": "For institutional delivery"},
            {"type": "ASHA incentive", "amount": "₹600", "details": "For facilitating delivery"},
        ],
        "documents_required": [
            {"document_name": "MCP card", "description": "Mother Child Protection card", "mandatory": True},
            {"document_name": "BPL card/SC-ST certificate", "description": "Eligibility proof", "mandatory": True},
            {"document_name": "Aadhaar card", "description": "Identity proof", "mandatory": True},
            {"document_name": "Bank passbook", "description": "For DBT", "mandatory": True},
        ],
        "application_process": [
            {"step_number": 1, "title": "ANC registration", "description": "Early pregnancy registration", "channel": "offline", "authority": "ANM/ASHA", "estimated_days": 1, "documents_needed": []},
            {"step_number": 2, "title": "Institutional delivery", "description": "At govt/accredited facility", "channel": "offline", "authority": "Hospital", "estimated_days": 1, "documents_needed": ["MCP card", "ID proof"]},
            {"step_number": 3, "title": "Claim submission", "description": "ASHA submits claim", "channel": "offline", "authority": "Block PHC", "estimated_days": 15, "documents_needed": ["Discharge summary", "Bank details"]},
        ],
        "official_website": "https://nhm.gov.in",
        "helpline": "104 / 1800-180-1900",
        "contact_person": "Block Medical Officer",
        "last_updated": date.today().isoformat(),
    },
    {
        "scheme_id": "PMJDY",
        "name": "Pradhan Mantri Jan Dhan Yojana",
        "category": SchemeCategory.SOCIAL_SECURITY.value,
        "implementing_agency": "Department of Financial Services",
        "level": "Central",
        "description": "Financial inclusion - zero balance bank accounts",
        "target_beneficiaries": [BeneficiaryType.GENERAL.value, BeneficiaryType.FARMER.value, BeneficiaryType.WOMEN.value],
        "eligibility_criteria": [
            "Indian citizen ≥10 years",
            "No existing bank account",
        ],
        "benefits": [
            {"type": "Bank account", "amount": "Zero balance", "details": "RuPay debit card, ₹2 lakh accident insurance"},
            {"type": "Overdraft", "amount": "Up to ₹10,000", "details": "After 6 months satisfactory operation"},
        ],
        "documents_required": [
            {"document_name": "Aadhaar card", "description": "Identity & address proof", "mandatory": True},
            {"document_name": "PAN card", "description": "If available", "mandatory": False},
            {"document_name": "Passport size photo", "description": "2 copies", "mandatory": True},
        ],
        "application_process": [
            {"step_number": 1, "title": "Visit bank/CSC", "description": "Any bank branch or CSC", "channel": "offline", "authority": "Bank/CSC", "estimated_days": 1, "documents_needed": ["Aadhaar", "Photo"]},
            {"step_number": 2, "title": "Form filling", "description": "PMJDY account opening form", "channel": "offline", "authority": "Bank", "estimated_days": 1, "documents_needed": []},
            {"step_number": 3, "title": "Account activation", "description": "Receive RuPay card & passbook", "channel": "offline", "authority": "Bank", "estimated_days": 7, "documents_needed": []},
        ],
        "official_website": "https://pmjdy.gov.in",
        "helpline": "1800-110-001 / 1800-180-1111",
        "contact_person": "Bank Manager",
        "last_updated": date.today().isoformat(),
    },
    {
        "scheme_id": "KISAN_CREDIT",
        "name": "Kisan Credit Card (KCC)",
        "category": SchemeCategory.AGRICULTURE.value,
        "implementing_agency": "Department of Agriculture & Farmers Welfare",
        "level": "Central",
        "description": "Credit card for farmers for crop production needs",
        "target_beneficiaries": [BeneficiaryType.FARMER.value],
        "eligibility_criteria": [
            "Individual/joint cultivators",
            "Sharecroppers/tenant farmers",
            "SHGs/JLGs of farmers",
            "Age 18-75 years",
        ],
        "benefits": [
            {"type": "Credit limit", "amount": "Based on cropping pattern", "details": "Flexible withdrawal, 4% interest with subvention"},
            {"type": "Insurance", "amount": "Crop + Personal accident", "details": "Built-in coverage"},
        ],
        "documents_required": [
            {"document_name": "Land records", "description": "Proof of cultivation", "mandatory": True},
            {"document_name": "Aadhaar card", "description": "Identity proof", "mandatory": True},
            {"document_name": "PAN card", "description": "For limit >₹50,000", "mandatory": False},
            {"document_name": "Passport photo", "description": "2 copies", "mandatory": True},
        ],
        "application_process": [
            {"step_number": 1, "title": "Apply at bank", "description": "Commercial/RRB/Cooperative bank", "channel": "offline", "authority": "Bank branch", "estimated_days": 1, "documents_needed": ["Land records", "Aadhaar", "Photo"]},
            {"step_number": 2, "title": "Verification", "description": "Field verification by bank", "channel": "offline", "authority": "Bank officer", "estimated_days": 15, "documents_needed": []},
            {"step_number": 3, "title": "Card issuance", "description": "KCC card with passbook", "channel": "offline", "authority": "Bank", "estimated_days": 7, "documents_needed": []},
        ],
        "official_website": "https://www.agricoop.nic.in",
        "helpline": "1800-180-1551",
        "contact_person": "Lead Bank Manager",
        "last_updated": date.today().isoformat(),
    },
    {
        "scheme_id": "LIVESTOCK_INSURANCE",
        "name": "Livestock Insurance Scheme",
        "category": SchemeCategory.LIVESTOCK.value,
        "implementing_agency": "Department of Animal Husbandry & Dairying",
        "level": "Central",
        "description": "Insurance for milch animals against death",
        "target_beneficiaries": [BeneficiaryType.FARMER.value, BeneficiaryType.WOMEN.value, BeneficiaryType.SC_ST.value],
        "eligibility_criteria": [
            "Milch cattle/buffalo",
            "Indigenous/crossbred",
            "Maximum 2 animals per beneficiary",
            "Subsidy: 50% (General), 70% (SC/ST/BPL)",
        ],
        "benefits": [
            {"type": "Insurance cover", "amount": "Market value of animal", "details": "Premium subsidized"},
            {"type": "Claim", "amount": "Sum insured on death", "details": "Post-mortem required"},
        ],
        "documents_required": [
            {"document_name": "Animal identification", "description": "Ear tag/photo", "mandatory": True},
            {"document_name": "Health certificate", "description": "From veterinarian", "mandatory": True},
            {"document_name": "Aadhaar card", "description": "Identity proof", "mandatory": True},
            {"document_name": "Bank passbook", "description": "For premium/claim", "mandatory": True},
        ],
        "application_process": [
            {"step_number": 1, "title": "Animal valuation", "description": "By veterinarian", "channel": "offline", "authority": "Veterinary officer", "estimated_days": 3, "documents_needed": ["Health certificate"]},
            {"step_number": 2, "title": "Proposal submission", "description": "Through bank/insurance agent", "channel": "offline", "authority": "Insurance company", "estimated_days": 7, "documents_needed": ["Valuation", "Aadhaar", "Bank details"]},
            {"step_number": 3, "title": "Premium payment", "description": "Beneficiary share only", "channel": "offline", "authority": "Bank/Insurance", "estimated_days": 1, "documents_needed": []},
        ],
        "official_website": "https://dahd.nic.in",
        "helpline": "1800-180-1551",
        "contact_person": "District Animal Husbandry Officer",
        "last_updated": date.today().isoformat(),
    },
    {
        "scheme_id": "NATIONAL_LIVESTOCK_MISSION",
        "name": "National Livestock Mission (NLM)",
        "category": SchemeCategory.LIVESTOCK.value,
        "implementing_agency": "Department of Animal Husbandry & Dairying",
        "level": "Central",
        "description": "Comprehensive livestock development programme",
        "target_beneficiaries": [BeneficiaryType.FARMER.value, BeneficiaryType.WOMEN.value, BeneficiaryType.SC_ST.value],
        "eligibility_criteria": [
            "Farmers/entrepreneurs/SHGs",
            "For breed improvement, feed/fodder, skill development",
            "State-specific components",
        ],
        "benefits": [
            {"type": "Subsidy", "amount": "25-50%", "details": "For breed improvement, poultry, piggery, feed units"},
            {"type": "Training", "amount": "Free", "details": "Skill development in livestock management"},
        ],
        "documents_required": [
            {"document_name": "Project proposal", "description": "Detailed business plan", "mandatory": True},
            {"document_name": "Land documents", "description": "Ownership/lease", "mandatory": True},
            {"document_name": "Aadhaar/PAN", "description": "Identity proof", "mandatory": True},
        ],
        "application_process": [
            {"step_number": 1, "title": "Project preparation", "description": "With veterinary officer help", "channel": "offline", "authority": "Applicant", "estimated_days": 30, "documents_needed": []},
            {"step_number": 2, "title": "Submission to state", "description": "Through District AH Officer", "channel": "offline", "authority": "State Implementing Agency", "estimated_days": 60, "documents_needed": ["Project report", "Land docs", "ID proofs"]},
            {"step_number": 3, "title": "Approval & sanction", "description": "State level committee", "channel": "offline", "authority": "SIA/SLEC", "estimated_days": 90, "documents_needed": []},
        ],
        "official_website": "https://nlm.udyamimitra.in",
        "helpline": "1800-180-1551",
        "contact_person": "District Animal Husbandry Officer",
        "last_updated": date.today().isoformat(),
    },
    {
        "scheme_id": "ICDS",
        "name": "Integrated Child Development Services (ICDS)",
        "category": SchemeCategory.HEALTH.value,
        "implementing_agency": "Ministry of Women & Child Development",
        "level": "Central",
        "description": "Supplementary nutrition, health checkups, preschool education",
        "target_beneficiaries": [BeneficiaryType.CHILD.value, BeneficiaryType.WOMEN.value],
        "eligibility_criteria": [
            "Children 0-6 years",
            "Pregnant/lactating women",
            "Adolescent girls (11-18 years) - SAG",
        ],
        "benefits": [
            {"type": "Supplementary nutrition", "amount": "Daily at AWC", "details": "Take-home ration for pregnant/lactating"},
            {"type": "Health services", "amount": "Free", "details": "Immunization, health checkup, referral"},
            {"type": "Pre-school education", "amount": "Free", "details": "3-6 years at AWC"},
        ],
        "documents_required": [
            {"document_name": "Birth certificate", "description": "Child age proof", "mandatory": True},
            {"document_name": "MCP card", "description": "For pregnant/lactating", "mandatory": True},
            {"document_name": "Aadhaar", "description": "Identity proof", "mandatory": False},
        ],
        "application_process": [
            {"step_number": 1, "title": "Register at AWC", "description": "Nearest Anganwadi Centre", "channel": "offline", "authority": "AWW/AWH", "estimated_days": 1, "documents_needed": ["Birth certificate", "MCP card"]},
            {"step_number": 2, "title": "Avail services", "description": "Regular visits to AWC", "channel": "offline", "authority": "AWW", "estimated_days": "Ongoing", "documents_needed": []},
        ],
        "official_website": "https://icds-wcd.nic.in",
        "helpline": "1800-111-4545",
        "contact_person": "CDPO / District Program Officer",
        "last_updated": date.today().isoformat(),
    },
    {
        "scheme_id": "PM_MATRU_VANDANA",
        "name": "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
        "category": SchemeCategory.HEALTH.value,
        "implementing_agency": "Ministry of Women & Child Development",
        "level": "Central",
        "description": "Maternity benefit for first living child",
        "target_beneficiaries": [BeneficiaryType.WOMEN.value],
        "eligibility_criteria": [
            "Pregnant women ≥19 years",
            "First live birth",
            "Not in regular govt employment",
            "Not receiving similar benefits",
        ],
        "benefits": [
            {"type": "Cash incentive", "amount": "₹5000", "details": "3 installments: ₹1000, ₹2000, ₹2000"},
        ],
        "documents_required": [
            {"document_name": "MCP card", "description": "Mother Child Protection card", "mandatory": True},
            {"document_name": "Aadhaar card", "description": "Identity proof", "mandatory": True},
            {"document_name": "Bank passbook", "description": "For DBT", "mandatory": True},
            {"document_name": "Pregnancy registration proof", "description": "ANC registration", "mandatory": True},
        ],
        "application_process": [
            {"step_number": 1, "title": "Registration", "description": "At AWC/health facility within 150 days LMP", "channel": "offline", "authority": "AWW/ANM", "estimated_days": 1, "documents_needed": ["MCP card", "Aadhaar"]},
            {"step_number": 2, "title": "Installments", "description": "On meeting conditions", "channel": "offline", "authority": "CDPO", "estimated_days": "Per condition", "documents_needed": ["ANC proof", "Delivery proof", "Immunization proof"]},
        ],
        "official_website": "https://pmmvy.wcd.gov.in",
        "helpline": "1800-111-4545",
        "contact_person": "CDPO",
        "last_updated": date.today().isoformat(),
    },
    {
        "scheme_id": "SUKANYA_SAMRIDDHI",
        "name": "Sukanya Samriddhi Yojana",
        "category": SchemeCategory.SOCIAL_SECURITY.value,
        "implementing_agency": "Department of Economic Affairs",
        "level": "Central",
        "description": "Savings scheme for girl child education/marriage",
        "target_beneficiaries": [BeneficiaryType.CHILD.value, BeneficiaryType.WOMEN.value],
        "eligibility_criteria": [
            "Girl child <10 years",
            "Maximum 2 accounts per family",
            "Minimum ₹250, maximum ₹1.5 lakh/year",
        ],
        "benefits": [
            {"type": "Savings", "amount": "7.6% interest (Q2 FY25)", "details": "Tax free, matures at 21 years"},
        ],
        "documents_required": [
            {"document_name": "Birth certificate", "description": "Girl child age proof", "mandatory": True},
            {"document_name": "Parent Aadhaar/PAN", "description": "Guardian identity", "mandatory": True},
            {"document_name": "Address proof", "description": "Guardian residence", "mandatory": True},
        ],
        "application_process": [
            {"step_number": 1, "title": "Open account", "description": "Post office / authorized bank", "channel": "offline", "authority": "Post office/Bank", "estimated_days": 1, "documents_needed": ["Birth cert", "Parent ID", "Address proof", "₹250 deposit"]},
        ],
        "official_website": "https://www.nsiindia.gov.in",
        "helpline": "1800-266-6868",
        "contact_person": "Post Master / Bank Manager",
        "last_updated": date.today().isoformat(),
    },
]


def search_schemes(
    category: Optional[SchemeCategory] = None,
    beneficiary_type: Optional[BeneficiaryType] = None,
    keywords: Optional[List[str]] = None,
    location: Optional[Location] = None,
    profile: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    results = []
    
    for scheme in SCHEMES_DB:
        score = 0
        matched = []
        
        if category and scheme["category"] == category.value:
            score += 10
            matched.append(f"Category: {category.value}")
        
        if beneficiary_type:
            if beneficiary_type.value in scheme["target_beneficiaries"]:
                score += 10
                matched.append(f"Beneficiary: {beneficiary_type.value}")
        
        if keywords:
            search_text = " ".join([
                scheme["name"],
                scheme["description"],
                " ".join(scheme["eligibility_criteria"]),
                " ".join([b.get("type", "") for b in scheme["benefits"]]),
            ]).lower()
            for kw in keywords:
                if kw.lower() in search_text:
                    score += 5
                    matched.append(f"Keyword: {kw}")
        
        if profile:
            if profile.get("gender") == "female" and BeneficiaryType.WOMEN.value in scheme["target_beneficiaries"]:
                score += 5
            if profile.get("caste_category") in ["SC", "ST"] and BeneficiaryType.SC_ST.value in scheme["target_beneficiaries"]:
                score += 5
            if profile.get("annual_income", 999999) < 200000 and BeneficiaryType.LANDLESS_LABOURER.value in scheme["target_beneficiaries"]:
                score += 5
            if profile.get("land_holding_hectares", 10) < 2 and BeneficiaryType.FARMER.value in scheme["target_beneficiaries"]:
                score += 5
        
        if score > 0:
            results.append({
                **scheme,
                "match_score": score,
                "matched_criteria": matched,
            })
    
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results


def get_scheme_detail(scheme_id: str) -> Optional[Dict[str, Any]]:
    for scheme in SCHEMES_DB:
        if scheme["scheme_id"] == scheme_id:
            return scheme
    return None


def check_eligibility(scheme_id: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    scheme = get_scheme_detail(scheme_id)
    if not scheme:
        return {"is_eligible": False, "reason": "Scheme not found"}
    
    met = []
    unmet = []
    missing_docs = []
    
    for criterion in scheme["eligibility_criteria"]:
        criterion_lower = criterion.lower()
        
        if "landholding" in criterion_lower or "cultivable" in criterion_lower:
            if profile.get("land_holding_hectares", 0) > 0:
                met.append(criterion)
            else:
                unmet.append(criterion)
                missing_docs.append("Land records (7/12 extract)")
        
        elif "women" in criterion_lower or "female" in criterion_lower:
            if profile.get("gender") == "female":
                met.append(criterion)
            else:
                unmet.append(criterion)
        
        elif "sc/st" in criterion_lower or "sc-st" in criterion_lower:
            if profile.get("caste_category") in ["SC", "ST"]:
                met.append(criterion)
            else:
                unmet.append(criterion)
        
        elif "bpl" in criterion_lower or "income" in criterion_lower:
            if profile.get("annual_income", 999999) < 200000:
                met.append(criterion)
            else:
                unmet.append(criterion)
                missing_docs.append("BPL card / Income certificate")
        
        elif "age" in criterion_lower:
            age = profile.get("age", 0)
            if "19" in criterion and age >= 19:
                met.append(criterion)
            elif "10" in criterion and age < 10:
                met.append(criterion)
            elif "18" in criterion and age >= 18:
                met.append(criterion)
            else:
                unmet.append(criterion)
        
        elif "pregnant" in criterion_lower:
            if profile.get("pregnant"):
                met.append(criterion)
            else:
                unmet.append(criterion)
        
        elif "first live birth" in criterion_lower:
            if profile.get("children_count", 1) == 0:
                met.append(criterion)
            else:
                unmet.append(criterion)
        
        elif "employment" in criterion_lower:
            if not profile.get("govt_employee", False):
                met.append(criterion)
            else:
                unmet.append(criterion)
        
        else:
            met.append(criterion)
    
    for doc in scheme["documents_required"]:
        if doc["mandatory"]:
            doc_name = doc["document_name"].lower()
            if "aadhaar" in doc_name and not profile.get("has_aadhaar", True):
                missing_docs.append(doc["document_name"])
            elif "land" in doc_name and profile.get("land_holding_hectares", 0) <= 0:
                missing_docs.append(doc["document_name"])
            elif "bank" in doc_name and not profile.get("has_bank_account", True):
                missing_docs.append(doc["document_name"])
            elif "mcp" in doc_name and not profile.get("has_mcp_card", False):
                missing_docs.append(doc["document_name"])
            elif "birth" in doc_name and not profile.get("has_birth_certificate", False):
                missing_docs.append(doc["document_name"])
    
    missing_docs = list(set(missing_docs))
    
    eligible = len(unmet) == 0
    score = (len(met) / (len(met) + len(unmet))) * 100 if (met or unmet) else 50
    
    benefit_estimate = ""
    for benefit in scheme["benefits"]:
        if "amount" in benefit:
            benefit_estimate = benefit["amount"]
            break
    
    next_steps = []
    if not eligible:
        next_steps.append("Review unmet eligibility criteria")
        if missing_docs:
            next_steps.append(f"Obtain missing documents: {', '.join(missing_docs)}")
    else:
        next_steps.append("Eligible! Proceed to application")
        next_steps.append("Visit official website or nearest CSC")
        next_steps.append("Prepare all required documents")
    
    return {
        "scheme_id": scheme_id,
        "scheme_name": scheme["name"],
        "is_eligible": eligible,
        "eligibility_score": round(score, 1),
        "met_criteria": met,
        "unmet_criteria": unmet,
        "missing_documents": missing_docs,
        "estimated_benefit": benefit_estimate,
        "next_steps": next_steps,
    }