import asyncio
import os
import sys
from pathlib import Path

# Make sure `app.*` imports resolve from the Python skeleton directory
_AGENT_DIR = Path(__file__).resolve().parent / "support-agent-python"
sys.path.insert(0, str(_AGENT_DIR))
os.chdir(_AGENT_DIR)

from app.processor import SupportRequestProcessor  # noqa: E402
from app import renderer  # noqa: E402

# ── All 8 sample requests, matching sample_requests.md ──────────────────────
CASES = [
    (
        "1", "First-month refund — enough info",
        """\
From: alice@example.com
Subject: Refund for new Premium plan

Hi,
I signed up for Premium on March 30 and I'm writing on April 10. I tried it for
a few days, but it is not really what I need and I have barely used the account.
Could you refund the $49.99 charge?

Thanks,
Alice""",
    ),
    (
        "2", "Ambiguous — refund / cancel / question",
        """\
From: jordan.p@example.com
Subject: what is going on with my account

hi. so i got an email saying my card was declined?? but i never asked to cancel
anything and i don't even remember signing up for premium. can someone just tell
me what is happening here. if i'm being charged for something i don't use i want
my money back obviously but also i don't really know what i'm paying for anymore.

jordan""",
    ),
    (
        "3", "Missing info — refund-ish but no specifics",
        """\
From: sam.r@example.com
Subject: charged twice?

hey i think you guys charged me twice this month, can you check and refund the
extra one please. thanks""",
    ),
    (
        "4", "Cancellation policy question",
        """\
From: meera.k@example.com
Subject: What happens if I cancel?

Hi support team,
I'm thinking about canceling my Basic plan because I'm not using it as much as I
expected. If I cancel now, do I keep access until the end of the month, and how
long do you keep my data?

Best,
Meera""",
    ),
    (
        "5", "Simple plan question",
        """\
From: dev.tan@example.com
Subject: API access on Basic?

Hello,
Quick question — does the Basic plan include API access, or is that Premium only?
I'm trying to decide which plan to start with.

Thanks!
Devon""",
    ),
    (
        "6", "Angry, repeated issue — escalation",
        """\
From: rachel.b@example.com
Subject: THIS IS THE THIRD TIME

This is the THIRD time I'm writing about the same billing issue and nobody has
fixed it. I was charged $149 for something I never agreed to and every time I
contact support I get a generic reply that doesn't help. I want this resolved
today or I'm disputing it with my bank and leaving a review everywhere I can.

Rachel""",
    ),
    (
        "7", "Explicit escalation — manager request",
        """\
From: tomas.l@example.com
Subject: Need to speak with a manager

Hi,
I've been going back and forth with support for a week about a refund and I'd
like to escalate this to a manager please. I don't want to re-explain the whole
story to another agent — can someone with authority just look at my case and
get back to me.

Thomas""",
    ),
    (
        "8", "Venting — no clear ask",
        """\
From: priya.s@example.com
Subject: disappointed

honestly just really disappointed with how things have been going. the product
used to be great and lately it just feels like nothing works the way it used to.
not sure what you guys want me to do at this point.""",
    ),
]

SEP = "=" * 70


async def run_all() -> None:
    processor = SupportRequestProcessor()

    # Accept optional case filter: python lab2_demo_run.py 3 6 7
    wanted = set(sys.argv[1:]) if len(sys.argv) > 1 else None

    for number, title, message in CASES:
        if wanted and number not in wanted:
            continue

        print(f"\n{SEP}")
        print(f"  CASE {number}: {title}")
        print(SEP)

        result = await processor.process(message)
        renderer.render(result)

    print(f"\n{SEP}")
    print("  All selected cases processed.")
    print(SEP)


if __name__ == "__main__":
    asyncio.run(run_all())
