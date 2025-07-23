# Healthcare Cost Navigator (MVP)

A minimal web service for searching hospitals by MS-DRG procedure, viewing estimated prices & quality ratings, and interacting with an AI assistant for natural language queries.

## Features
- Search hospitals by DRG, ZIP, and radius (fuzzy DRG search supported)
- View estimated prices and star ratings
- AI assistant for natural language cost/quality queries
- Minimal interface (raw HTML/JSON, no styling)

## Tech Stack
- Python 3.11, FastAPI, async SQLAlchemy, PostgreSQL, OpenAI API

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd Cost_navigator
```

### 2. Docker Compose Setup
Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=sk-...
```

Build and start the app and database:
```bash
docker-compose up --build
```

This will start both the FastAPI app (on port 8000) and PostgreSQL (on port 5432).

### 3. Database Seeding (ETL)
- Place your CMS CSV file in the `data/` directory.
- Run the ETL script inside the app container:
```bash
docker-compose exec app .venv/bin/python api/etl.py
```

---

## API Endpoints

### GET /providers
Search hospitals by DRG, ZIP, and radius (km):
```bash
curl "http://localhost:8000/providers?drg=470&zip=10001&radius_km=40"
```

### POST /ask
Ask natural language questions about costs, quality, or ratings:
```bash
curl -X POST "http://localhost:8000/ask" -H "Content-Type: application/json" -d '{"question": "Who has the best ratings for heart surgery near 10032?"}'
```

---

## Example Prompts for the AI Assistant
1. Who is the cheapest for DRG 470 within 25 miles of 10001?
2. Which hospitals have the best ratings for heart surgery near 10032?
3. What is the average covered charge for DRG 023 at Southeast Health Medical Center?
4. List the top 3 hospitals by star rating for DRG 038 in Alabama.
5. How many total discharges were there for DRG 023 at Southeast Health Medical Center?
6. What is the weather like in New York today? (out-of-scope)

---

## Architecture Decisions & Trade-offs
- **Minimal UI:** Raw HTML/JSON for speed and clarity.
- **Async SQLAlchemy:** For scalable, non-blocking DB access.
- **OpenAI for NL→SQL:** Flexible, powerful natural language interface.
- **No geospatial radius:** Only ZIP filtering implemented for MVP; can be extended with PostGIS.
- **Mock star ratings:** Randomly generated for demo; can be replaced with real data.

---

## Demo
- See attached Loom video for a walkthrough.
- Example GIF/clip: (insert here)

---

## Contact
For questions, contact [your email].
