# Technical Setup Guide: Jotform to Airtable Sync

This guide is for setup and maintenance.

## System overview

- Source: Jotform
- Destination: Airtable
- Orchestration: GitHub Actions (hourly)
- Sync script: `sync.py`
- State tracking: `watermark.json`

Data flow:
1. Fetch new/updated Jotform submissions.
2. Map fields and normalize values.
3. Upsert records in Airtable.
4. Update watermark for incremental sync.

## Repository structure

- `.github/workflows/sync.yml`: schedule and job definition
- `sync.py`: sync logic
- `setup_airtable_fields.py`: helper for field setup
- `watermark.json`: last processed update marker
- `requirements.txt`: Python dependencies

## Prerequisites

- Python 3.11+
- Airtable personal access token with base permissions
- Jotform API key and form ID
- GitHub repository admin access (for secrets/workflow)

## Required secrets

Configure in repository settings:

- `JOTFORM_API_KEY`
- `JOTFORM_FORM_ID`
- `AIRTABLE_TOKEN`
- `AIRTABLE_BASE_ID`

Optional (if implemented in your environment):
- `AIRTABLE_TABLE_NAME`

## Local setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `.env`:

```bash
JOTFORM_API_KEY=...
JOTFORM_FORM_ID=...
AIRTABLE_TOKEN=...
AIRTABLE_BASE_ID=...
```

Run checks:

```bash
python sync.py --dry-run
python sync.py
```

Useful flags:

```bash
python sync.py --ignore-watermark
python sync.py --skip-field-check
python sync.py --help
```

## Workflow behavior

- Scheduled hourly via `.github/workflows/sync.yml`
- Can be run manually from Actions tab
- Typical runtime: 1-3 minutes
- Incremental processing based on watermark

## Field handling notes

- New Jotform questions can create Airtable fields automatically.
- Airtable field renames/deletes are not fully automatic.
- Keep Jotform and Airtable names aligned when renaming.
- For deleted Jotform fields, remove Airtable columns manually.

## Operational runbook

Daily checks:
- Confirm recent workflow runs are green.
- Check runtime and record counts for unusual drops/spikes.

When a run fails:
1. Open failed run in GitHub Actions.
2. Inspect `sync` job logs.
3. Identify failing phase (fetch, transform, upsert, watermark).
4. Fix config or data issue.
5. Re-run workflow.

When data is missing:
1. Verify submission exists in Jotform.
2. Run with `--ignore-watermark` if safe for your case.
3. Confirm record key mapping is stable.

## Common failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| 401/403 API error | Bad/expired token | Rotate secret and rerun |
| 404 on base/table | Wrong Airtable ID | Correct base/table config |
| New fields not visible | Field created as hidden | Unhide in Airtable |
| Duplicate records | Key mapping drift | Verify unique submission key logic |
| No hourly runs | Workflow disabled/schedule issue | Check `sync.yml` and Actions settings |

## Security and compliance

- Store credentials only in GitHub Secrets or local `.env`.
- Never commit tokens to git.
- Rotate API keys on personnel changes.
- This tool moves personal data; document your retention/deletion process separately.

## Change management

Before deploying changes:
1. Run local `--dry-run`.
2. Validate with a manual Actions run.
3. Confirm records and field mappings in Airtable.
4. Monitor the next scheduled run.

## Related docs

- `README.md`: high-level overview
- `USER_GUIDE.md`: non-technical operations
- `QUICK_REFERENCE.md`: quick tasks
- `GITHUB_ACCESS_GUIDE.md`: access and GitHub basics
