from __future__ import annotations

from pydantic import BaseModel

from models import Category, CategoryDecision


class RouteResult(BaseModel):
    team: str
    queue_name: str
    message: str
    escalate: bool = False
    escalation_reason: str | None = None


ROUTES: dict[Category, RouteResult] = {
    Category.BILLING: RouteResult(
        team="Billing",
        queue_name="billing-support",
        message="Route to the billing support team.",
    ),
    Category.TECHNICAL: RouteResult(
        team="Technical Support",
        queue_name="technical-support",
        message="Route to the technical support team.",
    ),
    Category.SALES: RouteResult(
        team="Sales",
        queue_name="sales",
        message="Route to the sales team.",
    ),
    Category.GENERAL: RouteResult(
        team="General Support",
        queue_name="general-support",
        message="Route to the general support team.",
    ),
}


def route_ticket(decision: CategoryDecision) -> RouteResult:
    route = ROUTES[decision.category]

    if not decision.should_escalate:
        return route

    return route.model_copy(
        update={
            "escalate": True,
            "escalation_reason": "Severity is 4 or higher.",
        }
    )
