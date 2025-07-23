import os
import pandas as pd
import asyncio
import random
import pgeocode
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from api.models import Base, Provider, DRG, ProviderDRGStat

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@localhost:5432/cost_navigator')
CSV_FILE = 'data/MUP_INP_RY24_P03_V10_DY22_PrvSvc.csv'

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

def clean_str(val):
    if pd.isna(val):
        return None
    return str(val).strip()

def get_star_rating():
    return random.randint(1, 10)

nomi = pgeocode.Nominatim('US')

def get_lat_lon(zip_code):
    try:
        loc = nomi.query_postal_code(str(zip_code))
        if pd.isna(loc.latitude) or pd.isna(loc.longitude):
            return None, None
        return float(loc.latitude), float(loc.longitude)
    except Exception:
        return None, None

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def load_data():
    df = pd.read_csv(CSV_FILE, dtype=str).fillna('')
    async with AsyncSessionLocal() as session:
        for _, row in df.iterrows():
            provider_id = clean_str(row['Rndrng_Prvdr_CCN'])
            # Check if provider exists
            provider_exists = await session.execute(select(Provider).where(Provider.id == provider_id))
            provider = provider_exists.scalar_one_or_none()
            if not provider:
                zip_code = clean_str(row['Rndrng_Prvdr_Zip5'])
                lat, lon = get_lat_lon(zip_code)
                provider = Provider(
                    id=provider_id,
                    name=clean_str(row['Rndrng_Prvdr_Org_Name']),
                    address=clean_str(row['Rndrng_Prvdr_St']),
                    city=clean_str(row['Rndrng_Prvdr_City']),
                    state=clean_str(row['Rndrng_Prvdr_State_Abrvtn']),
                    zip_code=zip_code,
                    state_fips=clean_str(row['Rndrng_Prvdr_State_FIPS']),
                    ruca_code=clean_str(row['Rndrng_Prvdr_RUCA']),
                    ruca_desc=clean_str(row['Rndrng_Prvdr_RUCA_Desc']),
                    star_rating=get_star_rating(),
                    latitude=lat,
                    longitude=lon,
                )
                session.add(provider)
            drg_id = clean_str(row['DRG_Cd'])
            # Check if DRG exists
            drg_exists = await session.execute(select(DRG).where(DRG.id == drg_id))
            drg = drg_exists.scalar_one_or_none()
            if not drg:
                drg = DRG(
                    id=drg_id,
                    description=clean_str(row['DRG_Desc'])
                )
                session.add(drg)
            # Check if ProviderDRGStat exists
            stat_exists = await session.execute(
                select(ProviderDRGStat).where(
                    ProviderDRGStat.provider_id == provider_id,
                    ProviderDRGStat.drg_id == drg_id
                )
            )
            stat = stat_exists.scalar_one_or_none()
            if not stat:
                stat = ProviderDRGStat(
                    provider_id=provider_id,
                    drg_id=drg_id,
                    total_discharges=int(float(row['Tot_Dschrgs']) if row['Tot_Dschrgs'] else 0),
                    avg_covered_charges=float(row['Avg_Submtd_Cvrd_Chrg']) if row['Avg_Submtd_Cvrd_Chrg'] else None,
                    avg_total_payments=float(row['Avg_Tot_Pymt_Amt']) if row['Avg_Tot_Pymt_Amt'] else None,
                    avg_medicare_payments=float(row['Avg_Mdcr_Pymt_Amt']) if row['Avg_Mdcr_Pymt_Amt'] else None,
                )
                session.add(stat)
        await session.commit()

async def main():
    await create_tables()
    await load_data()

if __name__ == '__main__':
    asyncio.run(main()) 