# GitHub Access Guide

This guide is for team members who are new to GitHub.

## Why you need GitHub for this project

- The sync runs from GitHub Actions.
- You check status and errors in the repository.
- You can run a manual sync when needed.

## Step 1: Create a GitHub account

1. Go to `https://github.com`.
2. Click `Sign up`.
3. Complete email verification.
4. Save your username and password securely.

## Step 2: Accept repository access

1. Open your email invitation from GitHub.
2. Click `Join` or `Accept invitation`.
3. Confirm you can open this repository.

If no invitation is found:
- Check spam/junk folders.
- Ask the repository owner to resend access.

## Step 3: Find what you need in the repository

Main tabs:
- `Code`: files and documentation
- `Actions`: sync runs and logs
- `Issues`: reported problems and follow-ups

## Step 4: Check sync status

1. Open `Actions`.
2. Click the latest `Sync Jotform to Airtable` run.
3. Check status:
   - Green check: success
   - Red X: failed
   - Yellow: in progress

## Step 5: Run a manual sync

1. Open `Actions`.
2. Click `Sync Jotform to Airtable`.
3. Click `Run workflow`.
4. Wait until it completes.

## Mobile use (optional)

You can use the GitHub mobile app to:
- Check if runs are green/red
- Open run logs
- Trigger manual workflow runs

Desktop is usually easier for troubleshooting.

## Security basics

- Use a strong password.
- Turn on two-factor authentication in GitHub settings.
- Never share API keys in chat, email, or screenshots.
- If you leave the team, ask the owner to remove your access.

## Quick troubleshooting

| Issue | What to do |
|---|---|
| Cannot sign in | Reset password from GitHub login page |
| No repository access | Confirm invitation accepted; ask owner to re-invite |
| Actions tab missing | You may not have enough permissions |
| Run failed | Open the run and read `sync` job logs |

## Related docs

- `USER_GUIDE.md` for non-technical daily workflows
- `QUICK_REFERENCE.md` for fast task steps
- `TECHNICAL_SETUP_GUIDE.md` for technical maintenance
