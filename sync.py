import os
import json
import time
import argparse
from datetime import datetime
from typing import Any, Dict, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

JOTFORM_API_KEY = os.getenv("JOTFORM_API_KEY", "")
JOTFORM_FORM_ID = os.getenv("JOTFORM_FORM_ID", "")

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN", "")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")
AIRTABLE_TABLE = os.getenv("AIRTABLE_TABLE", "")

FIELD_SUBMISSION_ID = os.getenv("FIELD_SUBMISSION_ID", "Submission ID")
FIELD_UPDATED_AT = os.getenv("FIELD_UPDATED_AT", "Last Jotform Updated At")
FIELD_RAW = os.getenv("FIELD_RAW", "Raw Payload")

ATTACHMENTS_MODE = os.getenv("ATTACHMENTS_MODE", "attachment").strip().lower()
FIELD_FILES_TEXT = os.getenv("FIELD_FILES_TEXT", "Resume URLs")
FIELD_ATTACHMENTS = os.getenv("FIELD_ATTACHMENTS", "Resume")

JOTFORM_RESUME_QID = os.getenv("JOTFORM_RESUME_QID", "").strip()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WATERMARK_FILE = os.path.join(SCRIPT_DIR, "watermark.json")
QUESTIONS_CACHE: Dict[str, Any] = {}

JOTFORM_BASE = "https://api.jotform.com"
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
        # Try parsing as datetime string (e.g., '2025-12-28 13:21:58')
        try:
            dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            return int(dt.timestamp())
        except ValueError:
            pass
        # Try parsing as int string
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


def load_watermark() -> int:
    if not os.path.exists(WATERMARK_FILE):
        return 0
    with open(WATERMARK_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return int(data.get("last_updated_at", 0))


def save_watermark(ts: int) -> None:
    with open(WATERMARK_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_updated_at": int(ts)}, f)


def find_airtable_record_by_submission_id(submission_id: str) -> Optional[str]:
    # Airtable filterByFormula; escape single quotes by doubling them
    safe = submission_id.replace("'", "''")
    formula = f"{{{FIELD_SUBMISSION_ID}}}='{safe}'"
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


def extract_file_urls_from_answers(answers: Dict[str, Any]) -> List[str]:
    """
    Jotform answers structure varies by form setup.
    We try to robustly extract anything that looks like a URL from file upload answers.
    """
    urls: List[str] = []

    # If user provided a specific resume question id, prioritize it.
    if JOTFORM_RESUME_QID and JOTFORM_RESUME_QID in answers:
        a = answers[JOTFORM_RESUME_QID]
        urls.extend(extract_urls_from_one_answer(a))
        return dedupe_keep_order(urls)

    # Otherwise, scan all answers for file-like URLs
    for _, a in answers.items():
        urls.extend(extract_urls_from_one_answer(a))

    # Heuristic: keep only http(s) strings
    urls = [u for u in urls if isinstance(u, str) and u.startswith(("http://", "https://"))]
    return dedupe_keep_order(urls)


def extract_urls_from_one_answer(answer_obj: Any) -> List[str]:
    found: List[str] = []
    if isinstance(answer_obj, dict):
        # common places
        for k in ["answer", "prettyFormat", "value"]:
            v = answer_obj.get(k)
            found.extend(extract_urls_from_one_answer(v))
    elif isinstance(answer_obj, list):
        for item in answer_obj:
            found.extend(extract_urls_from_one_answer(item))
    elif isinstance(answer_obj, str):
        # sometimes multiple URLs separated by newlines/commas
        parts = [p.strip() for p in answer_obj.replace("\n", ",").split(",")]
        for p in parts:
            if p.startswith(("http://", "https://")):
                found.append(p)
    return found


def dedupe_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def fetch_all_submissions() -> List[Dict[str, Any]]:
    """
    Pull submissions in pages.
    Jotform API returns content with pagination (offset).
    """
    submissions: List[Dict[str, Any]] = []
    offset = 0
    limit = 100  # page size
    while True:
        resp = jotform_get(f"/form/{JOTFORM_FORM_ID}/submissions", {"limit": limit, "offset": offset})
        page = resp.get("content", [])
        if not page:
            break
        submissions.extend(page)
        offset += limit
        # safety break for extremely large forms
        if limit and len(page) < limit:
            break
    return submissions


def upsert_to_airtable(submission: Dict[str, Any], file_urls: List[str], dry_run: bool = False) -> None:
    submission_id = str(submission.get("id", ""))
    updated_at = parse_timestamp(submission.get("updated_at") or submission.get("created_at"))

    fields: Dict[str, Any] = {
        FIELD_SUBMISSION_ID: submission_id,
        FIELD_UPDATED_AT: str(updated_at),
    }

    # Optional raw payload to debug answer parsing
    if FIELD_RAW:
        fields[FIELD_RAW] = json.dumps(submission, ensure_ascii=False)

    # Map individual form fields to Airtable
    questions = fetch_form_questions()
    answers = submission.get("answers", {}) or {}

    # Loop through all questions to handle both filled and cleared fields
    for qid, question in questions.items():
        field_name = question.get("name", "")
        qtype = question.get("type", "")

        # Skip non-input controls
        if qtype in ["control_head", "control_button", "control_pagebreak", "control_divider", "control_text", "control_image"]:
            continue

        if not field_name:
            continue

        answer_obj = answers.get(qid)
        value = get_answer_value(answer_obj, qtype)

        # Set appropriate empty value for cleared fields
        if value is None or value == "":
            if qtype == "control_fileupload":
                fields[field_name] = []  # Empty array clears attachments
            else:
                fields[field_name] = ""  # Empty string clears text fields
        else:
            fields[field_name] = value

    record_id = find_airtable_record_by_submission_id(submission_id)

    if dry_run:
        print(f"[DRY RUN] Would {'update' if record_id else 'create'} Airtable record for submission {submission_id}")
        print(f"          updated_at={updated_at}, files={len(file_urls)}")
        return

    payload = {"fields": fields}

    if record_id:
        airtable_patch(record_id, payload)
        print(f"[OK] Updated Airtable record {record_id} for submission {submission_id} (files={len(file_urls)})")
    else:
        airtable_post(payload)
        print(f"[OK] Created Airtable record for submission {submission_id} (files={len(file_urls)})")

    # Airtable rate limit friendliness
    time.sleep(0.25)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run once and exit.")
    parser.add_argument("--dry-run", action="store_true", help="Do not write to Airtable.")
    parser.add_argument("--ignore-watermark", action="store_true", help="Process all submissions regardless of watermark.")
    args = parser.parse_args()

    if not (JOTFORM_FORM_ID and AIRTABLE_BASE_ID and AIRTABLE_TABLE):
        die("Missing required config: JOTFORM_FORM_ID / AIRTABLE_BASE_ID / AIRTABLE_TABLE")

    last_watermark = 0 if args.ignore_watermark else load_watermark()
    print(f"Loaded watermark: {last_watermark}")

    submissions = fetch_all_submissions()
    print(f"Fetched {len(submissions)} submissions from Jotform.")

    newest_seen = last_watermark

    # Process only updated submissions
    for s in submissions:
        updated_at = parse_timestamp(s.get("updated_at") or s.get("created_at"))
        if updated_at <= last_watermark:
            continue

        answers = s.get("answers", {}) or {}
        file_urls = extract_file_urls_from_answers(answers)

        upsert_to_airtable(s, file_urls, dry_run=args.dry_run)

        if updated_at > newest_seen:
            newest_seen = updated_at

    if newest_seen > last_watermark and not args.dry_run:
        save_watermark(newest_seen)
        print(f"Saved new watermark: {newest_seen}")
    else:
        print("No watermark update needed.")

    if args.once:
        return


if __name__ == "__main__":
    main()

