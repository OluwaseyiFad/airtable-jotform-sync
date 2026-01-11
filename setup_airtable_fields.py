import os
import requests
from dotenv import load_dotenv

load_dotenv()

JOTFORM_API_KEY = os.getenv("JOTFORM_API_KEY", "")
JOTFORM_FORM_ID = os.getenv("JOTFORM_FORM_ID", "")
AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN", "")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")
AIRTABLE_TABLE = os.getenv("AIRTABLE_TABLE", "")

JOTFORM_BASE = "https://api.jotform.com"


def get_jotform_questions():
    """Fetch all questions/fields from the Jotform form."""
    url = f"{JOTFORM_BASE}/form/{JOTFORM_FORM_ID}/questions"
    r = requests.get(url, params={"apiKey": JOTFORM_API_KEY}, timeout=30)
    r.raise_for_status()
    return r.json().get("content", {})


def jotform_type_to_airtable(qtype: str) -> dict:
    """Map Jotform question types to Airtable field types."""
    mapping = {
        "control_textbox": {"type": "singleLineText"},
        "control_fullname": {"type": "singleLineText"},
        "control_email": {"type": "email"},
        "control_phone": {"type": "phoneNumber"},
        "control_number": {"type": "number", "options": {"precision": 0}},
        "control_textarea": {"type": "multilineText"},
        "control_dropdown": {"type": "singleLineText"},
        "control_radio": {"type": "singleLineText"},
        "control_checkbox": {"type": "multilineText"},
        "control_fileupload": {"type": "multipleAttachments"},
        "control_datetime": {"type": "singleLineText"},
        "control_date": {"type": "date"},
        "control_address": {"type": "multilineText"},
        "control_scale": {"type": "number", "options": {"precision": 0}},
        "control_rating": {"type": "number", "options": {"precision": 0}},
        "control_signature": {"type": "multipleAttachments"},
    }
    return mapping.get(qtype, {"type": "singleLineText"})


def get_existing_airtable_fields():
    """Get existing fields in the Airtable table."""
    url = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()

    tables = r.json().get("tables", [])
    for table in tables:
        if table.get("name") == AIRTABLE_TABLE:
            return {f["name"]: f for f in table.get("fields", [])}
    return {}


def get_table_id():
    """Get the table ID for the configured table name."""
    url = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()

    tables = r.json().get("tables", [])
    for table in tables:
        if table.get("name") == AIRTABLE_TABLE:
            return table.get("id")
    return None


def create_airtable_field(table_id: str, name: str, field_config: dict):
    """Create a new field in Airtable."""
    url = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables/{table_id}/fields"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"name": name, **field_config}
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    if not r.ok:
        print(f"  [ERROR] Failed to create '{name}': {r.status_code} - {r.text}")
        return False
    print(f"  [OK] Created field: {name}")
    return True


def main():
    print("Fetching Jotform form questions...")
    questions = get_jotform_questions()
    print(f"Found {len(questions)} questions in Jotform.\n")

    print("Fetching existing Airtable fields...")
    existing_fields = get_existing_airtable_fields()
    print(f"Found {len(existing_fields)} existing fields in Airtable.\n")

    table_id = get_table_id()
    if not table_id:
        print(f"ERROR: Could not find table '{AIRTABLE_TABLE}'")
        return

    # Fields to create
    fields_to_create = []

    for qid, question in questions.items():
        qtype = question.get("type", "")
        name = question.get("name", "") or question.get("text", f"Question {qid}")

        # Skip non-input controls
        if qtype in ["control_head", "control_button", "control_pagebreak", "control_divider", "control_text", "control_image"]:
            continue

        # Clean up field name
        name = name.strip()[:255]  # Airtable has a 255 char limit
        if not name:
            name = f"Field_{qid}"

        if name in existing_fields:
            print(f"[SKIP] Field already exists: {name}")
            continue

        field_config = jotform_type_to_airtable(qtype)
        fields_to_create.append((name, field_config, qtype))

    if not fields_to_create:
        print("\nNo new fields to create. Airtable is already in sync!")
        return

    print(f"\nCreating {len(fields_to_create)} new fields in Airtable...")
    for name, field_config, qtype in fields_to_create:
        print(f"\n  Creating: {name} (Jotform type: {qtype})")
        create_airtable_field(table_id, name, field_config)

    print("\nDone!")


if __name__ == "__main__":
    main()
