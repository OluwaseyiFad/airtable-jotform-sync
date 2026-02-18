# User Guide: Jotform to Airtable Sync

This guide is for non-technical users.

## What this tool does

- People submit forms in Jotform.
- The system copies submissions into Airtable every hour.
- Updates to existing submissions also sync automatically.

## What happens automatically vs manually

Automatic:
- New submissions appear in Airtable.
- Edited submissions are updated in Airtable.
- New Jotform questions create Airtable fields.

Manual:
- Unhide newly created Airtable fields.
- If a field is renamed in Jotform, rename it in Airtable.
- If a field is deleted in Jotform, delete it in Airtable.

## Daily check (30 seconds)

1. Open the repository on GitHub.
2. Click the `Actions` tab.
3. Look at the latest `sync` run.
4. Confirm you see a green check.

Status icons:
- Green check: success
- Red X: failed
- Yellow dot: running

## Common tasks

### Unhide a new Airtable field

1. Open your Airtable table.
2. Open hidden fields.
3. Find the new field and click the eye icon.
4. Move the column to your preferred position.

### Rename a field safely

1. Rename the question in Jotform.
2. Rename the matching Airtable field to the same name.
3. Run a manual sync.
4. Confirm new submissions update the right column.

### Delete a field safely

1. Delete the question in Jotform.
2. Delete the matching Airtable field.
3. Run a manual sync.
4. Confirm no errors in Actions.

### Run a manual sync

1. Go to GitHub `Actions`.
2. Select `Sync Jotform to Airtable`.
3. Click `Run workflow`.
4. Wait for completion (usually 1-3 minutes).

## Troubleshooting

| Problem | First check | Next step |
|---|---|---|
| New field not visible | Hidden fields in Airtable | Unhide the field |
| Sync failed | Open latest failed run | Read error message in `sync` job |
| Sync has not run recently | Check schedule and latest run time | Run workflow manually |
| Data looks incorrect | Compare with original Jotform response | Re-run sync and recheck |
| Cannot open repo | Confirm GitHub invitation accepted | See `GITHUB_ACCESS_GUIDE.md` |

## Before asking for help

Collect these details:
- Link to the failed GitHub Actions run
- Time the issue started
- Example submission ID or record
- Screenshot of error message

## Related docs

- `QUICK_REFERENCE.md` for fast steps
- `GITHUB_ACCESS_GUIDE.md` for GitHub access help
- `TECHNICAL_SETUP_GUIDE.md` for technical setup and maintenance
