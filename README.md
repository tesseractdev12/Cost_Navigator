# Healthcare Cost Navigator (MVP)

A minimal web service for searching hospitals by MS-DRG procedure, viewing estimated prices & quality ratings, and interacting with an AI assistant for natural language queries.

---

## 🚀 Features
- Search hospitals by DRG, ZIP, and radius (fuzzy DRG search supported)
- View estimated prices and star ratings
- AI assistant for natural language cost/quality queries
- Minimal interface (raw HTML/JSON, no styling)

---

## 🐳 Docker Compose Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <your-repo-url>
   cd Cost_navigator
   ```

2. **Set up Environment Variables**
   - Copy the example env file and add your OpenAI API key:
     ```bash
     make env
     make chmod
     # Then edit .env and set OPENAI_API_KEY=sk-...
     ```

3. **Build and Start the App and Database**
   ```bash
   make infrastructure-up
   ```
   - This will start FastAPI (on port 8000) and PostgreSQL (on port 5432).

---

## 🗃️ Database Seeding Instructions

- Place your CMS CSV file in the `data/` directory.
- Seed the database (run ETL) inside the app container:
  ```bash
  make seed
  ```
  - This runs `scripts/seed.sh`, which should call your ETL script (e.g., `.venv/bin/python api/etl.py`).

---

## 🧪 Sample cURL Commands for All Endpoints

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

## 💡 5+ Example Prompts for the AI Assistant
1. Who is the cheapest for DRG 470 within 25 miles of 10001?
2. Which hospitals have the best ratings for heart surgery near 10032?
3. What is the average covered charge for DRG 023 at Southeast Health Medical Center?
4. List the top 3 hospitals by star rating for DRG 038 in Alabama.
5. How many total discharges were there for DRG 023 at Southeast Health Medical Center?
6. What is the weather like in New York today? (out-of-scope)

---

## 🏗️ Architecture Decisions & Trade-offs
- **Minimal UI:** Raw HTML/JSON for speed and clarity.
- **Async SQLAlchemy:** For scalable, non-blocking DB access.
- **OpenAI for NL→SQL:** Flexible, powerful natural language interface.
- **Geospatial radius search:** Uses pgeocode for ZIP-to-lat/lon and Haversine formula for radius queries.
- **Mock star ratings:** Randomly generated for demo; can be replaced with real data.
- **Idempotent ETL:** Safe to run multiple times, avoids duplicate data.

---

## 🎬 Demo
- See attached Loom video for a walkthrough.
- Example GIF/clip: (insert here)

---

## 🛠️ Makefile Commands
- `make chmod` — Change the mode of bash files to be executable 
- `make infrastructure-build` — Build Docker Compose services
- `make infrastructure-up` — Start the stack (app + db)
- `make env` — Copy `.env.example` to `.env` for OpenAI key setup
- `make seed` — Seed the database (run ETL in container)
- `make infrastructure-down` — To turn down the infrastructure

---

## 📄 .env Setup
- Copy `.env.example` to `.env` and set your OpenAI API key:
  ```
  OPENAI_API_KEY=sk-...
  ```

---

## 📬 Contact
For questions, contact [your email].
