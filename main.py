from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from models.company import Base, Company, BaseB, TempCompany, CompanyDetail, CompanyStat
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List
from schemas.schema import CreateCompany


# A DB 연결
# engine_a = create_engine("mysql+pymysql://root:123456@localhost:3306/company")
# SessionA = sessionmaker(bind=engine_a)

# # B DB 연결
# engine_b = create_engine("mysql+pymysql://root:123456@localhost:3306/blog")
# SessionB = sessionmaker(bind=engine_b)

# A to B

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/company"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, echo=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

# with SessionA() as session_a, SessionB() as session_b:
#     companies = session_a.query(Company).all()
#     for c in companies:
#         session_b.add(TempCompany(
#                 id=c.id, 
#                 name=c.name,
#             ))
#     session_b.commit()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/companies")
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

@app.get("/companies")
def get_company_names(db: Session = Depends(get_db)):
    names = db.query(Company.name).all()
    
    return [name[0] for name in names]
    
@app.post("/update/companies")
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


@app.get("/")
def read_root():
    return {"message": "Company API is running!"}
