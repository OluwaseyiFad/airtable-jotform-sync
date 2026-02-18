# Jotform to Airtable Sync

This project keeps Airtable in sync with Jotform submissions automatically (hourly via GitHub Actions).

It is built for teams that want reliable syncing without daily manual work.

## Start Here

If you are non-technical:

- Read `USER_GUIDE.md` for everyday use
- Keep `QUICK_REFERENCE.md` open for common tasks
- Use `GITHUB_ACCESS_GUIDE.md` if you are new to GitHub

If you are technical staff:

- Read `TECHNICAL_SETUP_GUIDE.md`
- Configure required GitHub Secrets:
  - `JOTFORM_API_KEY`
  - `JOTFORM_FORM_ID`
  - `AIRTABLE_TOKEN`
  - `AIRTABLE_BASE_ID`

## What Happens Automatically

- New Jotform submissions are added to Airtable
- Updated submissions are refreshed in Airtable
- New Jotform questions create new Airtable fields

Typical run time is 1-3 minutes.

## What Still Needs Manual Action

- Unhide newly created Airtable fields
- If a field is renamed or deleted in Jotform, make the matching change in Airtable

## Quick Health Check

1. Open the repository Actions tab.
2. Confirm recent `sync` runs are green.
3. Open Airtable and confirm recent submissions are present.

Status icons:
- Green check: success
- Red X: failed
- Yellow: running

## How Sync Works

1. GitHub Actions runs every hour.
2. `sync.py` pulls new or changed submissions from Jotform.
3. Records are upserted to Airtable.
4. `watermark.json` is updated so the next run only processes new changes.

## Local Run (Technical)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python sync.py --dry-run
```

Useful commands:

```bash
python sync.py --help
python sync.py --dry-run
python sync.py --ignore-watermark
python sync.py --skip-field-check
```

## Repository Map

- `.github/workflows/sync.yml`: hourly automation
- `sync.py`: main sync script
- `setup_airtable_fields.py`: field setup utility
- `watermark.json`: last successful sync marker
- `USER_GUIDE.md`: non-technical documentation
- `QUICK_REFERENCE.md`: short task guide
- `TECHNICAL_SETUP_GUIDE.md`: technical setup and architecture

## Security and Privacy Notes

- Credentials are stored in GitHub Secrets.
- API traffic uses HTTPS.
- This tool processes personal data and does not by itself satisfy privacy-law workflows (for example deletion/access request processes). Keep your compliance process documented separately.

## Support

- Usage questions: `USER_GUIDE.md` and `QUICK_REFERENCE.md`
- Technical troubleshooting: `TECHNICAL_SETUP_GUIDE.md`
- GitHub access help: `GITHUB_ACCESS_GUIDE.md`

## License

MIT
