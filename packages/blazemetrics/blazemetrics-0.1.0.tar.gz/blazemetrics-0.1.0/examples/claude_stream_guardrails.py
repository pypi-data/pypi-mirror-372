import os
import sys
from typing import Iterator
from blazemetrics import Guardrails, enforce_stream_sync

# Requires: pip install anthropic
import anthropic

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
if not API_KEY:
    print("Set ANTHROPIC_API_KEY to run this example", file=sys.stderr)
    sys.exit(0)

client = anthropic.Anthropic(api_key=API_KEY)

prompt = "Write a short paragraph that includes a phone number and SSN in a story."

rails = Guardrails(
    blocklist=["bomb", "terror"],
    regexes=[r"\b\d{3}-\d{2}-\d{4}\b"],
    case_insensitive=True,
    redact_pii=True,
    safety=True,
)

def token_iter() -> Iterator[str]:
    with client.messages.stream(
        model="claude-3-haiku-20240307",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=256,
        temperature=0.0,
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta" and event.delta.get("text"):
                yield event.delta["text"]

for out in enforce_stream_sync(token_iter(), rails, every_n_tokens=25, replacement="[BLOCKED]", safety_threshold=0.6):
    print(out, end="", flush=True)
print() 