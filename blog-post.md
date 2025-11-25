# Building a CLI Tool to Monitor Render.com Services with Claude

## The Problem

Recently, I've been playing around with Claude Code to develop some ideas. After a a bit of research, I decided on render.com my PaaS for hosting and deployment.

However, managing multiple services on Render requires me to go back and forth between the dashboard and the CLI. So I decided to create this tool.

## The Solution

I (read, Claude) built `render-status`, a Python CLI tool that displays all Render services, their deployment status, and cron job execution in a live-updating terminal interface.

## Technical Decisions

### Why Python?

Because I like it. And it plays well with LLMs. And has modern tooling. :)

### Architecture: Simple Over Clever

The tool follows a straightforward two-layer architecture. There is no state management, no caching, no abstractions beyond what's necessary.

### Timezone Display

All timestamps convert from UTC to system local time:

```python
def format_timestamp(ts: str | None) -> str:
    if not ts:
        return "N/A"
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    local_dt = dt.astimezone()
    tz_name = local_dt.strftime("%Z")
    return local_dt.strftime(f"%Y-%m-%d %H:%M:%S {tz_name}")
```

Users see timestamps in their context, not UTC math.

### Live Updates vs. Single Run

The tool supports two modes:
- Default: Refresh every 10 seconds using Rich's `Live` display
- `--once`: Fetch once and exit

## Conclusion

This tool solved a real problem: quick visibility into Render service health without leaving the terminal. Total development time was about 2 hours, including tests and documentation.

The codebase is ~500 lines of Python. No database, no state management, no complex patterns. Just HTTP requests and terminal rendering.

The best solution is usually the boring one.

---

**Repository**: [render-status](https://github.com/minac/render-status.git)
**Stack**: Python 3.11+, httpx, Rich, uv
**License**: MIT
