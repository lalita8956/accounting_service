from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
import datetime
from app.database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    financial_year = Column(String)

    ledgers = relationship("Ledger", back_populates="company")


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    nature = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"))

    company = relationship("Company")              
    ledgers = relationship("Ledger", back_populates="group")


class Ledger(Base):
    __tablename__ = "ledgers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))
    opening_balance = Column(Float, default=0.0)
    opening_balance_type = Column(String, default="DR")
    
    company = relationship("Company", back_populates="ledgers")
    group = relationship("Group", back_populates="ledgers")
    vouchers = relationship("Voucher", back_populates="ledger")


class Voucher(Base):
    __tablename__ = "vouchers"

    id = Column(Integer, primary_key=True, index=True)
    voucher_type = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow)

    amount = Column(Float, nullable=False)
    dr_cr = Column(String, nullable=False)  

    ledger_id = Column(Integer, ForeignKey("ledgers.id"))
    ledger = relationship("Ledger", back_populates="vouchers")