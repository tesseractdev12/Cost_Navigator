from fastapi import FastAPI, Depends, Query, HTTPException
from typing import Optional, List
from deps import get_db
from schemas import ProviderOut, DRGOut
from crud import search_providers
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from prompts import PROMPT_TEMPLATE

load_dotenv()

app = FastAPI()

@app.get('/providers', response_model=List[ProviderOut])
async def get_providers(
    drg: Optional[str] = Query(None, description="DRG code or description"),
    zip: Optional[str] = Query(None, description="ZIP code"),
    radius_km: Optional[float] = Query(None, description="Radius in kilometers"),
    db=Depends(get_db)
):
    results = await search_providers(db, drg=drg, zip_code=zip, radius_km=radius_km)
    providers_out = []
    for entry in results:
        provider = entry['provider']
        drgs = [DRGOut(id=drg.id, description=drg.description) for drg in entry['drgs']]
        providers_out.append(ProviderOut(
            id=provider.id,
            name=provider.name,
            address=provider.address,
            city=provider.city,
            state=provider.state,
            zip_code=provider.zip_code,
            star_rating=provider.star_rating,
            drgs=drgs,
            avg_covered_charges=entry['avg_covered_charges'],
            avg_total_payments=entry['avg_total_payments'],
            avg_medicare_payments=entry['avg_medicare_payments'],
            total_discharges=entry['total_discharges'],
        ))
    return providers_out

class AskRequest(BaseModel):
    question: str

@app.post('/ask')
async def ask_endpoint(request: AskRequest, db: AsyncSession = Depends(get_db)):
    # Prepare prompt
    prompt = PROMPT_TEMPLATE.format(question=request.question)
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    chain = PromptTemplate.from_template(prompt)
    sql_query = await llm.ainvoke(chain.format())
    sql_query = sql_query.strip()
    if sql_query.upper().startswith("OUT_OF_SCOPE"):
        return {"answer": "I can only help with hospital pricing and quality information. Please ask about medical procedures, costs, or hospital ratings."}
    # Only allow SELECT queries for safety
    if not sql_query.lower().startswith("select"):
        raise HTTPException(status_code=400, detail="Generated query is not a SELECT statement.")
    try:
        result = await db.execute(sql_query)
        rows = result.fetchall()
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in rows]
        return {"answer": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error executing query: {e}") 