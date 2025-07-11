from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from fastapi import APIRouter, Depends
from typing import List
import redis
from models.company import Company, CompanyDetail
from db.session import get_db
import os
from dotenv import load_dotenv
load_dotenv()

REDIS_URL = os.getenv("REDIS_SERVER")
REDIS_PORT = os.getenv("REDIS_PORT")

redis_client = redis.Redis(host=REDIS_URL, port=REDIS_PORT, decode_responses=True)

def increase_company_score(company_id: int):
    redis_client.zincrby("popular:company", 1, str(company_id))
    
def get_popular_company_ids(limit: int = 10) -> List[int]:
    ids = redis_client.zrevrange("popular:company", 0, limit - 1)
    return [int(i) for i in ids]

def get_popular_companies(db: Session, ids: List[int]) -> List[Company]:
    if not ids:
        return []

    companies = (
        db.query(Company)
        .join(Company.detail)
        .filter(Company.id.in_(ids))
        .all()
    )

    id_to_company = {c.id: c for c in companies}
    return [id_to_company[i] for i in ids if i in id_to_company]

router = APIRouter()

@router.get("/popular")
def popular_companies(db: Session = Depends(get_db)):
    popular_ids = get_popular_company_ids()
    companies = get_popular_companies(db, popular_ids)

    return [
        {
            "id": c.id,
            "name": c.name,
            "logo_url": c.detail.logo_url if c.detail else None,
        }
        for c in companies
    ]
