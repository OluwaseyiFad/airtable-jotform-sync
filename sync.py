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

AIRTABLE_TABLE = "Table 1"
SUBMISSION_ID_FIELD = "Submission ID"

NUMERIC_FIELDS = ["Top 10 Class"]

MULTI_SELECT_FIELDS = [
    "Are you interested in volunteering in one of the vocations below?",
    "Fields of Interest",
]

SKIP_FIELDS = [
    "Are you interested in volunteering in one of the vocations below?",
    "Fields of Interest",
    "Business Phone Number (Area Code)",
    "Business Address (State)",
    "Home Address (State/Province)",
]

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

VOCATION_VALUE_MAP = {
    "0-2 years": "0-2 Years",
    "> 10 years": "> 10 Years",
}

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
AIRTABLE_SCHEMA_CACHE: Optional[Dict[str, Any]] = None

JOTFORM_BASE = os.getenv("JOTFORM_BASE", "https://parityinc.jotform.com/API")
AIRTABLE_BASE = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE}"

JOTFORM_TO_AIRTABLE_TYPES = {
    "control_textbox": "singleLineText",
    "control_textarea": "multilineText",
    "control_email": "email",
    "control_phone": "phoneNumber",
    "control_number": "number",
    "control_dropdown": "singleSelect",
    "control_radio": "singleSelect",
    "control_checkbox": "multipleSelects",
    "control_fileupload": "multipleAttachments",
    "control_datetime": "date",
}


def die(msg: str) -> None:
    raise SystemExit(msg)


def parse_timestamp(value: Any) -> int:
    if not value:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            return int(dt.timestamp())
        except ValueError:
            try:
                return int(value)
            except ValueError:
                return 0
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
        try:
            response_data = r.json()
            error_type = response_data.get('error', {}).get('type', '')
            if error_type in ['INVALID_VALUE_FOR_COLUMN', 'INVALID_MULTIPLE_CHOICE_OPTIONS']:
                return {'error': response_data.get('error')}
        except:
            pass
        print(f"airtable error: {r.status_code}")
        print(f"response: {r.text}")
        print(f"payload fields: {list(payload.get('fields', {}).keys())}")
        r.raise_for_status()
    return r.json()


def airtable_patch(record_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    r = requests.patch(f"{AIRTABLE_BASE}/{record_id}", headers=headers_airtable(), json=payload, timeout=30)
    if not r.ok:
        try:
            response_data = r.json()
            error_type = response_data.get('error', {}).get('type', '')
            if error_type in ['INVALID_VALUE_FOR_COLUMN', 'INVALID_MULTIPLE_CHOICE_OPTIONS']:
                return {'error': response_data.get('error')}
        except:
            pass
        r.raise_for_status()
    return r.json()


def fetch_form_questions() -> Dict[str, Any]:
    global QUESTIONS_CACHE
    if QUESTIONS_CACHE:
        return QUESTIONS_CACHE
    resp = jotform_get(f"/form/{JOTFORM_FORM_ID}/questions")
    QUESTIONS_CACHE = resp.get("content", {})
    return QUESTIONS_CACHE


def get_answer_value(answer_obj: Any, qtype: str) -> Any:
    if answer_obj is None:
        return None

    if qtype == "control_fileupload":
        urls = extract_urls_from_one_answer(answer_obj)
        if urls:
            return to_airtable_attachments(urls)
        return None

    if isinstance(answer_obj, dict):
        val = answer_obj.get("prettyFormat") or answer_obj.get("answer")
        if isinstance(val, list):
            return ", ".join(str(v) for v in val if v)
        return val

    if isinstance(answer_obj, list):
        return ", ".join(str(v) for v in answer_obj if v)

    return answer_obj


def extract_composite_fields(field_name: str, answer_obj: Any) -> Dict[str, str]:
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

    fields: Dict[str, Any] = {SUBMISSION_ID_FIELD: submission_id}

    questions = fetch_form_questions()
    answers = submission.get("answers", {}) or {}
    _, at_field_types = get_airtable_schema()

    for qid, question in questions.items():
        field_name = question.get("name", "")
        qtype = question.get("type", "")

        if qtype in ["control_head", "control_button", "control_pagebreak",
                     "control_divider", "control_text", "control_image"]:
            continue

        if not field_name:
            continue

        answer_obj = answers.get(qid)

        if field_name in COMPOSITE_FIELDS:
            composite_values = extract_composite_fields(field_name, answer_obj)
            for k, v in composite_values.items():
                if k not in SKIP_FIELDS:
                    fields[k] = v
            continue

        airtable_field = question.get("text", "")

        if not airtable_field or airtable_field in SKIP_FIELDS:
            continue

        value = get_answer_value(answer_obj, qtype)

        if value is not None and value != "":
            at_field_info = at_field_types.get(airtable_field, {})
            at_field_type = at_field_info.get("type", "")

            if at_field_type == "number" and airtable_field in NUMERIC_FIELDS:
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    value = None
            elif at_field_type == "multipleSelects" and airtable_field in MULTI_SELECT_FIELDS:
                if isinstance(value, str):
                    value = [v.strip() for v in value.split(",") if v.strip()]

            if value is not None and value != []:
                fields[airtable_field] = value

    valid_fields = get_valid_airtable_fields()
    filtered_fields = {}
    for field_name, field_value in fields.items():
        if field_name in valid_fields:
            filtered_fields[field_name] = field_value

    record_id = find_record_by_submission_id(submission_id)

    if dry_run:
        print(f"[dry-run] {submission_id}")
        return

    payload = {"fields": filtered_fields}

    if record_id:
        result = airtable_patch(record_id, payload)
        if 'error' in result:
            print(f"skipped update {submission_id} (field error)")
        else:
            print(f"updated {submission_id}")
    else:
        result = airtable_post(payload)
        if 'error' in result:
            print(f"skipped create {submission_id} (field error)")
        else:
            print(f"created {submission_id}")

    time.sleep(0.25)


def get_jotform_questions():
    url = f"{JOTFORM_BASE}/form/{JOTFORM_FORM_ID}/questions"
    r = requests.get(url, params={"apiKey": JOTFORM_API_KEY})
    r.raise_for_status()
    return r.json().get("content", {})


def get_airtable_schema():
    url = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()

    data = r.json()
    for table in data["tables"]:
        if table["name"] == AIRTABLE_TABLE:
            return table["id"], {f["name"]: f for f in table["fields"]}

    raise ValueError(f"Table '{AIRTABLE_TABLE}' not found")


def get_valid_airtable_fields():
    global AIRTABLE_SCHEMA_CACHE
    if AIRTABLE_SCHEMA_CACHE is None:
        _, fields = get_airtable_schema()
        AIRTABLE_SCHEMA_CACHE = set(fields.keys())
    return AIRTABLE_SCHEMA_CACHE


def create_airtable_field(table_id, field_name, field_type, options=None):
    url = (
        f"https://api.airtable.com/v0/meta/bases/"
        f"{AIRTABLE_BASE_ID}/tables/{table_id}/fields"
    )
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {"name": field_name, "type": field_type}
    if options and field_type in ["singleSelect", "multipleSelects"]:
        payload["options"] = options

    r = requests.post(url, headers=headers, json=payload)
    return r.ok, r.json()


def parse_jotform_dropdown_options(options_str):
    if not options_str or not isinstance(options_str, str):
        return None
    choices = [
        {"name": opt.strip()}
        for opt in options_str.split("|")
        if opt.strip()
    ]
    return {"choices": choices} if choices else None


def auto_create_missing_fields():
    global AIRTABLE_SCHEMA_CACHE

    jf_questions = get_jotform_questions()
    jf_fields = {}
    for q in jf_questions.values():
        name = q.get("name", "")
        qtype = q.get("type", "")
        if qtype in ["control_head", "control_button", "control_text",
                     "control_divider"]:
            continue
        jf_fields[name] = {
            "text": q.get("text", ""),
            "type": qtype,
            "options": q.get("options", "")
        }

    table_id, at_fields = get_airtable_schema()

    new_fields = []

    if SUBMISSION_ID_FIELD not in at_fields:
        new_fields.append({
            "at_name": SUBMISSION_ID_FIELD,
            "at_type": "singleLineText",
            "options": None
        })

    for jf_name, jf_info in jf_fields.items():
        if jf_name in COMPOSITE_FIELDS:
            for subfield_name in COMPOSITE_FIELDS[jf_name].values():
                if subfield_name not in at_fields and subfield_name not in SKIP_FIELDS:
                    new_fields.append({
                        "at_name": subfield_name,
                        "at_type": "singleLineText",
                        "options": None
                    })
            continue

        at_field_name = jf_info["text"]
        if not at_field_name or at_field_name in at_fields:
            continue

        if at_field_name in NUMERIC_FIELDS:
            at_type = "number"
        elif at_field_name in MULTI_SELECT_FIELDS:
            at_type = "multipleSelects"
        elif at_field_name in VOCATION_FIELDS:
            at_type = "singleLineText"
        else:
            at_type = JOTFORM_TO_AIRTABLE_TYPES.get(
                jf_info["type"], "singleLineText"
            )

        new_fields.append({
            "at_name": at_field_name,
            "at_type": at_type,
            "options": jf_info.get("options")
        })

    if not new_fields:
        return 0

    created_count = 0
    for field in new_fields:
        options = None
        if field['at_type'] in ['singleSelect', 'multipleSelects']:
            options = parse_jotform_dropdown_options(field['options'])

        success, result = create_airtable_field(
            table_id,
            field['at_name'],
            field['at_type'],
            options
        )

        if success:
            created_count += 1
            print(f"created field: {field['at_name']}")
        else:
            error = result.get("error", {}) if isinstance(result, dict) else {}
            msg = error.get("message", "unknown error") if error else "unknown error"
            print(f"failed to create field '{field['at_name']}': {msg}")

    if created_count > 0:
        AIRTABLE_SCHEMA_CACHE = None

    return created_count


def delete_orphaned_fields():
    global AIRTABLE_SCHEMA_CACHE
    AIRTABLE_SCHEMA_CACHE = None

    jf_questions = get_jotform_questions()
    expected_at_fields = set()

    expected_at_fields.add(SUBMISSION_ID_FIELD)

    for q in jf_questions.values():
        if not isinstance(q, dict):
            continue
        name = q.get("name", "")
        qtype = q.get("type", "")
        if qtype in ["control_head", "control_button", "control_text",
                     "control_divider"]:
            continue

        if name in COMPOSITE_FIELDS:
            for subfield_name in COMPOSITE_FIELDS[name].values():
                expected_at_fields.add(subfield_name)
        else:
            at_field_name = q.get("text", "")
            if at_field_name:
                expected_at_fields.add(at_field_name)

    _, at_fields = get_airtable_schema()

    orphaned_fields = []
    for field_name, field_info in at_fields.items():
        if not isinstance(field_info, dict):
            continue
        field_type = field_info.get("type", "")
        if field_type in ["autoNumber", "createdTime", "lastModifiedTime",
                          "createdBy", "lastModifiedBy"]:
            continue
        if field_name in expected_at_fields:
            continue
        orphaned_fields.append({"name": field_name, "type": field_type})

    return len(orphaned_fields)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--ignore-watermark", action="store_true")
    parser.add_argument("--skip-field-check", action="store_true")
    parser.add_argument("--skip-field-deletion", action="store_true")
    args = parser.parse_args()

    if not (JOTFORM_FORM_ID and AIRTABLE_BASE_ID and AIRTABLE_TABLE):
        die("Missing required config")

    if not args.skip_field_check:
        try:
            auto_create_missing_fields()
        except Exception as e:
            print(f"field check error: {e}")

    if not args.skip_field_deletion:
        try:
            delete_orphaned_fields()
        except Exception as e:
            print(f"field deletion error: {e}")

    last_watermark = 0 if args.ignore_watermark else load_watermark()
    submissions = fetch_all_submissions()
    print(f"fetched {len(submissions)} submissions")

    processed = 0
    newest_seen = last_watermark

    for s in submissions:
        updated_at = parse_timestamp(
            s.get("updated_at") or s.get("created_at")
        )
        if updated_at <= last_watermark:
            continue
        upsert_to_airtable(s, dry_run=args.dry_run)
        processed += 1
        if updated_at > newest_seen:
            newest_seen = updated_at

    print(f"processed {processed} submissions")

    if newest_seen > last_watermark and not args.dry_run:
        save_watermark(newest_seen)
        print(f"updated watermark")


if __name__ == "__main__":
    main()
