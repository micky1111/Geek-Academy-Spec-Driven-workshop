import asyncio

from app.processor import SupportRequestProcessor


async def main() -> None:
    message = """From: alice@example.com
Subject: Refund for new Premium plan

Hi,
Could you refund order #A-1001 for the $49.99 charge from March 30?"""

    processor = SupportRequestProcessor()
    result = await processor.process(message)

    print("ACTION:", result.action_taken.value)
    print("TYPE:", result.response_type.value)
    print("NEXT:", result.recommended_next_action)
    print("REASONING:")
    for step in result.reasoning:
        print("-", step)

    print("\nRESPONSE:\n" + result.customer_facing_response)


if __name__ == "__main__":
    asyncio.run(main())
