from pydantic import BaseModel
from typing import List

class CreateCompany(BaseModel):
    name: str
    homepage_url: str
    industry: str
    region: str
    size: str
    
class UpdateCompany(BaseModel):
    logo_url: str
    homepage_url: str
    address: str
    revenue: str
    description: str
    employee_count: int
    