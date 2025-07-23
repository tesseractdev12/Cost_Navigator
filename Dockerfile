FROM python:3.11-slim

# Install uv (ultra fast Python package/dependency manager)
RUN pip install uv

WORKDIR /app
COPY requirements.txt requirements.txt 

RUN uv pip install -r requirements.txt --system

COPY . .

EXPOSE 8000



ENTRYPOINT ["./scripts/run.sh"]