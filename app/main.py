from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.database import engine, Base, get_db
from app.models import Company, Group, Ledger, Voucher
from app.schemas import (
    CompanyCreate, CompanyResponse,
    GroupCreate, GroupResponse,
    LedgerCreate, LedgerResponse,
    VoucherCreate, VoucherResponse
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Accounting API")


@app.post("/biz/companies", response_model=CompanyResponse)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):      
    db_company = Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

@app.put("/biz/companies/{company_id}", response_model=CompanyResponse)
def update_company(company_id: int, company: CompanyCreate, db: Session = Depends(get_db)):    
    db_company = db.get(Company, company_id)
    if not db_company:
        raise HTTPException(404, "Company not found")

    for key, value in company.dict().items():
        setattr(db_company, key, value)

    db.commit()
    db.refresh(db_company)
    return db_company


@app.get("/biz/companies")
def get_companies(db: Session = Depends(get_db)):
    return db.query(Company).all()

@app.post("/biz/group", response_model=GroupResponse)
def create_group(group: GroupCreate, db: Session = Depends(get_db)):    
    if not db.get(Company, group.company_id):
        raise HTTPException(404, "Company not found")

    db_group = Group(**group.dict())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

@app.get("/biz/group")
def get_group(db: Session = Depends(get_db)):
    return db.query(Group).all()



@app.put("/biz/group/{group_id}", response_model=GroupResponse)
def update_group(group_id: int, group: GroupCreate, db: Session = Depends(get_db)):    
    db_group = db.get(Group, group_id)
    if not db_group:
        raise HTTPException(404, "Group not found")

    for key, value in group.dict().items():
        setattr(db_group, key, value)

    db.commit()
    db.refresh(db_group)
    return db_group



@app.post("/biz/ledger", response_model=LedgerResponse)
def create_ledger(ledger: LedgerCreate, db: Session = Depends(get_db)):
    if not db.get(Company, ledger.company_id):
        raise HTTPException(404, "Company not found")
    if not db.get(Group, ledger.group_id):
        raise HTTPException(404, "Group not found")

    db_ledger = Ledger(**ledger.dict())
    db.add(db_ledger)
    db.commit()
    db.refresh(db_ledger)
    return db_ledger

@app.get("/biz/ledger")
def get_ledger(db: Session = Depends(get_db)):
    return db.query(Ledger).all()


@app.put("/biz/ledger/{ledger_id}", response_model=LedgerResponse)
def update_ledger(ledger_id: int, ledger: LedgerCreate, db: Session = Depends(get_db)):    
    db_ledger = db.get(Ledger, ledger_id)
    if not db_ledger:
        raise HTTPException(404, "Ledger not found")
    for key, value in ledger.dict().items():
        setattr(db_ledger, key, value)  
    db.commit()
    db.refresh(db_ledger)
    return db_ledger




@app.post("/biz/voucher", response_model=VoucherResponse)
def create_voucher(voucher: VoucherCreate, db: Session = Depends(get_db)):
    if not db.get(Ledger, voucher.ledger_id):
        raise HTTPException(404, "Ledger not found")

    db_voucher = Voucher(**voucher.dict())
    db.add(db_voucher)
    db.commit()
    db.refresh(db_voucher)
    return db_voucher

@app.get("/biz/voucher")
def get_voucher(db: Session = Depends(get_db)):
    return db.query(Voucher).all()


@app.put("/biz/voucher/{voucher_id}", response_model=VoucherResponse)
def update_voucher(voucher_id: int, voucher: VoucherCreate, db: Session = Depends(get_db)):    
    db_voucher = db.get(Voucher, voucher_id)
    if not db_voucher:
        raise HTTPException(404, "Voucher not found")   
    for key, value in voucher.dict().items():
        setattr(db_voucher, key, value)  
    db.commit()
    db.refresh(db_voucher)
    return db_voucher


@app.get("/reports/trial-balance")
def trial_balance(db: Session = Depends(get_db)):
    rows = (
        db.query(
            Ledger.name,
            func.sum(
                case(
                    (Voucher.dr_cr == "DR", Voucher.amount),
                    else_=-Voucher.amount
                )
            ).label("balance")
        )
        .join(Voucher)
        .group_by(Ledger.id)
        .all()
    )

    return [{"ledger": r.name, "balance": r.balance} for r in rows]



@app.get("/reports/balance-sheet")
def balance_sheet(db: Session = Depends(get_db)):
    assets = liabilities = capital = 0

    vouchers = db.query(Voucher).join(Ledger).join(Group).all()

    for v in vouchers:
        nature = v.ledger.group.nature
        dc = v.dr_cr

        if nature == "asset":
            assets += v.amount if dc == "dr" else -v.amount

        elif nature == "liability":
            liabilities += v.amount if dc == "cr" else -v.amount

        elif nature == "capital":
            capital += v.amount if dc == "cr" else -v.amount

    return {
        "assets": assets,
        "liabilities": liabilities,
        "capital": capital
    }

@app.get("/reports/daybook")
def daybook(db: Session = Depends(get_db)):
    vouchers = db.query(Voucher).order_by(Voucher.date).all()
    return [
        {
            "date": v.date,
            "ledger": v.ledger.name,
            "voucher_type": v.voucher_type,
            "amount": v.amount,
            "dr_cr": v.dr_cr
        }
        for v in vouchers
    ]
    
