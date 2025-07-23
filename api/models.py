from sqlalchemy import Column, Integer, String, Float, ForeignKey, Index
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base(cls=AsyncAttrs)

class Provider(Base):
    __tablename__ = 'providers'
    id = Column(String, primary_key=True)  # Rndrng_Prvdr_CCN
    name = Column(String, nullable=False)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String, index=True)
    state_fips = Column(String)
    ruca_code = Column(String)
    ruca_desc = Column(String)
    star_rating = Column(Integer)  # 1-10
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    drg_stats = relationship('ProviderDRGStat', back_populates='provider')

class DRG(Base):
    __tablename__ = 'drgs'
    id = Column(String, primary_key=True)  # DRG_Cd
    description = Column(String, index=True)
    drg_stats = relationship('ProviderDRGStat', back_populates='drg')

class ProviderDRGStat(Base):
    __tablename__ = 'provider_drg_stats'
    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(String, ForeignKey('providers.id'), nullable=False)
    drg_id = Column(String, ForeignKey('drgs.id'), nullable=False)
    total_discharges = Column(Integer)
    avg_covered_charges = Column(Float)
    avg_total_payments = Column(Float)
    avg_medicare_payments = Column(Float)
    provider = relationship('Provider', back_populates='drg_stats')
    drg = relationship('DRG', back_populates='drg_stats')

# Indexes for efficient search
Index('ix_providers_zip_code', Provider.zip_code)
Index('ix_drgs_description', DRG.description) 