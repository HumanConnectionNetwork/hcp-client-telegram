import json
from pathlib import Path
from typing import Any


DATA_DIR = Path("data")
RECORDS_FILE = DATA_DIR / "hcp_records.json"


def ensure_storage_exists() -> None:
    """
    Ensure that the local storage directory and records file exist.
    """

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not RECORDS_FILE.exists():
        RECORDS_FILE.write_text(
            "[]",
            encoding="utf-8",
        )


def load_records() -> list[dict[str, Any]]:
    """
    Load all locally stored HCP records.
    """

    ensure_storage_exists()

    try:
        content = RECORDS_FILE.read_text(
            encoding="utf-8",
        )

        records = json.loads(content)

        if not isinstance(records, list):
            return []

        return [
            record
            for record in records
            if isinstance(record, dict)
        ]

    except (json.JSONDecodeError, OSError):
        return []


def save_records(
    records: list[dict[str, Any]],
) -> None:
    """
    Save all HCP records to local storage.
    """

    ensure_storage_exists()

    RECORDS_FILE.write_text(
        json.dumps(
            records,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def add_record(
    record: dict[str, Any],
) -> None:
    """
    Add one canonical HCP record to local storage.
    """

    records = load_records()
    records.append(record)
    save_records(records)


def load_record_by_id(
    record_id: str,
) -> dict[str, Any] | None:
    """
    Return the record matching the supplied UUID.

    Returns None when no record exists.
    """

    normalized_id = str(record_id).strip().lower()

    if not normalized_id:
        return None

    for record in load_records():
        stored_id = str(
            record.get("id", "")
        ).strip().lower()

        if stored_id == normalized_id:
            return record

    return None
