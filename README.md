# Render Status

CLI tool to check Render deploy and cron job status.

## Installation

```bash
uv sync
```

## Configuration

Create `.env` file with your Render API key:

```bash
cp .env.example .env
```

Edit `.env`:
```
RENDER_API_KEY=your_api_key_here
```

Get your API key from: https://dashboard.render.com/u/settings

## Usage

Live update mode (refreshes every 10s):
```bash
uv run render-status
```

Single run mode:
```bash
uv run render-status --once
```

## Output

Displays two tables:

1. **Render Services**: All services with latest deploy status, type, and timestamps
2. **Cron Jobs**: Cron jobs with schedule, last run time, and status

All timestamps are displayed in your system's local timezone.

Status colors (bold):
- 🟢 Green: `live`, `succeeded`, `success`
- 🟡 Yellow: `building`, `deploying`, `running`
- 🔴 Red: `build_failed`, `failed`, `canceled`

## Development

Install dev dependencies:
```bash
uv sync --dev
```

Run tests:
```bash
uv run pytest
```

Lint:
```bash
ruff check .
```

## Requirements

- Python >=3.11
- Render API key with read access
