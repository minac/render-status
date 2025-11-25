# Project Instructions

## Testing
**ALWAYS** run `uv run render-status` and run the linter after any code changes to verify the CLI still works correctly.

## Architecture
- CLI tool that displays Render.com service status and deploy information
- Uses Render API v1
- Displays all timestamps in system's local timezone
- Supports both single-run (`--once`) and live-update modes (refreshes every 10s)
- Status indicators with bold colors (green/yellow/red)
- Main components:
  - `client.py`: HTTP client for Render API
  - `cli.py`: Display logic and table formatting with Rich library

## API Response Structure
Render API wraps all responses in objects with specific keys:
- `/services` returns: `[{service: {...}}, ...]`
- `/services/:id/deploys` returns: `[{deploy: {...}}, ...]`
- `/services/:id/jobs` returns: `[{job: {...}}, ...]` (often empty for cron jobs)

Extract the nested objects in client methods before returning.

## Cron Job Fields
- Schedule: `service.serviceDetails.schedule`
- Last run: `service.serviceDetails.lastSuccessfulRunAt`
- Jobs endpoint returns empty array; use `lastSuccessfulRunAt` instead

## Environment
- API key: `RENDER_API_KEY` in `.env`
- Do not commit `.env` file
