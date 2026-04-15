import asyncio
import os
import pathlib
import sys

from dotenv import load_dotenv

from app import renderer
from app.console_ui import (
    COLOR_CYAN,
    COLOR_DARK_YELLOW,
    COLOR_GRAY,
    write_colored_line,
    write_section_title,
    merge_clarification_context,
)
from app.models import ResponseType
from app.processor import SupportRequestProcessor

load_dotenv(pathlib.Path(__file__).with_name(".env"))


async def main() -> int:
    _validate_azure_openai_environment()

    try:
        processor = SupportRequestProcessor()
    except RuntimeError as ex:
        print(ex)
        return 1

    write_section_title("Customer Support — Request Processor", COLOR_CYAN)
    write_colored_line(
        "Paste a customer message, then end it with a line containing only '---'.",
        COLOR_GRAY,
    )
    write_colored_line("Type 'quit' on its own line to exit.", COLOR_GRAY)

    while True:
        write_section_title("Paste customer message (end with '---')", COLOR_CYAN)

        message = read_multiline_input()
        if message is None:
            break

        if not message.strip():
            continue

        result = await processor.process(message)
        renderer.render(result)

        if result.response_type == ResponseType.ClarificationNeeded and result.clarification_request:
            write_section_title("Provide Clarification (single follow-up)", COLOR_CYAN)
            follow_up = input().strip()
            if follow_up:
                merged_message, context = merge_clarification_context(
                    message,
                    result.clarification_request.required_fields,
                    follow_up,
                )
                follow_up_result = await processor.process(
                    merged_message,
                    clarification_context=context,
                )
                renderer.render(follow_up_result)

        write_colored_line(
            "\nConversation cycle complete. Enter a new request or 'quit'.",
            COLOR_DARK_YELLOW,
        )

    return 0


def read_multiline_input() -> str | None:
    lines: list[str] = []
    while True:
        try:
            line = input()
        except (EOFError, KeyboardInterrupt):
            print()
            return None

        trimmed = line.strip()

        if not lines and trimmed.lower() == "quit":
            return None

        if trimmed == "---":
            break

        lines.append(line)

    return "\n".join(lines).strip()


def _validate_azure_openai_environment() -> None:
    required = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_DEPLOYMENT_NAME",
    ]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        write_colored_line(
            "Azure OpenAI variables missing: " + ", ".join(missing) + ". Running with heuristic fallback.",
            COLOR_DARK_YELLOW,
        )


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
