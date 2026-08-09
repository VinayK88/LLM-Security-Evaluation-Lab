from __future__ import annotations

import json
from pathlib import Path
from typing import List

from .models import Scenario


def load_scenarios(path: str = "data/scenarios.json") -> List[Scenario]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Scenario(**item) for item in payload]
