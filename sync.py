import os
import json
import time
import argparse
from datetime import datetime
from typing import Any, Dict, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

# Secrets
JOTFORM_API_KEY = os.getenv("JOTFORM_API_KEY", "")
JOTFORM_FORM_ID = os.getenv("JOTFORM_FORM_ID", "")
AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN", "")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")

AIRTABLE_TABLE = "Table 1"
# Submission ID to track/update records
SUBMISSION_ID_FIELD = "Submission ID"

# Fields that need numeric conversion
NUMERIC_FIELDS = ["Top 10 Class"]

# Fields that need array format (multipleSelects in Airtable)
MULTI_SELECT_FIELDS = [
    "Are you interested in volunteering in one of the vocations below?",
    "Fields of Interest",
]

# Skip these fields for now
SKIP_FIELDS = [
    "Are you interested in volunteering in one of the vocations below?",
    "Fields of Interest",
    "Business Phone Number (Area Code)",
    "Business Address (State)",
    "Home Address (State/Province)",
]

# Vocation experience fields that need value normalization (Jotform → Airtable)
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
    "14. Human Resources",
]

# Normalize Jotform vocation values to match Airtable options
VOCATION_VALUE_MAP = {
    "0-2 years": "0-2 Years",
    "> 10 years": "> 10 Years",
    # These already match: "> 3-5 Years"
}

# Jotform field name - Airtable field name mapping
FIELD_MAPPING = {
    "highestEducation": "Highest Education Level Completed",
    "top10": "Top 10 Class",
    "title": "Title",
    "test": "Test 10",
    "mostRecent": "Most Recent Employer",
    "businessEmail": "Business Email (if currently employed)",
    "businessName": "Business Name",
    "personalEmail": "Personal Email",
    "whichOf": "Which of these options above are your Top 3 choices?",
    "resume": "Resume",
    "retired": "Retired",
    "additionalComments": "Additional Comments:",
    "typeA": "1. Public Health/Hospitals",
    "typeA35": "2. Public Service",
    "2Public": "3. Finance/Banking/Insurance",
    "2Public37": "4. Government",
    "2Public38": "5. Transportation (i.e. RTA)",
    "2Public39": "6. Engineering",
    "7It": "7. IT Technology",
    "2Public41": "8. Social Service",
    "2Public42": "9. Non Profit",
    "2Public43": "10. Public Safety",
    "2Public44": "11. Civil Rights Activist",
    "2Public45": "12. Mentoring",
    "2Public46": "13. Equity",
    "2Public47": "14. Human Resources",
    "typeA50": "Are you interested in volunteering in one of the vocations below?",
    "typeA77": "Fields of Interest",
}

# Composite fields (fullname, address, phone) with subfield mappings
COMPOSITE_FIELDS = {
    "name": {
        "first": "Name (First)",
        "last": "Name (Last)",
    },
    "homeAddress": {
        "addr_line1": "Home Address (Street)",
        "addr_line2": "Home Address (Street Line 2)",
        "city": "Home Address (City)",
        "state": "Home Address (State/Province)",
        "postal": "Home Address (Postal/Zip Code)",
    },
    "businessAddress15": {
        "addr_line1": "Business Address (Street Address)",
        "addr_line2": "Business Address (Street Address Line 2)",
        "city": "Business Address (City)",
        "state": "Business Address (State)",
        "postal": "Business Address (Zip Code)",
    },
    "personalPhone": {
        "full": "Personal Phone Number",
    },
    "businessPhone": {
        "area": "Business Phone Number (Area Code)",
        "full": "Business Phone Number",
    },
}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WATERMARK_FILE = os.path.join(SCRIPT_DIR, "watermark.json")
QUESTIONS_CACHE: Dict[str, Any] = {}

# Enterprise URL
JOTFORM_BASE = os.getenv("JOTFORM_BASE", "https://parityinc.jotform.com/API")
AIRTABLE_BASE = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE}"


def die(msg: str) -> None:
    raise SystemExit(msg)


def parse_timestamp(value: Any) -> int:
    """Convert Jotform datetime string or Unix timestamp to int timestamp."""
    if not value:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            return int(dt.timestamp())
        except ValueError:
            pass
        try:
            return int(value)
        except ValueError:
            pass
    return 0


def headers_airtable() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json",
    }


def jotform_get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if not JOTFORM_API_KEY:
        die("Missing JOTFORM_API_KEY")
    url = f"{JOTFORM_BASE}{path}"
    params = params or {}
    params["apiKey"] = JOTFORM_API_KEY
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def airtable_get(params: Dict[str, Any]) -> Dict[str, Any]:
    if not AIRTABLE_TOKEN:
        die("Missing AIRTABLE_TOKEN")
    r = requests.get(AIRTABLE_BASE, headers=headers_airtable(), params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def airtable_post(payload: Dict[str, Any]) -> Dict[str, Any]:
    r = requests.post(AIRTABLE_BASE, headers=headers_airtable(), json=payload, timeout=30)
    if not r.ok:
        print(f"[ERROR] Airtable POST failed: {r.status_code} - {r.text}")
    r.raise_for_status()
    return r.json()


def airtable_patch(record_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    r = requests.patch(f"{AIRTABLE_BASE}/{record_id}", headers=headers_airtable(), json=payload, timeout=30)
    if not r.ok:
        print(f"[ERROR] Airtable PATCH failed: {r.status_code} - {r.text}")
    r.raise_for_status()
    return r.json()


def fetch_form_questions() -> Dict[str, Any]:
    """Fetch and cache form questions (qid -> question info)."""
    global QUESTIONS_CACHE
    if QUESTIONS_CACHE:
        return QUESTIONS_CACHE
    resp = jotform_get(f"/form/{JOTFORM_FORM_ID}/questions")
    QUESTIONS_CACHE = resp.get("content", {})
    return QUESTIONS_CACHE


def get_answer_value(answer_obj: Any, qtype: str) -> Any:
    """Extract a displayable value from a Jotform answer object."""
    if answer_obj is None:
        return None

    # For file uploads, return URLs as attachments
    if qtype == "control_fileupload":
        urls = extract_urls_from_one_answer(answer_obj)
        if urls:
            return to_airtable_attachments(urls)
        return None

    # Try to get prettyFormat first (nicely formatted), then answer
    if isinstance(answer_obj, dict):
        val = answer_obj.get("prettyFormat") or answer_obj.get("answer")
        if isinstance(val, list):
            return ", ".join(str(v) for v in val if v)
        return val

    if isinstance(answer_obj, list):
        return ", ".join(str(v) for v in answer_obj if v)

    return answer_obj


def extract_composite_fields(field_name: str, answer_obj: Any) -> Dict[str, str]:
    """Extract subfields from composite Jotform fields (name, address, phone)."""
    result = {}
    if field_name not in COMPOSITE_FIELDS or not isinstance(answer_obj, dict):
        return result

    mapping = COMPOSITE_FIELDS[field_name]
    answer = answer_obj.get("answer", {})
    if not isinstance(answer, dict):
        return result

    for jotform_key, airtable_field in mapping.items():
        value = answer.get(jotform_key, "")
        if value:
            result[airtable_field] = str(value)
        else:
            result[airtable_field] = ""

    return result


def load_watermark() -> int:
    if not os.path.exists(WATERMARK_FILE):
        return 0
    with open(WATERMARK_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return int(data.get("last_updated_at", 0))


def save_watermark(ts: int) -> None:
    with open(WATERMARK_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_updated_at": int(ts)}, f)


def find_record_by_submission_id(submission_id: str) -> Optional[str]:
    """Find an Airtable record by Jotform submission ID."""
    if not submission_id:
        return None
    safe = submission_id.replace("'", "''")
    formula = f"{{{SUBMISSION_ID_FIELD}}}='{safe}'"
    resp = airtable_get({"filterByFormula": formula, "maxRecords": 1})
    records = resp.get("records", [])
    if records:
        return records[0]["id"]
    return None


def to_airtable_attachments(file_urls: List[str]) -> List[Dict[str, str]]:
    attachments = []
    for url in file_urls:
        filename = url.split("/")[-1].split("?")[0] or "file"
        attachments.append({"url": url, "filename": filename})
    return attachments


def extract_urls_from_one_answer(answer_obj: Any) -> List[str]:
    found: List[str] = []
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


def fetch_all_submissions() -> List[Dict[str, Any]]:
    """Pull submissions in pages."""
    submissions: List[Dict[str, Any]] = []
    offset = 0
    limit = 100
    while True:
        resp = jotform_get(f"/form/{JOTFORM_FORM_ID}/submissions", {"limit": limit, "offset": offset})
        page = resp.get("content", [])
        if not page:
            break
        submissions.extend(page)
        offset += limit
        if limit and len(page) < limit:
            break
    return submissions


def upsert_to_airtable(submission: Dict[str, Any], dry_run: bool = False) -> None:
    submission_id = str(submission.get("id", ""))

    # Start with submission ID for tracking
    fields: Dict[str, Any] = {
        SUBMISSION_ID_FIELD: submission_id,
    }

    questions = fetch_form_questions()
    answers = submission.get("answers", {}) or {}

    for qid, question in questions.items():
        field_name = question.get("name", "")
        qtype = question.get("type", "")

        if qtype in ["control_head", "control_button", "control_pagebreak", "control_divider", "control_text", "control_image"]:
            continue

        if not field_name:
            continue

        answer_obj = answers.get(qid)

        # Handle composite fields (name, address, phone)
        if field_name in COMPOSITE_FIELDS:
            composite_values = extract_composite_fields(field_name, answer_obj)
            # Filter out any SKIP_FIELDS from composite values
            for k, v in composite_values.items():
                if k not in SKIP_FIELDS:
                    fields[k] = v
            continue

        # Map field name to Airtable field name
        airtable_field = FIELD_MAPPING.get(field_name, field_name)

        # Skip problematic select fields
        if airtable_field in SKIP_FIELDS:
            continue

        value = get_answer_value(answer_obj, qtype)

        # Only add non-empty values
        if value is not None and value != "":
            # Convert numeric fields
            if airtable_field in NUMERIC_FIELDS:
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    value = None
            # Convert multi-select fields to arrays
            elif airtable_field in MULTI_SELECT_FIELDS:
                if isinstance(value, str):
                    value = [v.strip() for v in value.split(",") if v.strip()]
            # Normalize vocation field values to match Airtable options
            elif airtable_field in VOCATION_FIELDS:
                if isinstance(value, str):
                    value = VOCATION_VALUE_MAP.get(value, value)
            if value is not None and value != []:
                fields[airtable_field] = value

    # Look up existing record by submission ID
    record_id = find_record_by_submission_id(submission_id)

    if dry_run:
        action = "update" if record_id else "create"
        print(f"[DRY RUN] Would {action} record for submission {submission_id}")
        print(f"          Fields: {list(fields.keys())}")
        return

    payload = {"fields": fields}

    if record_id:
        airtable_patch(record_id, payload)
        print(f"[OK] Updated record {record_id} for submission {submission_id}")
    else:
        airtable_post(payload)
        print(f"[OK] Created record for submission {submission_id}")

    time.sleep(0.25)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run once and exit.")
    parser.add_argument("--dry-run", action="store_true", help="Do not write to Airtable.")
    parser.add_argument("--ignore-watermark", action="store_true", help="Process all submissions.")
    args = parser.parse_args()

    if not (JOTFORM_FORM_ID and AIRTABLE_BASE_ID and AIRTABLE_TABLE):
        die("Missing required config: JOTFORM_FORM_ID / AIRTABLE_BASE_ID / AIRTABLE_TABLE")

    last_watermark = 0 if args.ignore_watermark else load_watermark()
    print(f"Loaded watermark: {last_watermark}")

    submissions = fetch_all_submissions()
    print(f"Fetched {len(submissions)} submissions from Jotform.")

    newest_seen = last_watermark

    for s in submissions:
        updated_at = parse_timestamp(s.get("updated_at") or s.get("created_at"))
        if updated_at <= last_watermark:
            continue

        upsert_to_airtable(s, dry_run=args.dry_run)

        if updated_at > newest_seen:
            newest_seen = updated_at

    if newest_seen > last_watermark and not args.dry_run:
        save_watermark(newest_seen)
        print(f"Saved new watermark: {newest_seen}")
    else:
        print("No watermark update needed.")


if __name__ == "__main__":
    main()
