from typing import Any


def _clean_text(value: Any) -> str | None:
    """
    Normalize optional text supplied by the Telegram conversation.

    Empty values are omitted from the canonical HCP Query.
    """

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    return text


def _clean_age(value: Any) -> int | None:
    """
    Normalize an optional estimated human age.

    Returns None when no age was supplied.

    Raises:
        ValueError:
            If the supplied age is not a non-negative integer.
    """

    if value is None or value == "":
        return None

    if isinstance(value, bool):
        raise ValueError(
            "estimated_age must be a non-negative integer"
        )

    try:
        age = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "estimated_age must be a non-negative integer"
        ) from exc

    if age < 0:
        raise ValueError(
            "estimated_age must be a non-negative integer"
        )

    return age


def _build_human_subject(
    search_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Build the canonical Subject Query for a human.
    """

    subject: dict[str, Any] = {
        "type": "human",
    }

    reported_label = _clean_text(
        search_data.get("reported_name")
    )
    estimated_age = _clean_age(
        search_data.get("estimated_age")
    )
    recognition_features = _clean_text(
        search_data.get("recognition_features")
    )

    if reported_label is not None:
        subject["reported_label"] = reported_label

    if estimated_age is not None:
        subject["estimated_age"] = estimated_age

    if recognition_features is not None:
        subject["recognition_features"] = recognition_features

    return subject


def _build_animal_subject(
    search_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Build the canonical Subject Query for an animal.

    Animal-specific fields are included as extensible HCP evidence. Current
    nodes may ignore unsupported fields while preserving the canonical Query.
    """

    subject: dict[str, Any] = {
        "type": "animal",
    }

    reported_label = _clean_text(
        search_data.get("animal_name")
    )
    recognition_features = _clean_text(
        search_data.get("recognition_features")
    )
    species = _clean_text(
        search_data.get("species")
    )
    size = _clean_text(
        search_data.get("size")
    )
    breed = _clean_text(
        search_data.get("breed_or_type")
    )

    if reported_label is not None:
        subject["reported_label"] = reported_label

    if recognition_features is not None:
        subject["recognition_features"] = recognition_features

    if species is not None:
        subject["species"] = species

    if size is not None:
        subject["size"] = size

    if breed is not None:
        subject["breed"] = breed

    return subject


def _build_observation_query(
    search_data: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Build optional observation criteria for the HCP Query.

    The observation object is omitted when no observation evidence exists.
    """

    observation: dict[str, Any] = {}

    reported_location = _clean_text(
        search_data.get("location")
    )
    event_type = _clean_text(
        search_data.get("event_type")
    )

    if reported_location is not None:
        observation["reported_location"] = reported_location

    if event_type is not None:
        observation["event_type"] = event_type

    return observation or None


def build_hcp_query(
    search_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert Telegram search conversation data into a canonical HCP Query.

    The Telegram conversation is free to use UX-oriented field names such as
    ``reported_name`` or ``breed_or_type``. This builder is the only component
    responsible for translating those values into HCP semantics.

    Args:
        search_data:
            Temporary search information stored in
            ``context.user_data["search_record"]``.

    Returns:
        A canonical Humanitarian Query ready to send to an HCP Node.

    Raises:
        TypeError:
            If search_data is not a dictionary.

        ValueError:
            If the search category is missing, unsupported or contains invalid
            values.
    """

    if not isinstance(search_data, dict):
        raise TypeError(
            "search_data must be a dictionary"
        )

    category = _clean_text(
        search_data.get("category")
    )

    if category == "person":
        subject = _build_human_subject(search_data)

    elif category == "animal":
        subject = _build_animal_subject(search_data)

    else:
        raise ValueError(
            "search category must be 'person' or 'animal'"
        )

    query: dict[str, Any] = {
        "subject": subject,
    }

    observation = _build_observation_query(search_data)

    if observation is not None:
        query["observation"] = observation

    return query
