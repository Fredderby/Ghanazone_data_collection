# Deeper Life Bible Church — Attendance Collection

A simple, modern web form for collecting one aggregated church attendance report per country for **Sunday, 29 November 2026**, including online attendance. Submissions are stored in MySQL.

## Configuration

Database settings come from environment variables (or `.env` for local development):

```
DB_HOST=mysql-202931-0.cloudclusters.net
DB_PORT=19944
DB_USER=...
DB_PASSWORD=...
DB_NAME=smatsouls
```

See `.env.example` for the template. The `submissions` table is created automatically on startup.

## Local development

```powershell
.\env\Scripts\pip.exe install -r requirements.txt
.\env\Scripts\python.exe app.py
```

Open <http://127.0.0.1:5000>.

## Docker / Dokploy deployment (port 3001)

The image serves the app with Gunicorn on **port 3001**. `wsgi.py` creates the database table at startup.

```powershell
docker compose up -d --build
```

Then open <http://localhost:3001>.

### Deploying on Dokploy

1. Create a new **Docker Compose** application and point it at this repository/folder.
2. Set the service port to **3001** in Dokploy (or let `docker-compose.yml` publish `3001:3001`).
3. Add these environment variables in the Dokploy app settings:
   - `DB_HOST`
   - `DB_PORT` (default `3306`)
   - `DB_USER`
   - `DB_PASSWORD`
   - `DB_NAME`
4. Deploy. Dokploy will build the image and start the container.

Secrets are never baked into the image — `.env` is excluded by `.dockerignore`; values come from the deployment environment.

## Pages

| URL | Purpose |
|---|---|
| `/` | Attendance collection form |
| `/submit` | POST endpoint (form submission) |
| `/submissions` | Read-only list of submitted reports |
| `/health` | Health check including database status |

## Tests

```powershell
.\env\Scripts\python.exe -m pytest -v
```
