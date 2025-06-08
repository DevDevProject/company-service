from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session, joinedload
from models.company import Base, Company, BaseB, TempCompany, CompanyDetail, CompanyStat
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List, Optional
from schemas.schema import CreateCompany
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from kafka.consumer import consume_blog_recruit_topics
from api.company import router as company_router

from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

SQLALCHEMY_DATABASE_URL = os.environ["DB_URL"]

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def start_kafka_consumer():
    asyncio.create_task(consume_blog_recruit_topics())

app.include_router(company_router, prefix="/api/company")