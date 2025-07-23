from sqlalchemy import select, or_, func
from api.models import Provider, DRG, ProviderDRGStat
from typing import Optional
import pgeocode
import math

nomi = pgeocode.Nominatim('US')

def haversine_expr(lat1, lon1, lat2_col, lon2_col):
    # Returns the SQLAlchemy expression for Haversine distance in km
    return 6371 * func.acos(
        func.cos(func.radians(lat1)) * func.cos(func.radians(lat2_col)) * func.cos(func.radians(lon2_col) - func.radians(lon1)) +
        func.sin(func.radians(lat1)) * func.sin(func.radians(lat2_col))
    )

async def search_providers(session, drg: Optional[str] = None, zip_code: Optional[str] = None, radius_km: Optional[float] = None):
    query = (
        select(Provider, ProviderDRGStat, DRG)
        .join(ProviderDRGStat, Provider.id == ProviderDRGStat.provider_id)
        .join(DRG, DRG.id == ProviderDRGStat.drg_id)
    )
    if drg:
        query = query.where(or_(DRG.id == drg, DRG.description.ilike(f"%{drg}%")))
    if zip_code and radius_km:
        loc = nomi.query_postal_code(str(zip_code))
        if not (math.isnan(loc.latitude) or math.isnan(loc.longitude)):
            lat1, lon1 = float(loc.latitude), float(loc.longitude)
            distance_expr = haversine_expr(lat1, lon1, Provider.latitude, Provider.longitude)
            query = query.where(distance_expr <= radius_km)
    elif zip_code:
        query = query.where(Provider.zip_code == zip_code)
    query = query.order_by(ProviderDRGStat.avg_covered_charges.asc())
    result = await session.execute(query)
    rows = result.all()
    providers = []
    for provider, stat, drg in rows:
        providers.append({
            'provider': provider,
            'drgs': [drg],
            'avg_covered_charges': stat.avg_covered_charges,
            'avg_total_payments': stat.avg_total_payments,
            'avg_medicare_payments': stat.avg_medicare_payments,
            'total_discharges': stat.total_discharges,
        })
    return providers 