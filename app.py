from __future__ import annotations

from jev_client import JevClient, JevConfigurationError, JevRequestError
from router import route_ticket


TEST_TICKET = "Payment was deducted twice from my account."


def main() -> None:
    client = JevClient.from_env()

    print("Input:")
    print(TEST_TICKET)
    print()

    try:
        decision = client.analyze_ticket(TEST_TICKET)
    except JevConfigurationError as exc:
        print(f"Configuration error: {exc}")
        print("Create a .env file with TYPESAFE_API_KEY=your_key_here, then run again.")
        raise SystemExit(2) from exc
    except JevRequestError as exc:
        print(f"Jev request failed: {exc}")
        raise SystemExit(1) from exc

    print("Ticket Analysis")
    print(f"Category: {decision.category.value}")
    print(f"Urgent: {'YES' if decision.is_urgent else 'NO'}")
    print(f"Urgency probability: {decision.urgent_probability:.4f}")
    print(f"Severity: {decision.severity_display} / 5")

    if decision.confidence is not None:
        print(f"Category confidence: {decision.confidence:.4f}")

    if decision.severity_confidence is not None:
        print(f"Severity confidence: {decision.severity_confidence:.4f}")

    if decision.probabilities:
        print()
        print("Probabilities:")
        for category, probability in decision.probabilities.items():
            print(f"{category.value:<10} {probability:.4f}")

    if decision.severity_probabilities:
        print()
        print("Severity probabilities:")
        for level, probability in decision.severity_probabilities.items():
            print(f"{level:<10} {probability:.4f}")

    route = route_ticket(decision)

    print()
    print("Routing Decision")
    print(f"Team: {route.team}")
    print(f"Queue: {route.queue_name}")
    print(f"Escalate: {'YES' if route.escalate else 'NO'}")
    if route.escalation_reason:
        print(f"Escalation reason: {route.escalation_reason}")
    print(route.message)

    print()
    print(f"Model: {decision.model}")
    if decision.usage_input_tokens is not None:
        print(f"Input tokens: {decision.usage_input_tokens}")
    if decision.usage_output_tokens is not None:
        print(f"Output tokens: {decision.usage_output_tokens}")


if __name__ == "__main__":
    main()
