from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CompanyCreate(BaseModel):
    name: str
    financial_year: str

class CompanyResponse(CompanyCreate):
    id: int
    class Config:
        from_attributes = True
        
class Config:
        from_attributes = True

class GroupCreate(BaseModel):
    name: str
    nature: str
    company_id: int

class GroupResponse(GroupCreate):
    id: int
    class Config:
        from_attributes = True


class LedgerCreate(BaseModel):
    name: str
    company_id: int
    group_id: int
    opening_balance: float = 0
    opening_balance_type: str | None = None

class LedgerResponse(LedgerCreate):
    id: int
    class Config:
        from_attributes = True



class VoucherCreate(BaseModel):
    voucher_type: str
    ledger_id: int
    amount: float
    dr_cr: str

class VoucherResponse(VoucherCreate):
    id: int
    date: datetime
    class Config:
        from_attributes = True