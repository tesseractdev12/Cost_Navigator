FROM python:3.11-slim

# Install uv (ultra fast Python package/dependency manager)
RUN pip install uv

WORKDIR /app
COPY requirements.txt requirements.txt 

RUN uv pip install -r requirements.txt --system


# Copy project files
COPY . .

# Create and activate virtual environment, install dependencies from requirements.txt

# Expose port
EXPOSE 8000



# Run the FastAPI app
# CMD [".venv/bin/uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"] 

ENTRYPOINT ["./scripts/run.sh"]