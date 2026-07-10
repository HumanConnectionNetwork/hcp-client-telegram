import json
from pathlib import Path
from typing import Any


DATA_DIR = Path("data")
RECORDS_FILE = DATA_DIR / "hcp_records.json"


def ensure_storage_exists() -> None:
    """
    Ensures that the local development storage exists.

    In production, this module can later be replaced by a repository
    connected to an HCP Node or another persistent storage system.
    """

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not RECORDS_FILE.exists():
        RECORDS_FILE.write_text(
            "[]",
            encoding="utf-8",
        )


def load_records() -> list[dict[str, Any]]:
    """
    Loads all locally stored HCP records.

    Returns an empty list if the file does not contain valid JSON,
    cannot be read, or does not contain a JSON array.
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
    Replaces the local record collection with the supplied records.
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
    Appends one canonical HCP record to local storage.
    """

    records = load_records()
    records.append(record)
    save_records(records)

def load_record_by_id(
    record_id: str,
) -> dict[str, Any] | None:
    """
    Returns one HCP record matching the supplied UUID.

    The comparison ignores surrounding whitespace and letter casing.
    Returns None when the record does not exist.
    """

    normalized_id = str(record_id).strip().lower()

    if not normalized_id:
        return None

    for record in load_records():
        stored_id = str(record.get("id", "")).strip().lower()

        if stored_id == normalized_id:
            return record

    return None


def load_record_by_id(
    record_id: str,
) -> dict[str, Any] | None:
    """
    Returns one HCP record matching the supplied UUID.

    The comparison ignores surrounding whitespace and letter casing.
    Returns None when the record does not exist.
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
