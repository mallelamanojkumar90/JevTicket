from __future__ import annotations

from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

from config import Settings, load_settings
from models import CATEGORY_CRITERIA, SEVERITY_CRITERIA, Category, CategoryDecision


class JevConfigurationError(RuntimeError):
    pass


class JevRequestError(RuntimeError):
    pass


class JevClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @classmethod
    def from_env(cls) -> "JevClient":
        return cls(load_settings())

    def analyze_ticket(self, ticket_message: str) -> CategoryDecision:
        if not self._settings.typesafe_api_key:
            raise JevConfigurationError("Missing TYPESAFE_API_KEY.")

        try:
            with TypeSafeClient(
                api_key=self._settings.typesafe_api_key,
                model=self._settings.typesafe_default_model,
            ) as client:
                response = client.system_one(
                    state={
                        "ticket": ticket_message,
                    },
                    questions={
                        "category": Choice(
                            instructions="Classify this support ticket into exactly one support category.",
                            criteria=CATEGORY_CRITERIA,
                        ),
                        "urgent": Noul(
                            instructions="Does this ticket require urgent attention?",
                            criteria={
                                "true": "The customer describes immediate time pressure, a blocked critical workflow, production impact, or asks for urgent help.",
                                "false": "The ticket can be handled through the normal support queue.",
                            },
                        ),
                        "severity": Score(
                            instructions="Rate the severity of this support ticket on a 1 to 5 scale.",
                            criteria=SEVERITY_CRITERIA,
                        ),
                    },
                )
        except Exception as exc:
            raise JevRequestError(str(exc)) from exc

        category_answer = response.choices["category"]
        urgency_answer = response.nouls["urgent"]
        severity_answer = response.scores["severity"]

        try:
            category = Category(category_answer.choice.upper())
        except ValueError as exc:
            raise JevRequestError(f"Jev returned an unknown category: {category_answer.choice}") from exc

        return CategoryDecision(
            category=category,
            confidence=category_answer.confidence,
            probabilities={
                Category(raw_category.upper()): probability
                for raw_category, probability in category_answer.probabilities.items()
                if raw_category.upper() in Category.__members__
            },
            urgent_probability=urgency_answer.noul,
            severity=severity_answer.score + 1,
            severity_confidence=severity_answer.confidence,
            severity_probabilities={
                int(level) + 1: probability
                for level, probability in severity_answer.probabilities.items()
            },
            model=response.model,
            usage_input_tokens=response.usage.input_tokens,
            usage_output_tokens=response.usage.output_tokens,
        )

    def classify_ticket_category(self, ticket_message: str) -> CategoryDecision:
        return self.analyze_ticket(ticket_message)
