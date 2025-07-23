from sqlalchemy import select, or_
from migration.models import Provider, DRG, ProviderDRGStat
from typing import Optional

async def search_providers(session, drg: Optional[str] = None, zip_code: Optional[str] = None, radius_km: Optional[float] = None):
    # Build the base query joining all three tables
    query = (
        select(Provider, ProviderDRGStat, DRG)
        .join(ProviderDRGStat, Provider.id == ProviderDRGStat.provider_id)
        .join(DRG, DRG.id == ProviderDRGStat.drg_id)
    )
    # Filter by DRG code or fuzzy description
    if drg:
        query = query.where(or_(DRG.id == drg, DRG.description.ilike(f"%{drg}%")))
    # Filter by ZIP code
    if zip_code:
        query = query.where(Provider.zip_code == zip_code)
    # (Optional) Radius logic could go here
    # Sort by avg_covered_charges (ascending)
    query = query.order_by(ProviderDRGStat.avg_covered_charges.asc())
    # Execute and process results
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