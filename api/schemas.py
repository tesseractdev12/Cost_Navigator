from pydantic import BaseModel
from typing import Optional

class DRGOut(BaseModel):
    id: str
    description: str

class ProviderOut(BaseModel):
    id: str
    name: str
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    star_rating: Optional[int]
    drgs: list[DRGOut] = []
    avg_covered_charges: Optional[float]
    avg_total_payments: Optional[float]
    avg_medicare_payments: Optional[float]
    total_discharges: Optional[int]

    class Config:
        orm_mode = True 