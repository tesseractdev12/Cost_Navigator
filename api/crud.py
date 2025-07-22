from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from migration.models import Provider, DRG, ProviderDRGStat
from typing import Optional

async def search_providers(session, drg: Optional[str] = None, zip_code: Optional[str] = None, radius_km: Optional[float] = None):
    query = select(Provider, ProviderDRGStat, DRG).join(ProviderDRGStat, Provider.id == ProviderDRGStat.provider_id).join(DRG, DRG.id == ProviderDRGStat.drg_id)
    if drg:
        # Match by DRG code or description (ILIKE for fuzzy search)
        query = query.where((DRG.id == drg) | (DRG.description.ilike(f"%{drg}%")))
    if zip_code:
        query = query.where(Provider.zip_code == zip_code)
    # TODO: Implement radius_km logic using geocoding if needed
    query = query.order_by(ProviderDRGStat.avg_covered_charges)
    result = await session.execute(query)
    rows = result.all()
    # Group by provider, aggregate DRGs for each provider
    providers = {}
    for provider, stat, drg in rows:
        if provider.id not in providers:
            providers[provider.id] = {
                'provider': provider,
                'drgs': [],
                'avg_covered_charges': stat.avg_covered_charges,
                'avg_total_payments': stat.avg_total_payments,
                'avg_medicare_payments': stat.avg_medicare_payments,
                'total_discharges': stat.total_discharges,
            }
        providers[provider.id]['drgs'].append(drg)
    return list(providers.values()) 