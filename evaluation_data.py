from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from models import Category


DATA_PATH = Path(__file__).parent / "data" / "labeled_tickets.json"


class LabeledTicket(BaseModel):
    ticket_id: str
    message: str = Field(min_length=1)
    category: Category
    urgent: bool
    severity: int = Field(ge=1, le=5)


def load_labeled_tickets(path: Path = DATA_PATH) -> list[LabeledTicket]:
    with path.open("r", encoding="utf-8") as file:
        raw_tickets = json.load(file)

    return [LabeledTicket.model_validate(ticket) for ticket in raw_tickets]
