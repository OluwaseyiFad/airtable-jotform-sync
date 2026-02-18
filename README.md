# 🔄 Jotform to Airtable Sync

**Automated synchronization tool for non-profit organizations**

[![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📖 What is This?

This tool **automatically syncs** form submissions from Jotform to Airtable every hour. It's designed specifically for non-profit organizations that use Jotform to collect volunteer applications, registrations, or other data, and need that information organized in Airtable.

### ✨ Key Features

- **🤖 Automatic Sync** - Runs every hour without manual intervention
- **🔄 Smart Updates** - Only processes new or changed submissions
- **🆕 Auto-Field Creation** - Automatically creates Airtable columns for new Jotform questions
- **🔐 Secure** - API credentials stored safely in GitHub Secrets
- **📊 Transparent** - Full visibility into sync status via GitHub Actions
- **🛡️ Safe** - Incremental sync prevents data loss

---

## 🚀 Quick Start

### For End Users

If you're a non-technical user who needs to **use** this tool:

1. **📚 Read the [USER_GUIDE.md](USER_GUIDE.md)** - Complete guide for day-to-day operations
2. **📋 Bookmark [QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - One-page cheat sheet for common tasks
3. **👤 Check [GITHUB_ACCESS_GUIDE.md](GITHUB_ACCESS_GUIDE.md)** - If you're new to GitHub

### For Technical Staff

If you're setting up or maintaining this tool:

1. **🔧 Read the [TECHNICAL_SETUP_GUIDE.md](TECHNICAL_SETUP_GUIDE.md)** - Comprehensive technical documentation
2. **⚙️ Configure GitHub Secrets** - Required: `JOTFORM_API_KEY`, `JOTFORM_FORM_ID`, `AIRTABLE_TOKEN`, `AIRTABLE_BASE_ID`
3. **🧪 Test locally** - Run `python sync.py --dry-run` to verify configuration

### For Video Tutorials

Complete video scripts and production guide available:

- **🎥 [VIDEO_RECORDING_SCRIPT.md](VIDEO_RECORDING_SCRIPT.md)** - Scripts for 5 tutorial videos (~25 minutes total)

---

## 🎯 What This Tool Does

### Automatic Operations (No Action Required)

The following happen automatically every hour:

| What | Description | Your Action |
|------|-------------|-------------|
| ✅ **New Submissions** | Someone fills out your Jotform | None - just view in Airtable |
| ✅ **Updated Submissions** | Someone edits their response | None - changes sync automatically |
| ✅ **New Field Creation** | You add a question to Jotform | Unhide the column in Airtable |

### Manual Operations (Quick Actions Required)

Some tasks require brief manual action in both platforms:

| What | Where | Time Required |
|------|-------|---------------|
| 👁️ **Unhide New Fields** | Airtable | ~30 seconds |
| ❌ **Delete Fields** | Jotform + Airtable | ~2 minutes |
| ✏️ **Rename Fields** | Jotform + Airtable | ~2 minutes |

> **💡 Pro Tip:** Check the [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for step-by-step instructions on these tasks!

---

## 📚 Complete Documentation

### User Documentation (Non-Technical)

- **[USER_GUIDE.md](USER_GUIDE.md)** - Complete guide for managing the sync tool
  - Understanding the system
  - Step-by-step instructions with screenshots
  - Troubleshooting common issues
  - How to get help

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - One-page cheat sheet
  - Common tasks at a glance
  - Quick troubleshooting
  - Contact information

- **[GITHUB_ACCESS_GUIDE.md](GITHUB_ACCESS_GUIDE.md)** - GitHub for beginners
  - Creating a GitHub account
  - Accepting repository access
  - Understanding the Actions tab
  - Security best practices

### Technical Documentation

- **[TECHNICAL_SETUP_GUIDE.md](TECHNICAL_SETUP_GUIDE.md)** - Comprehensive technical guide
  - System architecture
  - File structure explanation
  - Watermark system details
  - Field mappings and type conversions
  - Running locally
  - Security and data privacy
  - Advanced customization

### Video Production

- **[VIDEO_RECORDING_SCRIPT.md](VIDEO_RECORDING_SCRIPT.md)** - Complete video tutorial scripts
  - Video 1: Overview & Introduction (5-7 min)
  - Video 2: Making New Fields Visible (3-4 min)
  - Video 3: Deleting and Renaming Fields (5-6 min)
  - Video 4: Running Manual Sync & Checking Status (4-5 min)
  - Video 5: Troubleshooting Common Issues (6-8 min)

---

## 🎬 Video Tutorials

> 📹 **Coming Soon!** Complete video tutorial series to accompany this documentation.

### Planned Videos

1. **Overview & Introduction** (5-7 min) - [Placeholder]
   - What the tool does and why it matters
   
2. **Making New Fields Visible** (3-4 min) - [Placeholder]
   - How to unhide columns in Airtable
   
3. **Deleting and Renaming Fields** (5-6 min) - [Placeholder]
   - Safe procedures for field management
   
4. **Running Manual Sync & Checking Status** (4-5 min) - [Placeholder]
   - Triggering syncs and monitoring health
   
5. **Troubleshooting Common Issues** (6-8 min) - [Placeholder]
   - Diagnosing and fixing problems

**Total Duration:** ~25 minutes  
**Production Guide:** See [VIDEO_RECORDING_SCRIPT.md](VIDEO_RECORDING_SCRIPT.md)

---

## ✅ How to Check if Sync is Working

### Quick Health Check (30 seconds)

1. **Go to GitHub Actions Tab**
   - Navigate to: `github.com/OluwaseyiFad/airtable-jotform-sync/actions`

2. **Look for Green Checkmarks**
   - ✅ Green checkmark = Working perfectly
   - ❌ Red X = Needs attention
   - 🟡 Yellow circle = Currently running

3. **Check Frequency**
   - Should see a new run every hour
   - Each run should complete in 1-3 minutes

### Detailed Health Check (2 minutes)

1. **Click on Latest Run** in Actions tab
2. **Click on "sync" job** to see details
3. **Look for:**
   - "fetched X submissions" 
   - "processed Y submissions"
   - "updated watermark"

4. **Check Airtable**
   - Open your Airtable base
   - Verify recent submissions are present
   - Check that data looks correct

> **💡 Having trouble?** See [Troubleshooting Section](USER_GUIDE.md#troubleshooting-common-issues) in the User Guide

---

## 🗂️ Repository Structure

```
airtable-jotform-sync/
├── .github/
│   └── workflows/
│       └── sync.yml                  # Automated sync schedule (hourly)
├── sync.py                           # Main synchronization script
├── setup_airtable_fields.py         # One-time field setup utility
├── watermark.json                    # Tracks last sync timestamp
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
├── USER_GUIDE.md                     # Non-technical user documentation
├── TECHNICAL_SETUP_GUIDE.md          # Technical documentation
├── GITHUB_ACCESS_GUIDE.md            # GitHub onboarding guide
├── VIDEO_RECORDING_SCRIPT.md         # Video tutorial scripts
└── QUICK_REFERENCE.md                # Quick reference cheat sheet
```

### Key Files Explained

| File | Purpose | Who Needs It |
|------|---------|--------------|
| `sync.py` | Main sync logic | Developers only |
| `watermark.json` | Last sync timestamp | System (auto-updated) |
| `.github/workflows/sync.yml` | Automation schedule | Technical staff |
| `USER_GUIDE.md` | How to use the tool | End users ⭐ |
| `TECHNICAL_SETUP_GUIDE.md` | Setup and architecture | Technical staff |
| `QUICK_REFERENCE.md` | Quick task guide | Everyone ⭐ |

---

## ⚙️ How It Works

### System Flow

```
┌─────────────┐
│   Jotform   │  ← People submit forms
│    Forms    │
└──────┬──────┘
       │
       │ (Every hour)
       ▼
┌─────────────┐
│   GitHub    │  ← Automated sync runs
│   Actions   │
└──────┬──────┘
       │
       │ (Fetches new data)
       ▼
┌─────────────┐
│  Airtable   │  ← Organized database
│    Base     │
└─────────────┘
```

### Sync Schedule

- **Automatic:** Every hour at :00 (e.g., 1:00 PM, 2:00 PM, 3:00 PM)
- **Manual:** Anytime via GitHub Actions "Run workflow" button
- **Duration:** Typically 1-3 minutes per run

### What Gets Synced

- ✅ New form submissions
- ✅ Updated submissions (if someone edits)
- ✅ All form fields (with some exceptions)
- ✅ File attachments (as URLs)
- ❌ Deleted submissions (not detected)

### Special Field Handling

- **Names** - Split into "First Name" and "Last Name"
- **Addresses** - Split into Street, City, State, Zip components
- **Phone Numbers** - Formatted consistently
- **Multi-Select Fields** - Preserved as arrays
- **Numeric Fields** - Converted to numbers

---

## 🔐 Security & Privacy

### Data Protection

- ✅ All API credentials stored securely in GitHub Secrets
- ✅ HTTPS encryption for all API calls
- ✅ No local data storage (except watermark timestamp)
- ✅ Read-only access to Jotform (never modifies submissions)

### Access Control

- 🔒 Repository access controlled via GitHub permissions
- 🔒 Airtable token scoped to specific base
- 🔒 Jotform API key for specific form only

### Compliance

**Note:** This system processes personal information (PII). Organizations must:
- Have legal basis for data processing (GDPR)
- Honor data subject rights (access, deletion, etc.)
- Maintain appropriate security measures
- Document data retention policies

> **⚠️ Important:** This tool does not automatically implement GDPR/CCPA compliance. Manual processes required for privacy requests.

---

## 🛠️ Technical Details

### Technology Stack

- **Language:** Python 3.11
- **Key Libraries:** `requests`, `python-dotenv`
- **APIs:** Jotform API v4, Airtable API v0
- **Orchestration:** GitHub Actions
- **State Management:** JSON watermark file

### Configuration

Required GitHub Secrets:
- `JOTFORM_API_KEY` - Jotform API authentication key
- `JOTFORM_FORM_ID` - ID of the form to sync
- `AIRTABLE_TOKEN` - Airtable Personal Access Token
- `AIRTABLE_BASE_ID` - ID of the Airtable base

### Running Locally

```bash
# Clone repository
git clone https://github.com/OluwaseyiFad/airtable-jotform-sync.git
cd airtable-jotform-sync

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with credentials
echo "JOTFORM_API_KEY=your_key" > .env
echo "JOTFORM_FORM_ID=your_id" >> .env
echo "AIRTABLE_TOKEN=your_token" >> .env
echo "AIRTABLE_BASE_ID=your_base_id" >> .env

# Run sync (dry run for testing)
python sync.py --dry-run

# Run actual sync
python sync.py
```

### Command-Line Options

```bash
python sync.py --help
python sync.py --dry-run           # Simulate without changes
python sync.py --ignore-watermark  # Process all submissions
python sync.py --skip-field-check  # Don't create new fields
```

---

## 📞 Contact & Support

### Getting Help

**For Day-to-Day Questions:**
- 📖 Check the [USER_GUIDE.md](USER_GUIDE.md)
- 📋 See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- 🔍 Review [Troubleshooting Section](USER_GUIDE.md#troubleshooting-common-issues)

**For Technical Issues:**
- 🔧 See [TECHNICAL_SETUP_GUIDE.md](TECHNICAL_SETUP_GUIDE.md)
- 🐛 Check GitHub Actions logs for error messages
- 💬 Open an issue in this repository

**For GitHub Access:**
- 👤 See [GITHUB_ACCESS_GUIDE.md](GITHUB_ACCESS_GUIDE.md)

### External Resources

- **Jotform Help:** https://www.jotform.com/help/
- **Airtable Support:** https://support.airtable.com/
- **GitHub Docs:** https://docs.github.com/

---

## 🤝 Contributing

Contributions welcome! If you'd like to improve this tool:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Test thoroughly
5. Submit a pull request

Please update documentation for any changes!

---

## 📜 License

This project is open source and available under the MIT License.

---

## 🙏 Acknowledgments

Created with ❤️ for non-profit organizations to streamline their volunteer management and data collection processes.

**Special Thanks:**
- Jotform for providing a robust forms platform
- Airtable for flexible database capabilities
- GitHub Actions for reliable automation

---

## 📊 Project Status

- ✅ **Active** - Maintained and in use
- ✅ **Stable** - Production-ready
- ✅ **Documented** - Comprehensive guides available
- 🎥 **Videos** - Coming soon!

**Last Updated:** February 2026  
**Version:** 1.0  
**Maintainer:** OluwaseyiFad

---

## 🎯 Next Steps

### New Users
1. ✅ Read the [USER_GUIDE.md](USER_GUIDE.md)
2. ✅ Bookmark this repository
3. ✅ Check the Actions tab to see sync in action

### Technical Staff
1. ✅ Review [TECHNICAL_SETUP_GUIDE.md](TECHNICAL_SETUP_GUIDE.md)
2. ✅ Verify all GitHub Secrets are configured
3. ✅ Test locally before deployment

### Video Production
1. ✅ Review [VIDEO_RECORDING_SCRIPT.md](VIDEO_RECORDING_SCRIPT.md)
2. ✅ Set up recording equipment
3. ✅ Record and publish tutorials

---

**Happy Syncing! 🎉**

*If you have questions or suggestions, please open an issue or reach out to the repository maintainer.*