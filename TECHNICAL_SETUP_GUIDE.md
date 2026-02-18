# 🔧 Technical Setup Guide: Jotform to Airtable Sync

**Version 1.0**  
**Last Updated: February 2026**

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [File Structure](#file-structure)
4. [The Watermark System](#the-watermark-system)
5. [Field Mappings and Type Conversions](#field-mappings-and-type-conversions)
6. [Configuration Details](#configuration-details)
7. [GitHub Secrets](#github-secrets)
8. [Special Field Handling](#special-field-handling)
9. [Type Conversion Table](#type-conversion-table)
10. [Running Locally](#running-locally)
11. [Troubleshooting Technical Issues](#troubleshooting-technical-issues)
12. [Security and Data Privacy](#security-and-data-privacy)
13. [Advanced Customization](#advanced-customization)
14. [Development Workflow](#development-workflow)

---

## 🌐 System Overview

### Purpose

This system provides **automated bidirectional field synchronization** and **unidirectional data synchronization** between Jotform and Airtable:

- **Data Flow:** Jotform (source) → Airtable (destination)
- **Field Creation:** Automatic creation of Airtable fields based on Jotform questions
- **Update Strategy:** Incremental updates using watermark-based change tracking
- **Execution Environment:** GitHub Actions with hourly cron schedule

### Key Features

✅ **Incremental Sync:** Only processes submissions updated since last sync  
✅ **Automatic Field Creation:** Creates missing Airtable fields dynamically  
✅ **Type Conversion:** Intelligently maps Jotform field types to Airtable types  
✅ **Composite Field Handling:** Splits complex fields (names, addresses) into components  
✅ **Error Tolerance:** Graceful error handling with detailed logging  
✅ **Idempotent Operations:** Safe to run multiple times without duplicating data

### Technology Stack

- **Language:** Python 3.11
- **Key Libraries:**
  - `requests` - HTTP client for API calls
  - `python-dotenv` - Environment variable management
- **APIs:**
  - Jotform API v4 (REST)
  - Airtable API v0 (REST + Meta API)
- **Orchestration:** GitHub Actions
- **State Management:** JSON watermark file

---

## 🏗️ Architecture

### System Flow Diagram

```
┌─────────────────┐
│   Jotform API   │
│  (Data Source)  │
└────────┬────────┘
         │
         │ HTTP GET
         │ (Every Hour)
         ▼
┌─────────────────────────┐
│  GitHub Actions Runner  │
│  ┌──────────────────┐   │
│  │   sync.py        │   │
│  │   - Fetch data   │   │
│  │   - Transform    │   │
│  │   - Load         │   │
│  └──────────────────┘   │
└────────┬────────────────┘
         │
         │ HTTP POST/PATCH
         │
         ▼
┌─────────────────┐
│  Airtable API   │
│ (Destination DB) │
└─────────────────┘
         │
         │ Commit
         ▼
┌─────────────────┐
│ watermark.json  │
│ (State Tracker) │
└─────────────────┘
```

### Execution Phases

#### 1. **Pre-Sync Phase**
- Load watermark (last sync timestamp)
- Validate environment variables
- Check field schema synchronization

#### 2. **Field Synchronization Phase**
- Fetch Jotform form questions
- Fetch Airtable table schema
- Create missing Airtable fields
- Identify orphaned fields (optional cleanup)

#### 3. **Data Synchronization Phase**
- Fetch all submissions from Jotform
- Filter submissions updated since watermark
- Transform data (field mapping, type conversion)
- Upsert to Airtable (create or update records)

#### 4. **Post-Sync Phase**
- Update watermark with newest submission timestamp
- Commit watermark.json to repository
- Log summary statistics

---

## 📁 File Structure

```
airtable-jotform-sync/
├── .github/
│   └── workflows/
│       └── sync.yml              # GitHub Actions workflow configuration
├── sync.py                        # Main synchronization script
├── setup_airtable_fields.py      # One-time field setup utility
├── watermark.json                 # Sync state tracking file
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore patterns
├── README.md                      # Project overview
├── USER_GUIDE.md                  # Non-technical user documentation
├── TECHNICAL_SETUP_GUIDE.md       # This file
├── GITHUB_ACCESS_GUIDE.md         # GitHub onboarding guide
├── VIDEO_RECORDING_SCRIPT.md      # Video tutorial scripts
└── QUICK_REFERENCE.md             # Quick reference cheat sheet
```

### Key Files Explained

#### `sync.py` (Main Script)

**Purpose:** Core synchronization logic  
**Lines of Code:** ~719  
**Key Functions:**

- `fetch_all_submissions()` - Retrieves all Jotform submissions with pagination
- `upsert_to_airtable()` - Creates or updates Airtable records
- `auto_create_missing_fields()` - Dynamically creates new Airtable fields
- `convert_value_for_airtable()` - Type conversion logic
- `load_watermark()` / `save_watermark()` - State management

**Entry Point:** `main()` function with CLI argument support

#### `setup_airtable_fields.py` (Setup Utility)

**Purpose:** One-time bulk field creation  
**Lines of Code:** ~142  
**Usage:** Run once during initial setup to create all Airtable fields

**When to Use:**
- First-time setup
- After deleting Airtable table
- When many fields are missing

**Command:**
```bash
python setup_airtable_fields.py
```

#### `watermark.json` (State File)

**Purpose:** Tracks last successful sync timestamp  
**Format:**
```json
{
  "last_updated_at": 1739011200
}
```

**Timestamp Format:** Unix epoch time (seconds since January 1, 1970 UTC)

**Why It Matters:**
- Enables incremental syncing (only new/updated submissions)
- Prevents redundant processing
- Reduces API calls and execution time
- Acts as a checkpoint for recovery

**Lifecycle:**
1. Read at sync start
2. Updated with newest submission timestamp
3. Committed to Git after successful sync

#### `.github/workflows/sync.yml` (CI/CD Configuration)

**Purpose:** Automates sync execution via GitHub Actions

**Key Configuration:**

```yaml
on:
  schedule:
    - cron: '0 * * * *'  # Every hour at minute 0
  workflow_dispatch:      # Manual trigger enabled
```

**Jobs:**
1. Checkout repository
2. Setup Python 3.11
3. Install dependencies
4. Run sync.py with environment variables
5. Commit and push watermark.json

---

## ⏰ The Watermark System

### Concept

The watermark system implements **incremental synchronization** by tracking the timestamp of the most recently processed submission.

### How It Works

#### Initial State (First Run)
```python
watermark = 0  # Process all submissions
```

#### Subsequent Runs
```python
watermark = 1739011200  # Only process submissions after this timestamp
```

### Implementation Details

#### Loading Watermark
```python
def load_watermark() -> int:
    if not os.path.exists(WATERMARK_FILE):
        return 0  # No previous sync
    with open(WATERMARK_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return int(data.get("last_updated_at", 0))
```

#### Saving Watermark
```python
def save_watermark(ts: int) -> None:
    with open(WATERMARK_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_updated_at": int(ts)}, f)
```

#### Filtering Submissions
```python
last_watermark = load_watermark()
newest_seen = last_watermark

for submission in submissions:
    updated_at = parse_timestamp(
        submission.get("updated_at") or submission.get("created_at")
    )
    
    if updated_at <= last_watermark:
        continue  # Skip already processed
    
    upsert_to_airtable(submission)
    
    if updated_at > newest_seen:
        newest_seen = updated_at

save_watermark(newest_seen)
```

### Edge Cases Handled

1. **Missing Watermark File:** Defaults to 0 (process all)
2. **Concurrent Updates:** Uses `updated_at` field to detect changes
3. **Timestamp Parsing:** Handles multiple formats (int, string, datetime)
4. **Git Conflicts:** Uses `git pull --rebase` before push

### Advantages

✅ **Efficiency:** Only processes new/changed data  
✅ **Reliability:** Can resume after interruption  
✅ **Scalability:** Performance doesn't degrade as data grows  
✅ **Auditability:** Provides checkpoint for troubleshooting

### Limitations

⚠️ **Clock Skew:** Relies on accurate timestamps from Jotform  
⚠️ **Deletion Detection:** Cannot detect deleted submissions  
⚠️ **Backfill:** Use `--ignore-watermark` flag to reprocess all data

---

## 🗂️ Field Mappings and Type Conversions

### Composite Fields

Complex Jotform fields are automatically split into multiple Airtable columns.

#### Name Field

**Jotform Field:** `name` (full name input)

**Maps To:**
```python
{
    "first": "Name (First)",
    "last": "Name (Last)"
}
```

**Example:**
- Input: `{"first": "John", "last": "Doe"}`
- Output: Two separate Airtable columns

#### Home Address Field

**Jotform Field:** `homeAddress`

**Maps To:**
```python
{
    "addr_line1": "Home Address (Street)",
    "addr_line2": "Home Address (Street Line 2)",
    "city": "Home Address (City)",
    "state": "Home Address (State/Province)",
    "postal": "Home Address (Postal/Zip Code)"
}
```

**Note:** `state` subfield is in `SKIP_FIELDS` - not synced to avoid redundancy

#### Business Address Field

**Jotform Field:** `businessAddress15`

**Maps To:**
```python
{
    "addr_line1": "Business Address (Street Address)",
    "addr_line2": "Business Address (Street Address Line 2)",
    "city": "Business Address (City)",
    "state": "Business Address (State)",
    "postal": "Business Address (Zip Code)"
}
```

#### Phone Number Fields

**Personal Phone:**
```python
{
    "full": "Personal Phone Number"
}
```

**Business Phone:**
```python
{
    "area": "Business Phone Number (Area Code)",  # Skipped
    "full": "Business Phone Number"
}
```

**Rationale:** Area code is skipped when full number is available

### Special Field Categories

#### Numeric Fields

Fields that should be stored as numbers in Airtable:

```python
NUMERIC_FIELDS = ["Top 10 Class"]
```

**Conversion:** String → Integer or Float

#### Multi-Select Fields

Fields that support multiple selections:

```python
MULTI_SELECT_FIELDS = [
    "Are you interested in volunteering in one of the vocations below?",
    "Fields of Interest"
]
```

**Storage:** Array of strings in Airtable  
**Note:** These fields are also in `SKIP_FIELDS` to prevent data duplication

#### Skip Fields

Fields explicitly excluded from synchronization:

```python
SKIP_FIELDS = [
    "Are you interested in volunteering in one of the vocations below?",
    "Fields of Interest",
    "Business Phone Number (Area Code)",
    "Business Address (State)",
    "Home Address (State/Province)"
]
```

**Reasons for Skipping:**
- Redundant data (area code included in full phone number)
- State fields handled differently
- Data complexity issues

#### Vocation Fields

Special fields with value normalization:

```python
VOCATION_FIELDS = [
    "1. Public Health/Hospitals",
    "2. Public Service",
    "3. Finance/Banking/Insurance",
    "4. Government",
    "5. Transportation (i.e. RTA)",
    "6. Engineering",
    "7. IT Technology",
    "8. Social Service",
    "9. Non Profit",
    "10. Public Safety",
    "11. Civil Rights Activist",
    "12. Mentoring",
    "13. Equity",
    "14. Human Resources"
]

VOCATION_VALUE_MAP = {
    "0-2 years": "0-2 Years",
    "> 10 years": "> 10 Years"
}
```

**Purpose:** Normalizes experience level values for consistency

---

## 🔄 Type Conversion Table

### Jotform to Airtable Field Type Mapping

| Jotform Type | Airtable Type | Options | Notes |
|--------------|---------------|---------|-------|
| `control_textbox` | `singleLineText` | - | Plain text input |
| `control_textarea` | `multilineText` | - | Long text input |
| `control_email` | `email` | - | Validated email format |
| `control_phone` | `phoneNumber` | - | Phone number validation |
| `control_number` | `number` | `precision: 0` | Integer or float |
| `control_dropdown` | `singleSelect` | `choices` array | Single choice from list |
| `control_radio` | `singleSelect` | `choices` array | Radio button selection |
| `control_checkbox` | `multipleSelects` | `choices` array | Multiple selections allowed |
| `control_fileupload` | `multipleAttachments` | - | File URLs → Attachments |
| `control_datetime` | `date` | - | ISO 8601 date format |
| `control_fullname` | `singleLineText` | - | Composite field (split) |
| `control_address` | `multilineText` | - | Composite field (split) |

### Value Conversion Logic

#### String → Number

```python
def convert_to_number(value):
    try:
        if '.' not in str(value):
            return int(value)
        return float(value)
    except (ValueError, TypeError):
        return None
```

**Handles:**
- Integer strings: `"42"` → `42`
- Float strings: `"3.14"` → `3.14`
- Invalid values: Returns `None`

#### String → Array (Multi-Select)

```python
def convert_to_array(value):
    if isinstance(value, list):
        return [str(v).strip() for v in value if v]
    elif isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    return None
```

**Handles:**
- Already array: Validates and cleans
- Comma-separated string: Splits into array
- Preserves items with commas within list values

#### String → Date

```python
def convert_to_date(value):
    try:
        dt = datetime.strptime(value.split()[0], "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except (ValueError, IndexError):
        return None
```

**Expected Format:** `YYYY-MM-DD` (ISO 8601)

#### URL → Attachment

```python
def to_airtable_attachments(file_urls):
    attachments = []
    for url in file_urls:
        filename = url.split("/")[-1].split("?")[0] or "file"
        attachments.append({"url": url, "filename": filename})
    return attachments
```

**Input:** List of file URLs  
**Output:** Array of Airtable attachment objects

---

## ⚙️ Configuration Details

### Environment Variables

Required for both local and GitHub Actions execution:

```bash
# Jotform Configuration
JOTFORM_API_KEY=<your_jotform_api_key>
JOTFORM_FORM_ID=<your_form_id>

# Airtable Configuration
AIRTABLE_TOKEN=<your_airtable_personal_access_token>
AIRTABLE_BASE_ID=<your_base_id>

# Optional: Custom API Base URL
JOTFORM_BASE=https://parityinc.jotform.com/API  # Default if not set
```

### Hardcoded Configuration

#### Airtable Table Name

```python
AIRTABLE_TABLE = "Table 1"
```

**To Change:** Edit `sync.py` line 17

#### Submission ID Field

```python
SUBMISSION_ID_FIELD = "Submission ID"
```

**Purpose:** Unique identifier for deduplication  
**Must Exist:** Created automatically if missing

### GitHub Actions Configuration

#### Cron Schedule

```yaml
on:
  schedule:
    - cron: '0 * * * *'
```

**Current:** Every hour at minute 0 (e.g., 1:00, 2:00, 3:00)

**To Modify:**
- Edit `.github/workflows/sync.yml`
- Cron syntax: `minute hour day month weekday`
- Examples:
  - Every 30 minutes: `*/30 * * * *`
  - Every 6 hours: `0 */6 * * *`
  - Daily at 2am: `0 2 * * *`

#### Manual Trigger

```yaml
workflow_dispatch:
```

**Enables:** "Run workflow" button in GitHub Actions UI

### API Rate Limits

#### Jotform API

- **Rate Limit:** 100 requests per minute
- **Mitigation:** Single request fetches all submissions with pagination
- **Timeout:** 30 seconds per request

#### Airtable API

- **Rate Limit:** 5 requests per second per base
- **Mitigation:** 250ms delay between upsert operations
- **Timeout:** 30 seconds per request

```python
time.sleep(0.25)  # 250ms delay = 4 requests/second
```

---

## 🔐 GitHub Secrets

GitHub Secrets store sensitive credentials securely. They are encrypted and only exposed to GitHub Actions during workflow execution.

### Required Secrets

#### 1. `JOTFORM_API_KEY`

**What:** Jotform API authentication key  
**Where to Find:**
1. Log in to Jotform
2. Go to "My Account" → "API" section
3. Click "Create New Key"
4. Copy the generated key

**Format:** 40-character hexadecimal string  
**Example:** `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0`

#### 2. `JOTFORM_FORM_ID`

**What:** Unique identifier for your Jotform form  
**Where to Find:**
1. Open your form in Jotform
2. Look at the URL: `https://www.jotform.com/build/231234567890123`
3. The form ID is the number: `231234567890123`

**Format:** 15-digit number (typically)  
**Example:** `231234567890123`

#### 3. `AIRTABLE_TOKEN`

**What:** Airtable Personal Access Token (PAT)  
**Where to Find:**
1. Log in to Airtable
2. Go to "Account" → "Developer hub"
3. Click "Personal access tokens"
4. Click "Create new token"
5. Grant scopes: `data.records:read`, `data.records:write`, `schema.bases:read`, `schema.bases:write`
6. Add the specific base to the token
7. Click "Create token"
8. Copy the token (shown only once!)

**Format:** `pat` prefix + base64-encoded string  
**Example:** `patAbCdEfGhIjKlMnOpQrStUvWxYz.1234567890abcdefghijklmnopqrstuvwxyz`

**⚠️ Security Note:** This token has broad access. Never commit it to Git or share it publicly.

#### 4. `AIRTABLE_BASE_ID`

**What:** Unique identifier for your Airtable base  
**Where to Find:**
1. Open your base in Airtable
2. Look at the URL: `https://airtable.com/appAbCdEfGhIjKlMn/tblXyZ123456`
3. The base ID starts with `app`: `appAbCdEfGhIjKlMn`

**Format:** `app` prefix + 14-character alphanumeric string  
**Example:** `appAbCdEfGhIjKlMn`

### Setting Secrets in GitHub

#### Via Web UI:

1. Navigate to your repository on GitHub
2. Click **Settings** tab
3. Click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Enter **Name** (e.g., `JOTFORM_API_KEY`)
6. Enter **Value** (the actual secret)
7. Click **Add secret**
8. Repeat for each secret

#### Via GitHub CLI:

```bash
gh secret set JOTFORM_API_KEY
# Paste the value when prompted

gh secret set JOTFORM_FORM_ID
gh secret set AIRTABLE_TOKEN
gh secret set AIRTABLE_BASE_ID
```

### Verifying Secrets

Secrets cannot be viewed after creation, but you can verify they exist:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. You should see all four secrets listed
3. To test, run the workflow manually
4. Check the logs for authentication errors

### Rotating Secrets

**When to Rotate:**
- Suspected compromise
- Team member with access leaves
- Every 90 days (best practice)

**How to Rotate:**
1. Generate new credential in source system (Jotform/Airtable)
2. Update the secret in GitHub
3. Delete old credential in source system

---

## 🎯 Special Field Handling

### File Upload Fields

Jotform file uploads return URLs. The sync converts these to Airtable attachment objects.

#### Extraction Logic

```python
def extract_urls_from_one_answer(answer_obj):
    found = []
    if isinstance(answer_obj, dict):
        for k in ["answer", "prettyFormat", "value"]:
            v = answer_obj.get(k)
            found.extend(extract_urls_from_one_answer(v))
    elif isinstance(answer_obj, list):
        for item in answer_obj:
            found.extend(extract_urls_from_one_answer(item))
    elif isinstance(answer_obj, str):
        parts = [p.strip() for p in answer_obj.replace("\n", ",").split(",")]
        for p in parts:
            if p.startswith(("http://", "https://")):
                found.append(p)
    return found
```

**Recursively searches for URLs in:**
- Dictionary values
- List items
- Comma/newline-separated strings

#### Conversion to Attachments

```python
def to_airtable_attachments(file_urls):
    attachments = []
    for url in file_urls:
        filename = url.split("/")[-1].split("?")[0] or "file"
        attachments.append({"url": url, "filename": filename})
    return attachments
```

**Output Format:**
```json
[
  {
    "url": "https://www.jotform.com/uploads/file123.pdf",
    "filename": "file123.pdf"
  }
]
```

### Checkbox Fields (Multi-Select)

Checkbox fields preserve array structure to handle values containing commas.

#### Problem:

If a checkbox option is `"Red, Blue"` (contains comma), splitting by comma would break it into two options.

#### Solution:

```python
if qtype == "control_checkbox":
    if isinstance(answer_obj, dict):
        val = answer_obj.get("prettyFormat") or answer_obj.get("answer")
        if isinstance(val, list):
            return [str(v) for v in val if v]  # Keep as array
        elif isinstance(val, str):
            return [val] if val else None
        return val
    if isinstance(answer_obj, list):
        return [str(v) for v in answer_obj if v]  # Keep as array
    return answer_obj
```

**Preserves:** Original array structure from Jotform

### Composite Fields Implementation

#### Name Field Extraction

```python
def extract_composite_fields(field_name, answer_obj):
    result = {}
    if field_name not in COMPOSITE_FIELDS:
        return result
    
    mapping = COMPOSITE_FIELDS[field_name]
    answer = answer_obj.get("answer", {})
    
    for jotform_key, airtable_field in mapping.items():
        value = answer.get(jotform_key, "")
        if value:  # Only include non-empty values
            result[airtable_field] = str(value)
    
    return result
```

**Example Input:**
```json
{
  "name": {
    "answer": {
      "first": "Jane",
      "last": "Smith"
    }
  }
}
```

**Example Output:**
```python
{
  "Name (First)": "Jane",
  "Name (Last)": "Smith"
}
```

### Dynamic Field Creation

When a new question is added to Jotform, the system automatically creates the corresponding Airtable field.

#### Field Detection

```python
def auto_create_missing_fields():
    jf_questions = get_jotform_questions()
    table_id, at_fields = get_airtable_schema()
    
    new_fields = []
    
    for jf_name, jf_info in jf_fields.items():
        at_field_name = jf_info["text"]
        if at_field_name not in at_fields:
            at_type = determine_airtable_type(jf_info)
            new_fields.append({
                "at_name": at_field_name,
                "at_type": at_type,
                "options": jf_info.get("options")
            })
    
    # Create all new fields
    for field in new_fields:
        create_airtable_field(table_id, field['at_name'], field['at_type'])
```

#### Type Determination

```python
if at_field_name in NUMERIC_FIELDS:
    at_type = "number"
elif at_field_name in MULTI_SELECT_FIELDS:
    at_type = "multipleSelects"
elif at_field_name in VOCATION_FIELDS:
    at_type = "singleLineText"
else:
    at_type = JOTFORM_TO_AIRTABLE_TYPES.get(jf_info["type"], "singleLineText")
```

#### Options Handling

For `singleSelect` and `multipleSelects` fields:

```python
def parse_jotform_dropdown_options(options_str):
    if not options_str:
        return None
    choices = [
        {"name": opt.strip()}
        for opt in options_str.split("|")
        if opt.strip()
    ]
    return {"choices": choices} if choices else None
```

**Jotform Format:** `"Option 1|Option 2|Option 3"`  
**Airtable Format:** `{"choices": [{"name": "Option 1"}, {"name": "Option 2"}]}`

### Field Visibility Limitation

**Airtable API Limitation:** Fields created via API are automatically hidden.

**Workaround:** Users must manually unhide fields in the Airtable UI.

**Why Can't We Auto-Unhide?**
- Airtable Meta API does not expose field visibility settings
- No API endpoint to modify field visibility
- This is a known limitation of Airtable's API

**User Impact:** Documented in USER_GUIDE.md with step-by-step instructions

---

## 🧪 Running Locally

### Prerequisites

- Python 3.11 or higher
- Git
- Access to Jotform and Airtable APIs

### Setup Instructions

#### 1. Clone Repository

```bash
git clone https://github.com/OluwaseyiFad/airtable-jotform-sync.git
cd airtable-jotform-sync
```

#### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Contents of requirements.txt:**
```
requests
python-dotenv
```

#### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# .env
JOTFORM_API_KEY=your_api_key_here
JOTFORM_FORM_ID=your_form_id_here
AIRTABLE_TOKEN=your_token_here
AIRTABLE_BASE_ID=your_base_id_here
```

**⚠️ Security:** Never commit `.env` to Git! It should be in `.gitignore`.

#### 5. Run Sync Script

**Full Sync (ignore watermark):**
```bash
python sync.py --ignore-watermark
```

**Incremental Sync (normal operation):**
```bash
python sync.py
```

**Dry Run (no changes):**
```bash
python sync.py --dry-run
```

**Run once (don't loop):**
```bash
python sync.py --once
```

**Skip field creation:**
```bash
python sync.py --skip-field-check
```

### Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--once` | Run once and exit | Loop mode |
| `--dry-run` | Simulate without making changes | False |
| `--ignore-watermark` | Process all submissions | Use watermark |
| `--skip-field-check` | Don't create new fields | Check fields |
| `--skip-field-deletion` | Don't check for orphaned fields | Check for orphans |

### Testing Field Creation

Run the setup script to bulk-create all missing fields:

```bash
python setup_airtable_fields.py
```

**Output:**
```
Fetching Jotform form questions...
Found 42 questions in Jotform.

Fetching existing Airtable fields...
Found 38 existing fields in Airtable.

Creating 4 new fields in Airtable...

  Creating: New Question Field (Jotform type: control_textbox)
  [OK] Created field: New Question Field

Done!
```

### Debugging Tips

#### Enable Verbose Logging

Modify `sync.py` to add debug prints:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Inspect API Responses

```python
response = requests.get(url, params=params)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

#### Check Watermark State

```bash
cat watermark.json
python -c "import json; print(json.load(open('watermark.json')))"
```

#### Validate Environment Variables

```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('JOTFORM_API_KEY'))"
```

---

## 🔍 Troubleshooting Technical Issues

### Issue: "Missing required config"

**Symptom:** Script exits immediately with error message

**Cause:** One or more required environment variables not set

**Solution:**

```bash
# Check environment variables
echo $JOTFORM_API_KEY
echo $JOTFORM_FORM_ID
echo $AIRTABLE_TOKEN
echo $AIRTABLE_BASE_ID

# If using .env file, verify it's loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('JOTFORM_API_KEY'))"
```

### Issue: "INVALID_VALUE_FOR_COLUMN"

**Symptom:** Airtable returns error when creating/updating record

**Cause:** Data type mismatch between value and column type

**Debug Steps:**

1. Check the error message for field name
2. Inspect the column type in Airtable
3. Check the value being sent

**Fix:**

```python
# Add to NUMERIC_FIELDS if should be number
NUMERIC_FIELDS = ["Top 10 Class", "Your Field Name"]

# Or add to MULTI_SELECT_FIELDS if should be array
MULTI_SELECT_FIELDS = ["Your Field Name"]
```

### Issue: "INVALID_MULTIPLE_CHOICE_OPTIONS"

**Symptom:** Cannot create/update singleSelect or multipleSelects field

**Cause:** Value not in the predefined choices list

**Solutions:**

1. **Add option to Airtable manually** (preferred)
2. **Change field type to singleLineText** (loses validation)
3. **Update sync logic** to handle dynamic options

### Issue: Rate Limit Exceeded

**Jotform Error:** `429 Too Many Requests`

**Solution:**
```python
# Increase delay between requests
time.sleep(1)  # Wait 1 second instead of 0.25
```

**Airtable Error:** `429 Too Many Requests`

**Solution:**
```python
# Increase delay in upsert_to_airtable()
time.sleep(0.5)  # Wait 500ms instead of 250ms
```

### Issue: Duplicate Records Created

**Symptom:** Same submission appears multiple times in Airtable

**Cause:** `find_record_by_submission_id()` not finding existing record

**Debug:**

```python
# Check if Submission ID field exists and is populated
submission_id = "12345"
record_id = find_record_by_submission_id(submission_id)
print(f"Found record: {record_id}")
```

**Fix:**

1. Verify "Submission ID" field exists in Airtable
2. Check field name matches `SUBMISSION_ID_FIELD` constant
3. Ensure field is not hidden

### Issue: Fields Not Creating Automatically

**Symptom:** New Jotform questions don't create Airtable columns

**Cause:** Field creation logic failing silently

**Debug:**

```bash
# Run with field creation enabled
python sync.py

# Check output for "created field: ..." messages
```

**Check:**
- Airtable token has `schema.bases:write` permission
- Table ID is correctly identified
- Field name doesn't contain invalid characters

### Issue: Watermark Not Updating

**Symptom:** Script processes same submissions repeatedly

**Cause:** Git commit failing or watermark.json not writable

**Debug:**

```bash
# Check file permissions
ls -la watermark.json

# Check Git status
git status
git diff watermark.json
```

**Fix:**

```bash
# Reset Git state if needed
git checkout watermark.json
git pull

# Run sync again
python sync.py
```

### Issue: Timeout Errors

**Symptom:** `requests.exceptions.Timeout`

**Cause:** API response taking too long (>30 seconds)

**Solutions:**

1. **Increase timeout:**
```python
r = requests.get(url, timeout=60)  # 60 seconds
```

2. **Reduce batch size:**
```python
limit = 50  # Instead of 100
```

3. **Check network connectivity**

---

## 🔒 Security and Data Privacy

### Threat Model

#### Assets to Protect:

1. **API Credentials** - Unauthorized access could lead to data breaches
2. **Form Submission Data** - Contains PII (Personally Identifiable Information)
3. **Airtable Database** - Central storage of sensitive information
4. **GitHub Repository** - Source code and configuration

#### Threats:

- **Credential Leakage:** Secrets committed to Git or exposed in logs
- **Man-in-the-Middle:** API requests intercepted
- **Unauthorized Access:** Stolen tokens used to access data
- **Data Tampering:** Malicious modification of submissions
- **Denial of Service:** Rate limit exhaustion

### Security Measures Implemented

#### 1. Secret Management

✅ **GitHub Secrets:** All credentials stored encrypted  
✅ **Environment Variables:** Not hardcoded in source  
✅ **.gitignore:** Prevents `.env` file from being committed

#### 2. API Security

✅ **HTTPS Only:** All API calls use TLS encryption  
✅ **Token-Based Auth:** No username/password transmission  
✅ **Timeout Limits:** Prevents hanging connections  
✅ **Error Handling:** Sensitive data not logged in error messages

#### 3. Data Handling

✅ **Read-Only Source:** Never modifies Jotform submissions  
✅ **Idempotent Updates:** Safe to run multiple times  
✅ **No Local Storage:** Data not persisted locally (except watermark)

#### 4. Access Control

✅ **Minimal Permissions:** Airtable token scoped to specific base  
✅ **GitHub Actions Only:** Credentials not accessible outside workflows  
✅ **Repository Permissions:** Only authorized users can modify code

### Best Practices

#### For Repository Maintainers:

1. **Rotate Secrets Regularly**
   - Every 90 days minimum
   - Immediately if compromise suspected

2. **Review Access Logs**
   - Monitor GitHub Actions runs
   - Check Airtable audit log
   - Review Jotform API usage

3. **Keep Dependencies Updated**
   ```bash
   pip list --outdated
   pip install --upgrade requests python-dotenv
   ```

4. **Code Review**
   - All changes reviewed before merge
   - Look for hardcoded credentials
   - Validate input handling

#### For End Users:

1. **Strong Passwords**
   - Use unique password for GitHub
   - Use password manager

2. **Enable 2FA**
   - GitHub two-factor authentication
   - Airtable 2FA
   - Jotform 2FA

3. **Monitor Activity**
   - Review GitHub notifications
   - Check Airtable activity log
   - Monitor form submissions

### Data Privacy Considerations

#### PII Handling:

The system processes sensitive personal information:
- Names
- Email addresses
- Phone numbers
- Home addresses
- Work addresses

#### Compliance Notes:

**GDPR (EU):**
- Data processing must have legal basis
- Data subject rights must be respected (access, deletion, etc.)
- Data minimization principle applies

**CCPA (California):**
- California residents have right to know what data is collected
- Right to deletion must be honored

**Implementation:**
- **Deletion:** Manual process (delete from Jotform and Airtable)
- **Access:** Export functionality in both Jotform and Airtable
- **Retention:** No automatic data retention policies implemented

**⚠️ Important:** This system does not implement automatic GDPR/CCPA compliance. The organization must handle privacy requests manually.

### Incident Response

#### If Credentials Are Compromised:

1. **Immediately Revoke:**
   - Jotform API key
   - Airtable personal access token

2. **Generate New Credentials:**
   - Create new API key in Jotform
   - Create new PAT in Airtable

3. **Update GitHub Secrets:**
   - Replace compromised secrets
   - Verify update in Actions run

4. **Audit Access:**
   - Check Airtable activity log for unauthorized access
   - Review Jotform API usage logs
   - Check for unexpected data modifications

5. **Notify Stakeholders:**
   - Inform affected users if data accessed
   - Document incident for compliance

---

## 🎨 Advanced Customization

### Changing the Sync Schedule

Edit `.github/workflows/sync.yml`:

```yaml
on:
  schedule:
    - cron: '0 */2 * * *'  # Every 2 hours
```

**Common Schedules:**

- Every 15 minutes: `*/15 * * * *`
- Every 30 minutes: `*/30 * * * *`
- Every 2 hours: `0 */2 * * *`
- Every 6 hours: `0 */6 * * *`
- Daily at 2am: `0 2 * * *`
- Weekdays at 9am: `0 9 * * 1-5`

**⚠️ Note:** More frequent syncs = more API calls = higher rate limit risk

### Adding Custom Field Transformations

Example: Convert state abbreviations to full names

```python
STATE_MAP = {
    "CA": "California",
    "NY": "New York",
    "TX": "Texas",
    # ... add more states
}

def convert_value_for_airtable(value, at_field_type, at_field_info, field_name):
    # ... existing code ...
    
    # Custom transformation for state fields
    if field_name == "State":
        if value in STATE_MAP:
            return STATE_MAP[value]
    
    return str(value) if value else None
```

### Adding New Composite Fields

Example: Add a custom composite field for "Emergency Contact"

```python
COMPOSITE_FIELDS = {
    # ... existing fields ...
    
    "emergencyContact": {
        "name": "Emergency Contact Name",
        "phone": "Emergency Contact Phone",
        "relationship": "Emergency Contact Relationship"
    }
}
```

### Custom Validation

Add data validation before Airtable insert:

```python
def validate_submission(fields):
    """Validate submission data before syncing."""
    errors = []
    
    # Email validation
    if "Email" in fields:
        email = fields["Email"]
        if "@" not in email:
            errors.append(f"Invalid email: {email}")
    
    # Phone validation
    if "Personal Phone Number" in fields:
        phone = fields["Personal Phone Number"]
        if len(phone.replace("-", "").replace("(", "").replace(")", "")) < 10:
            errors.append(f"Invalid phone: {phone}")
    
    return errors

# In upsert_to_airtable():
validation_errors = validate_submission(filtered_fields)
if validation_errors:
    print(f"Validation errors for {submission_id}: {validation_errors}")
    return  # Skip this submission
```

### Multiple Form Support

To sync multiple forms to different tables:

**Option 1: Multiple Workflows**

Create separate workflow files:
- `.github/workflows/sync-form1.yml`
- `.github/workflows/sync-form2.yml`

Each with different environment variables.

**Option 2: Configuration File**

Create `config.json`:
```json
{
  "forms": [
    {
      "jotform_id": "123456789",
      "airtable_base": "appXYZ",
      "airtable_table": "Form 1 Responses"
    },
    {
      "jotform_id": "987654321",
      "airtable_base": "appABC",
      "airtable_table": "Form 2 Responses"
    }
  ]
}
```

Modify `sync.py` to loop through forms.

### Notification Integration

Add Slack/Email notifications on sync completion:

```python
import requests

def send_slack_notification(message):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return
    
    payload = {"text": message}
    requests.post(webhook_url, json=payload)

# In main():
send_slack_notification(f"Sync completed: {processed} submissions processed")
```

### Data Export to CSV

Add CSV export functionality:

```python
import csv

def export_to_csv(submissions, filename="export.csv"):
    if not submissions:
        return
    
    keys = submissions[0].keys()
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(submissions)
    
    print(f"Exported {len(submissions)} submissions to {filename}")
```

---

## 🔧 Development Workflow

### Local Development Setup

```bash
# Create feature branch
git checkout -b feature/my-new-feature

# Make changes
# ... edit files ...

# Run tests
python sync.py --dry-run --ignore-watermark

# Commit changes
git add .
git commit -m "Add my new feature"

# Push to GitHub
git push origin feature/my-new-feature

# Create Pull Request on GitHub
```

### Testing Changes

#### 1. Dry Run

```bash
python sync.py --dry-run --ignore-watermark
```

**Purpose:** Simulate sync without making changes

#### 2. Limited Run

```bash
python sync.py --once
```

**Purpose:** Run once and exit (no loop)

#### 3. Test with Specific Submissions

Modify `sync.py` temporarily:

```python
# In main(), before processing:
submissions = [s for s in submissions if s['id'] == '12345']  # Test one submission
```

#### 4. Test Field Creation

```bash
python setup_airtable_fields.py
```

**Purpose:** Verify field creation logic

### Code Style

**Follow PEP 8:**
```bash
pip install flake8
flake8 sync.py
```

**Type Hints:**
```python
def my_function(param: str) -> int:
    return len(param)
```

**Docstrings:**
```python
def my_function(param):
    """
    Brief description.
    
    Args:
        param (str): Description of parameter.
    
    Returns:
        int: Description of return value.
    """
    return len(param)
```

### Version Control Best Practices

**Commit Messages:**
```
Add feature to handle X
Fix bug in Y conversion
Update documentation for Z
Refactor field mapping logic
```

**Branch Naming:**
- Feature: `feature/description`
- Bugfix: `fix/description`
- Documentation: `docs/description`

**Pull Requests:**
- Clear title
- Description of changes
- Link to related issues
- Screenshots if UI changes

### Deployment

**To Production:**

1. Merge PR to `main` branch
2. GitHub Actions automatically runs sync
3. Monitor first few runs for errors
4. Check Airtable for expected data

**Rollback:**

```bash
git revert <commit-hash>
git push origin main
```

---

## 📊 Performance Optimization

### Current Performance

**Typical Execution Time:**
- 50 submissions: ~30 seconds
- 100 submissions: ~1 minute
- 500 submissions: ~3 minutes

**Bottlenecks:**
1. API rate limits (250ms delay per upsert)
2. Network latency
3. Sequential processing

### Optimization Opportunities

#### 1. Batch Operations

Airtable supports batch create/update (up to 10 records):

```python
def batch_upsert_to_airtable(submissions_batch):
    records = []
    for submission in submissions_batch:
        fields = transform_submission(submission)
        records.append({"fields": fields})
    
    payload = {"records": records}
    response = airtable_post_batch(payload)
    return response
```

**Benefit:** 10x reduction in API calls

#### 2. Parallel Processing

Use `concurrent.futures` for parallel API calls:

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(upsert_to_airtable, sub) for sub in submissions]
    results = [f.result() for f in futures]
```

**⚠️ Caution:** Respect rate limits

#### 3. Caching

Cache Airtable schema:

```python
SCHEMA_CACHE_DURATION = 300  # 5 minutes
schema_cache_time = 0

def get_airtable_schema_cached():
    global schema_cache_time, AIRTABLE_SCHEMA_CACHE
    
    now = time.time()
    if now - schema_cache_time < SCHEMA_CACHE_DURATION:
        return AIRTABLE_SCHEMA_CACHE
    
    schema = get_airtable_schema()
    AIRTABLE_SCHEMA_CACHE = schema
    schema_cache_time = now
    return schema
```

#### 4. Delta Sync Optimization

Only fetch submissions updated since watermark:

**⚠️ Note:** Jotform API doesn't support filtering by `updated_at` in query parameters. Current implementation fetches all and filters locally.

**Potential:** If Jotform adds filter support, reduce data transfer significantly.

---

## 📈 Monitoring and Logging

### GitHub Actions Logs

**Access:**
1. Repository → Actions tab
2. Click on workflow run
3. Click on "sync" job
4. View detailed logs

**What to Monitor:**
- Green checkmarks = success
- Red X = failure
- Execution time
- Number of submissions processed

### Log Analysis

**Successful Run Example:**
```
Fetching submissions...
fetched 42 submissions
created field: New Field Name
processed 5 submissions
updated watermark
```

**Failed Run Example:**
```
Fetching submissions...
fetched 42 submissions
Error creating 12345: INVALID_VALUE_FOR_COLUMN - Value not valid for field
processed 4 submissions
Error: Process completed with exit code 1.
```

### Custom Metrics

Add custom logging:

```python
import json
import datetime

def log_metrics(processed, created, updated, errors):
    metrics = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "processed": processed,
        "created": created,
        "updated": updated,
        "errors": errors
    }
    
    print(f"METRICS: {json.dumps(metrics)}")
```

Parse from logs for analytics.

---

## 🤝 Contributing

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Test thoroughly**
5. **Submit a pull request**

### Contribution Guidelines

- **Code Quality:** Follow PEP 8, add type hints
- **Documentation:** Update docs for any changes
- **Testing:** Test locally before submitting
- **Commit Messages:** Clear and descriptive
- **Backward Compatibility:** Don't break existing functionality

### Reporting Issues

**Include:**
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Error messages (if any)
- Environment details (Python version, OS, etc.)

---

## 📚 Additional Resources

### API Documentation

- **Jotform API:** https://api.jotform.com/docs/
- **Airtable API:** https://airtable.com/developers/web/api/introduction
- **Airtable Meta API:** https://airtable.com/developers/web/api/model/bases-tables-fields

### Related Tools

- **Zapier:** No-code alternative for simple integrations
- **Make (Integromat):** Advanced no-code automation
- **Airtable Scripting:** Custom logic within Airtable

### Community

- **GitHub Discussions:** [Enable for Q&A]
- **GitHub Issues:** Bug reports and feature requests

---

## ✅ Checklist for Technical Setup

- [ ] Python 3.11 installed
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with all secrets
- [ ] Jotform API key obtained and tested
- [ ] Airtable personal access token created with correct scopes
- [ ] Airtable base ID identified
- [ ] Test run completed locally (`python sync.py --dry-run`)
- [ ] GitHub secrets configured in repository settings
- [ ] GitHub Actions workflow enabled
- [ ] Manual workflow run tested via GitHub UI
- [ ] Automatic schedule verified (check Actions tab after 1 hour)
- [ ] Documentation reviewed and understood
- [ ] Team members granted repository access
- [ ] Monitoring plan established

---

**End of Technical Setup Guide**

*For non-technical user instructions, see [USER_GUIDE.md](USER_GUIDE.md).*

---

**Document Version:** 1.0  
**Last Updated:** February 2026  
**Repository:** github.com/OluwaseyiFad/airtable-jotform-sync  
**Maintainer:** OluwaseyiFad
