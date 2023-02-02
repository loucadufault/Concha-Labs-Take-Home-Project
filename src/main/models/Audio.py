from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List


@dataclass_json
@dataclass
class Audio:
    """Model representing all input information of an audio file."""
    session_id: int
    ticks: List
    selected_tick: int
    step_count: int
