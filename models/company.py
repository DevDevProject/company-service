from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Company(Base):
    __tablename__ = "company"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    homepage_url = Column(Text)
    industry = Column(String(100))
    region = Column(String(100))
    size = Column(String(50))
    blog_count = Column(Integer)
    recruit_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    detail = relationship("CompanyDetail", back_populates="company", uselist=False)
    stat = relationship("CompanyStat", back_populates="company", uselist=False)


class CompanyDetail(Base):
    __tablename__ = "company_detail"

    company_id = Column(BigInteger, ForeignKey("company.id"), primary_key=True)
    description = Column(Text)
    logo_url = Column(Text)
    contact_email = Column(String(255))
    phone_number = Column(String(50))
    address = Column(String(255))
    representation = Column(String(255))

    company = relationship("Company", back_populates="detail")


class CompanyStat(Base):
    __tablename__ = "company_stat"

    company_id = Column(BigInteger, ForeignKey("company.id"), primary_key=True)
    employee_count = Column(Integer)
    revenue = Column(String(255))
    establishment = Column(DateTime, default=datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = relationship("Company", back_populates="stat")

class BlogUpdateFailLog(Base):
    __tablename__ = "blog_update_fail_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(Integer)
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


BaseB = declarative_base()

class TempCompany(BaseB):
    __tablename__ = "company"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)