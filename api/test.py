from deps import get_db, engine
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy import text
db: AsyncSession = Depends(get_db())

print(db)

query = """SELECT p.name, p.address, p.city, p.state, p.zip_code, p.star_rating
FROM providers p
JOIN provider_drg_stats ds ON p.id = ds.provider_id
JOIN drgs d ON ds.drg_id = d.id
WHERE d.description LIKE '%heart surgery%'
AND p.zip_code = '10032'
ORDER BY p.star_rating DESC;"""
async def run_query():
    async with engine.connect() as conn:
        result = await conn.execute(text(query))
        rows = result.mappings().all()   # list of dict-like rows
    await engine.dispose()
    return rows

import asyncio

rows = asyncio.run(run_query())
print(rows)   



# async def run_query(zip_code: str):
#     engine = create_async_engine(DATABASE_URL, echo=False, future=True)
#     sql = text("""
#         SELECT p.name, p.address, p.city, p.state, p.zip_code, p.star_rating
#         FROM providers p
#         JOIN provider_drg_stats ds ON p.id = ds.provider_id
#         JOIN drgs d ON ds.drg_id = d.id
#         WHERE d.description ILIKE :pattern
#           AND p.zip_code = :zip
#         ORDER BY p.star_rating DESC
#     """)
#     async with engine.connect() as conn:
#         result = await conn.execute(sql, {"pattern": "%heart surgery%", "zip": zip_code})
#         rows = result.mappings().all()   # list of dict-like rows
#     await engine.dispose()
#     return rows




"""SELECT 
    p.id AS provider_id,
    p.name,
    p.address,
    p.city,
    p.state,
    p.zip_code,
    p.star_rating,
    d.id AS drg_id,
    d.description AS drg_description,
    s.total_discharges,
    s.avg_covered_charges,
    s.avg_total_payments,
    s.avg_medicare_payments
FROM providers p
JOIN provider_drg_stats s ON p.id = s.provider_id
JOIN drgs d ON s.drg_id = d.id
WHERE p.id = '010001'
  AND d.id = '023'
LIMIT 5;"""