# Quick Reference

Use this page for the most common actions.

## Normal behavior

| Event | Expected result | Your action |
|---|---|---|
| New form submission | Appears in Airtable within ~1 hour | None |
| Submission edited | Record updates in Airtable | None |
| New Jotform question | Airtable field is created | Unhide field |
| Question renamed/deleted | No automatic rename/delete in Airtable | Update Airtable manually |

## Check sync status

1. Open GitHub repository.
2. Go to `Actions`.
3. Open latest `Sync Jotform to Airtable` run.
4. Confirm status icon:
- Green check: success
- Red X: failed
- Yellow: running

## Run manual sync

1. `Actions` tab
2. `Sync Jotform to Airtable`
3. `Run workflow`
4. Wait for completion

## Common fixes

| Problem | First action |
|---|---|
| New field not visible | Unhide field in Airtable |
| Run failed | Open `sync` logs in failed run |
| No recent runs | Check schedule and run manually |
| Wrong data | Compare with original Jotform submission |
| Access error | Re-check repo invitation and permissions |

## Safety reminders

- Do not share API keys in screenshots or chat.
- Keep Airtable field names aligned with Jotform names.
- Confirm success in Actions after manual changes.

## More help

- `USER_GUIDE.md` for detailed non-technical instructions
- `GITHUB_ACCESS_GUIDE.md` for account/access issues
- `TECHNICAL_SETUP_GUIDE.md` for technical troubleshooting
