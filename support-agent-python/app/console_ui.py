COLOR_RESET = "\033[0m"
COLOR_CYAN = "\033[96m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_GRAY = "\033[90m"
COLOR_WHITE = "\033[97m"
COLOR_DARK_YELLOW = "\033[33m"


def write_section_title(title: str, color: str = COLOR_CYAN) -> None:
    print(f"{color}\n=== {title} ==={COLOR_RESET}")


def write_colored_line(text: str, color: str) -> None:
    print(f"{color}{text}{COLOR_RESET}")


def merge_clarification_context(
    original_message: str,
    clarification_fields: list[str],
    clarification_response: str,
) -> tuple[str, dict[str, object]]:
    merged_message = f"{original_message}\n\nClarification provided: {clarification_response}".strip()
    context = {
        "clarification_round_used": True,
        "required_fields": clarification_fields,
        "clarification_response": clarification_response,
    }
    return merged_message, context
