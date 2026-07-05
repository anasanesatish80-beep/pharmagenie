# Deployment Guide

## Docker

```powershell
docker build -t pharmagenie .
docker run --env-file .env -p 8080:8080 pharmagenie
```

## Docker Compose

```powershell
docker compose up --build
```

API: `http://localhost:8080`

UI: `http://localhost:8501`

## Cloud Run Notes

The API container binds to `$PORT`, which is required by Cloud Run. Configure
runtime secrets through Cloud Run environment variables or Secret Manager rather
than committing `.env` values.

Suggested deployment command after project configuration:

```powershell
gcloud run deploy pharmagenie --source . --region us-central1 --allow-unauthenticated
```
