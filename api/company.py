from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from db.session import get_db
from models.company import Company, CompanyDetail, CompanyStat
from schemas.schema import CreateCompany
from typing import List, Optional

router = APIRouter()

@router.post("/companies")
def create_companies(
    companies: List[CreateCompany],
    db: Session = Depends(get_db)
):
    result = []
    
    for company in companies:
        existing = db.query(Company).filter(Company.name == company.name).first()
        
        if existing:
            existing.homepage_url = company.homepage_url
            existing.industry = company.industry
            existing.region = company.region
            existing.size = company.size
        else:
            new_company = Company(
                name=company.name,
                homepage_url=company.homepage_url,
                industry=company.industry,
                region=company.region,
                size=company.size,
            )
            db.add(new_company)
            result.append(new_company)
    
    db.commit()
    return {"status": "ok", "processed": len(companies)}

@router.get("/companies")
def get_company_names(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=2000),
    fields: Optional[str] = Query(None, description = "name, industry"),
    search: Optional[str] = Query(None, description="company name %like%"),
    db: Session = Depends(get_db)
):
    query = db.query(Company).options(
        joinedload(Company.detail),
        joinedload(Company.stat)
    )
    
    if search:
        query = query.filter(Company.name.ilike(f"%{search}%"))
    
    total = query.count()
    companies = query.offset((page - 1) * page_size).limit(page_size).all()
    
    field_list = fields.split(",") if fields else None
    
    field_map = {
        "id": lambda c: c.id,
        "name": lambda c: c.name,
        "homepage_url": lambda c: c.homepage_url,
        "industry": lambda c: c.industry,
        "region": lambda c: c.region,
        "size": lambda c: c.size,
        "description": lambda c: c.detail.description if c.detail else None,
        "logo_url": lambda c: c.detail.logo_url if c.detail else None,
        "address": lambda c: c.detail.address if c.detail else None,
        "representation": lambda c: c.detail.representation if c.detail else None,
        "employee_count": lambda c: c.stat.employee_count if c.stat else None,
        "blog_count": lambda c: c.blog_count if c else None,
        "recruit_count": lambda c: c.recruit_count if c else None,
        "revenue": lambda c: c.stat.revenue if c.stat else None,
        "establishment": lambda c: c.stat.establishment.strftime("%Y-%m-%d") if c.stat and c.stat.establishment else None
    }
    
    result = []
    for company in companies:
        if field_list:
            result.append({
                field: field_map[field](company)
                for field in field_list if field in field_map
            })
        else:
            # 필드 미지정 시 기본 전체 반환
            result.append({
                k: f(company) for k, f in field_map.items()
            })

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "companies": result
    }
    
@router.post("/update/companies")
def update_company_info(
    data: List[dict],
    db: Session = Depends(get_db)
):
    success_count = 0
    fail_list = []
    for item in data:
        try:
            company = db.query(Company).filter(Company.name == item.get("name")).first()

            if not company:
                fail_list.append({"name": item.get("name"), "error": "회사 없음"})
                continue
            
            # 기존 company 정보 업데이트
            company.homepage_url = item.get("homepage_url")
            company.industry = item.get("industry")
            company.region = item.get("region")
            company.size = item.get("size")
            db.commit()

            # 연관된 CompanyStat 추가
            stat = CompanyStat(
                revenue=item.get("revenue"),
                employee_count=item.get("employee_count"),
                establishment=item.get("establishment"),
                company_id=company.id
            )
            db.add(stat)

            # 연관된 CompanyDetail 추가
            detail = CompanyDetail(
                description=item.get("description"),
                logo_url=item.get("logo_url"),
                address=item.get("address"),
                representation=item.get("representation"),
                company_id=company.id
            )
            db.add(detail)
            db.commit()
            
            success_count += 1

        except Exception as e:
            db.rollback()  # 실패 시 롤백
            fail_list.append({"name": item.get("name"), "error": str(e)})

    db.commit()  # 전체 처리 후 한 번에 커밋

    return {
        "message": f"{success_count}개 성공, {len(fail_list)}개 실패",
        "failures": fail_list
    }
    
@router.get("/companies/single")
def get_single_company(
    name: str = Query(..., description="정확한 회사 이름"),
    fields: Optional[str] = Query(None, description="예: name,logo_url"),
    db: Session = Depends(get_db)
):
    company = db.query(Company).options(
        joinedload(Company.detail),
        joinedload(Company.stat)
    ).filter(Company.name == name).first()

    # if not company:
    #     raise HTTPException(status_code=404, detail="Company not found")

    field_list = fields.split(",") if fields else None

    field_map = {
        "id": lambda c: c.id,
        "name": lambda c: c.name,
        "homepage_url": lambda c: c.homepage_url,
        "industry": lambda c: c.industry,
        "region": lambda c: c.region,
        "size": lambda c: c.size,
        "description": lambda c: c.detail.description if c.detail else None,
        "logo_url": lambda c: c.detail.logo_url if c.detail else None,
        "address": lambda c: c.detail.address if c.detail else None,
        "representation": lambda c: c.detail.representation if c.detail else None,
        "employee_count": lambda c: c.stat.employee_count if c.stat else None,
        "blog_count": lambda c: c.blog_count if c else None,
        "recruit_count": lambda c: c.recruit_count if c else None,
        "revenue": lambda c: c.stat.revenue if c.stat else None,
        "establishment": lambda c: c.stat.establishment.strftime("%Y-%m-%d") if c.stat and c.stat.establishment else None
    }

    if field_list:
        return {
            field: field_map[field](company)
            for field in field_list if field in field_map
        }
    else:
        return {k: f(company) for k, f in field_map.items()}