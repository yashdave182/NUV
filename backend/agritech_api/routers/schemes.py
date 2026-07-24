from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, date, timedelta
import uuid

from agritech_api.schemas import (
    SchemeQueryRequest, SchemeQueryResponse, SchemeSummary,
    SchemeDetailRequest, SchemeDetailResponse, DocumentRequirement,
    ApplicationStep, ApplicationTrackerRequest, ApplicationTrackerResponse,
    ApplicationStatus, EligibilityCheckRequest, EligibilityCheckResponse,
    EligibilityResult, SchemeCategory, BeneficiaryType, Language, Location,
)
from agritech_api.services.schemes_service import search_schemes, get_scheme_detail as service_get_scheme_detail, check_eligibility
from agritech_api.utils.cache import async_ttl_cache

router = APIRouter(prefix="/schemes", tags=["Government Schemes"])


def _benefit_str(benefits) -> str:
    """Safely extract a benefit summary string from dict or list."""
    if not benefits:
        return "See details"
    if isinstance(benefits, dict):
        # benefits is a single dict
        return benefits.get("type", "Benefit") + ": " + str(benefits.get("amount", ""))
    if isinstance(benefits, list) and len(benefits) > 0:
        b = benefits[0]
        if isinstance(b, dict):
            return b.get("type", "Benefit") + ": " + str(b.get("amount", ""))
        return str(b)
    return "See details"


@router.post("/search", response_model=SchemeQueryResponse)
@async_ttl_cache(ttl_seconds=300)
async def search_schemes_endpoint(request: SchemeQueryRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        results = search_schemes(
            category=request.category,
            beneficiary_type=request.beneficiary_type,
            keywords=request.keywords,
            location=request.location,
            profile={
                "age": request.age,
                "gender": request.gender,
                "annual_income": request.annual_income,
                "land_holding_hectares": request.land_holding_hectares,
                "caste_category": request.caste_category,
            } if any([request.age, request.gender, request.annual_income, 
                      request.land_holding_hectares, request.caste_category]) else None,
        )
        
        schemes = []
        for r in results[:10]:
            schemes.append(SchemeSummary(
                scheme_id=r["scheme_id"],
                name=r["name"],
                category=SchemeCategory(r["category"]),
                implementing_agency=r["implementing_agency"],
                level=r["level"],
                benefit_summary=_benefit_str(r.get("benefits", [])),
                eligibility_summary="; ".join((r.get("eligibility_criteria") or [])[:3]),
            ))
        
        sms = f"Found {len(schemes)} schemes. Top: {', '.join([s.name[:20] for s in schemes[:3]])}. Reply with scheme ID for details."
        
        return SchemeQueryResponse(
            request_id=request_id,
            phone=request.phone,
            matched_schemes=schemes,
            total_count=len(results),
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
            detailed_report_id=f"rpt_sch_{request_id}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detail", response_model=SchemeDetailResponse)
@async_ttl_cache(ttl_seconds=600)
async def get_scheme_detail(request: SchemeDetailRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        scheme = service_get_scheme_detail(request.scheme_id)
        if not scheme:
            raise HTTPException(status_code=404, detail="Scheme not found")
        
        documents = []
        for doc in scheme["documents_required"]:
            documents.append(DocumentRequirement(
                document_name=doc["document_name"],
                description=doc["description"],
                mandatory=doc["mandatory"],
                alternatives=doc.get("alternatives", []),
            ))
        
        steps = []
        for step in scheme["application_process"]:
            steps.append(ApplicationStep(
                step_number=step["step_number"],
                title=step["title"],
                description=step["description"],
                channel=step["channel"],
                authority=step["authority"],
                estimated_days=step["estimated_days"],
                documents_needed=step["documents_needed"],
            ))
        
        sms = f"{scheme['name']}: {scheme['benefits'][0]['type'] if scheme['benefits'] else 'Benefits'}. Apply: {scheme['application_process'][0]['title']}. Helpline: {scheme.get('helpline', 'N/A')}"
        
        return SchemeDetailResponse(
            request_id=request_id,
            phone=request.phone,
            scheme_id=scheme["scheme_id"],
            name=scheme["name"],
            category=SchemeCategory(scheme["category"]),
            description=scheme["description"],
            implementing_agency=scheme["implementing_agency"],
            level=scheme["level"],
            target_beneficiaries=[BeneficiaryType(b) for b in scheme["target_beneficiaries"]],
            eligibility_criteria=scheme["eligibility_criteria"],
            benefits=scheme["benefits"],
            documents_required=documents,
            application_process=steps,
            official_website=scheme.get("official_website"),
            helpline=scheme.get("helpline"),
            contact_person=scheme.get("contact_person"),
            last_updated=date.fromisoformat(scheme["last_updated"]) if isinstance(scheme["last_updated"], str) else scheme["last_updated"],
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
            detailed_report_id=f"rpt_det_{request_id}",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/track", response_model=ApplicationTrackerResponse)
async def track_application(request: ApplicationTrackerRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        application = ApplicationStatus(
            application_id=request.application_id,
            scheme_name="PM-KISAN",
            status="under_review",
            current_stage="State verification",
            submitted_date=date.today() - timedelta(days=15),
            last_updated=date.today(),
            expected_completion=date.today() + timedelta(days=30),
            remarks="Documents verified, pending state approval",
            documents_pending=[],
        )
        
        sms = f"Application {request.application_id}: {application.status.replace('_', ' ').title()}. Stage: {application.current_stage}. Expected: {application.expected_completion}."
        
        return ApplicationTrackerResponse(
            request_id=request_id,
            phone=request.phone,
            application=application,
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/eligibility", response_model=EligibilityCheckResponse)
async def check_scheme_eligibility(request: EligibilityCheckRequest):
    try:
        request_id = str(uuid.uuid4())[:8]
        
        scheme_id = request.scheme_id or "PMKISAN"
        profile = request.profile or {
            "crop_type": request.crop_type,
            "land_holding_hectares": request.land_holding_hectares,
        }
        result = check_eligibility(scheme_id, profile)
        
        sms = f"Eligibility for {result['scheme_name']}: {'✅ ELIGIBLE' if result['is_eligible'] else '❌ NOT ELIGIBLE'} (Score: {result['eligibility_score']}%). {'; '.join(result['unmet_criteria'][:2]) if result['unmet_criteria'] else 'All criteria met'}."
        
        return EligibilityCheckResponse(
            request_id=request_id,
            phone=request.phone,
            result=EligibilityResult(
                scheme_id=result["scheme_id"],
                scheme_name=result["scheme_name"],
                is_eligible=result["is_eligible"],
                eligibility_score=result["eligibility_score"],
                met_criteria=result["met_criteria"],
                unmet_criteria=result["unmet_criteria"],
                missing_documents=result["missing_documents"],
                estimated_benefit=result["estimated_benefit"],
                next_steps=result["next_steps"],
            ),
            language=request.language,
            generated_at=datetime.utcnow(),
            sms_summary=sms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))