from app.console_ui import (
    COLOR_CYAN,
    COLOR_GRAY,
    COLOR_GREEN,
    COLOR_RESET,
    COLOR_WHITE,
    COLOR_YELLOW,
    write_colored_line,
    write_section_title,
)
from app.models import ClarificationRequest, HandbookPolicy, Intent, SupportRequestResult


def render(result: SupportRequestResult) -> None:
    write_section_title("Classification", COLOR_CYAN)
    _write_field("Intent", result.intent.value)
    _write_field("Sentiment", result.sentiment.value)
    _write_field("Urgency", result.urgency.value)

    write_section_title("Reasoning", COLOR_CYAN)
    for step in result.reasoning:
        write_colored_line(f"  - {step}", COLOR_GRAY)

    write_section_title("Action", COLOR_CYAN)
    _write_field("Taken", result.action_taken.value)
    if result.recommended_next_action and result.recommended_next_action.strip():
        _write_field("Next", result.recommended_next_action)

    write_section_title("Customer-Facing Response", COLOR_GREEN)
    write_colored_line(result.customer_facing_response, COLOR_YELLOW)

    if result.cited_policies:
        write_section_title("Policy Citations", COLOR_CYAN)
        for policy in result.cited_policies:
            write_colored_line(
                f"  - {policy.title} ({policy.section}, score={policy.relevance_score:.2f})",
                COLOR_GRAY,
            )


def _write_field(label: str, value: str) -> None:
    print(f"{COLOR_WHITE}  {label:<10}{COLOR_RESET} {value}")


def render_clarification_prompt(clarification: ClarificationRequest, rationale: str) -> str:
    lines = [rationale, "Please share:"]
    for index, question in enumerate(clarification.questions, start=1):
        lines.append(f"{index}. {question}")
    return "\n".join(lines)


def inject_policy_citations(message: str, policies: list[HandbookPolicy]) -> str:
    if not policies:
        return message
    citations = "; ".join(policy.title for policy in policies)
    return f"{message}\n\nPolicy reference: {citations}."


def compose_billing_explanation(message: str, entities: dict[str, str]) -> str:
    lower = message.lower()
    if "charged again" in lower or "renewal" in lower:
        return "This usually aligns with subscription renewal timing, so the latest charge appears to be a normal recurring renewal."
    if "twice" in lower or "duplicate" in lower:
        return "This may be a duplicate or pending-authorization display issue; I will verify against billing rules before finalizing."
    amount = entities.get("amount")
    if amount:
        return f"I reviewed the available billing context for ${amount} and this appears to match a normal subscription or feature-related charge."
    return "I reviewed your billing question and matched it to our known charge patterns for subscriptions and plan features."


def render_empathetic_escalation(prefix: str, next_step: str) -> str:
    return f"{prefix} {next_step}"


def compose_conversation_summary(
    message: str, intent: Intent, entities: dict[str, str]
) -> str:
    summary = f"I understand your request is about {intent.value.lower()}."
    if entities:
        summary += f" I captured: {', '.join(sorted(entities.keys()))}."
    return summary


def compose_response_envelope(summary: str, action: str, next_step: str) -> str:
    return f"{summary}\n\nAction: {action}\n\nNext step: {next_step}"
