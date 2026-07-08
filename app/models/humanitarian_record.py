from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class HumanitarianRecord:
    """
    Humanitarian Record defined by HCP.

    A Humanitarian Record represents a humanitarian observation
    composed of correlation variables.

    It is not an identity record.
    """

    subject_type: str
    event_type: str

    reported_name: str
    estimated_age: int
    reported_location: str

    source: str
    recognition_features: str

    status: str = "reported"

    def to_dict(self) -> dict[str, Any]:
        """
        Returns the Humanitarian Record as a dictionary.
        """
        return asdict(self)
