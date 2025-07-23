from fastapi import FastAPI, Depends, Query, HTTPException
from typing import Optional, List
from api.deps import get_db
from api.schemas import ProviderOut, DRGOut
from api.crud import search_providers
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import os
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from api.prompts import PROMPT_TEMPLATE, SUMMARY_PROMPT_TEMPLATE
from fastapi.responses import HTMLResponse
from sqlalchemy import text

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

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <body>
            <h2>Healthcare Cost Navigator</h2>
            <h3>Ask a Question (AI Assistant)</h3>
            <form action="/ask" method="post" id="ask-form">
                <label for="question">Ask a question:</label><br>
                <input type="text" id="question" name="question" style="width:400px"><br><br>
                <input type="submit" value="Ask">
            </form>
            <div id="answer"></div>
            <hr>
            <h3>Search Hospitals by DRG, ZIP, and Radius</h3>
            <form id="provider-search">
                <input type="text" name="drg" placeholder="DRG code or description">
                <input type="text" name="zip" placeholder="ZIP code">
                <input type="number" name="radius_km" placeholder="Radius (km)">
                <button type="submit">Search</button>
            </form>
            <pre id="results"></pre>
            <script>
                document.getElementById('ask-form').onsubmit = async function(e) {
                    e.preventDefault();
                    const question = document.getElementById('question').value;
                    const response = await fetch('/ask', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ question })
                    });
                    const data = await response.json();
                    document.getElementById('answer').innerText = data.answer;
                };
                document.getElementById('provider-search').onsubmit = async function(e) {
                    e.preventDefault();
                    const drg = e.target.drg.value;
                    const zip = e.target.zip.value;
                    const radius_km = e.target.radius_km.value;
                    const params = new URLSearchParams({ drg, zip, radius_km });
                    const response = await fetch('/providers?' + params.toString());
                    const data = await response.json();
                    document.getElementById('results').innerText = JSON.stringify(data, null, 2);
                };
            </script>
        </body>
    </html>
    """

class AskRequest(BaseModel):
    question: str

@app.post('/ask')
async def ask_endpoint(request: AskRequest, db: AsyncSession = Depends(get_db)):
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"), temperature=0)
    # Step 1: Generate SQL query from question
    try:
        prompt = PROMPT_TEMPLATE.format(question=request.question)
        chain = PromptTemplate.from_template(prompt)
        sql_query_resp = await llm.ainvoke(chain.format())
        sql_query = sql_query_resp.content.strip() if hasattr(sql_query_resp, 'content') else str(sql_query_resp).strip()
        # Remove code fences (```sql ... ```)
        pattern = r"^```[a-zA-Z]*\n|```$"
        query = re.sub(pattern, "", sql_query, flags=re.MULTILINE).strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating SQL from LLM: {e}")

    # Step 2: Handle out-of-scope and validate query
    if query.upper().startswith("OUT_OF_SCOPE"):
        return {"answer": "I can only help with hospital pricing and quality information. Please ask about medical procedures, costs, or hospital ratings."}
    if not query.lower().startswith("select"):
        raise HTTPException(status_code=400, detail="Generated query is not a SELECT statement.")

    # Step 3: Execute SQL and fetch results
    try:
        print("Here issql_query", query)
        result = await db.execute(text(query))

        
        rows = result.fetchall()
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in rows]
        print("Here is result", data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error executing query: {e}")

    # Step 4: Summarize results using LLM
    try:
        summary_prompt = SUMMARY_PROMPT_TEMPLATE.format(question=request.question, data=data)
        print(type(data))
        # summary_chain = PromptTemplate.from_template(summary_prompt)
        # print("Here is summary_chain", summary_chain)
        summary_resp = await llm.ainvoke(summary_prompt)
        # print("Here is summary_resp", summary_resp)

        summary = summary_resp.content.strip() if hasattr(summary_resp, 'content') else str(summary_resp).strip()

        return {"answer": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary from LLM: {e}") 