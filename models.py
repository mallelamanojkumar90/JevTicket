from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict


class Category(str, Enum):
    BILLING = "BILLING"
    TECHNICAL = "TECHNICAL"
    SALES = "SALES"
    GENERAL = "GENERAL"


CATEGORY_CRITERIA = {
    Category.BILLING.value: "Payments, refunds, invoices, charges, subscriptions, or account balances.",
    Category.TECHNICAL.value: "Bugs, outages, login problems, integrations, errors, or product failures.",
    Category.SALES.value: "Pricing questions, plan comparisons, demos, upgrades, or buying intent.",
    Category.GENERAL.value: "Questions or requests that do not clearly fit billing, technical, or sales.",
}

SEVERITY_CRITERIA = [
    "Very low: informational request, no impact, no time pressure.",
    "Low: minor inconvenience or simple question with little customer impact.",
    "Medium: customer is affected and needs help, but there is no severe outage or major financial risk.",
    "High: serious customer impact, urgent financial issue, blocked workflow, or strong time pressure.",
    "Critical: production outage, security concern, major financial loss, or many customers affected.",
]


class CategoryDecision(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    category: Category
    confidence: float | None = None
    probabilities: dict[Category, float] | None = None
    urgent_probability: float
    severity: float
    severity_confidence: float | None = None
    severity_probabilities: dict[int, float] | None = None
    model: str
    usage_input_tokens: int | None = None
    usage_output_tokens: int | None = None

    @property
    def is_urgent(self) -> bool:
        return self.urgent_probability >= 0.5

    @property
    def severity_display(self) -> int:
        return round(self.severity)

    @property
    def should_escalate(self) -> bool:
        return self.severity_display >= 4
